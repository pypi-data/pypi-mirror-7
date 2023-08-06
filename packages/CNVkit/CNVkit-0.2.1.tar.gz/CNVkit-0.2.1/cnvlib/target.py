"""Transform bait intervals into targets more suitable for CNVkit."""
from __future__ import division, absolute_import
import collections
from itertools import groupby

from . import ngfrills


# _____________________________________________________________________________
# Assign refFlat gene names to target intervals
# ftp://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/

def add_refflat_names(region_rows, refflat_fname):
    """Apply RefSeq gene names to a list of targeted regions."""
    return cover_introns(assign_names(region_rows, refflat_fname))


def cover_introns(regions):
    """Apply the name of the surrounding gene to intronic targets.

    If an unnamed target is surrounded by targets that have the same name,
    consider it an intron and apply that gene name to the unnamed target.
    Otherwise, leave it unnamed ("-").
    """
    last_gene = None
    last_chrom = None
    queue = []
    for chrom, start, end, name in regions:
        if chrom != last_chrom:
            # Queue was not intronic (3'-terminal of last chrom)
            for row in queue:
                yield row
            queue = []
            last_chrom = chrom
            last_gene = name if name != '-' else None
        # Track genes; smooth over intronic '-' regions
        if name == '-':
            # Not sure if intronic -- enqueue
            queue.append((chrom, start, end, name))
        else:
            if name == last_gene:
                # Queued row(s) were intronic
                if queue:
                    for cm, st, ed, _nm in queue:
                        yield cm, st, ed, name
                    queue = []
            else:
                # Queued row(s) were intergenic
                for row in queue:
                    yield row
                queue = []
                last_gene = name
            yield chrom, start, end, name
    # Remainder
    for row in queue:
        yield row


def assign_names(region_rows, refflat_fname, default_name='-'):
    """Replace the interval gene names with those at the same loc in refFlat.txt
    """
    ref_genes = read_refflat_genes(refflat_fname)
    region_rows = sorted(region_rows,
                         key=lambda row: (row[0], row[3], row[1], row[2]))
    for (chrom, strand), chr_rows in groupby(region_rows,
                                             lambda row: (row[0], row[3])):
        if (chrom, strand) not in ref_genes:
            ngfrills.echo("Chromosome", chrom, "strand", strand,
                          "not in annotations")
            continue
        genes_in_chrom = iter(ref_genes[(chrom, strand)])
        ex_start, ex_end, ex_name = next(genes_in_chrom)
        for row in chr_rows:
            start, end = row[1:3]
            if ex_end < start:
                # Burn through genes until hitting or passing the interval
                while ex_end < start:
                    try:
                        ex_start, ex_end, ex_name = next(genes_in_chrom)
                    except StopIteration:
                        # Interval is past the last annotated gene in chromosome
                        ngfrills.echo("Interval %s:%d-%d unannotated in refFlat"
                                      % (chrom, start, end))
                        # Fake it...
                        ex_start, ex_end = end + 1, end + 2
                        ex_name = default_name

            if ex_start > end:
                # Interval is an unannotated intergenic region (we skipped it)
                yield (chrom, start, end, default_name)
            else:
                assert ex_end > start or ex_start < end
                # Overlap: Use this gene's name and emit the interval
                yield (chrom, start, end, ex_name)


def read_refflat_genes(fname):
    """Parse genes; merge those with same name and overlapping regions.

    Returns a dict of: {chrom: [(gene start, gene end, gene name), ...]}
    """
    genedict = collections.defaultdict(list)
    with open(fname) as genefile:
        for line in genefile:
            name, _rx, chrom, strand, start, end, _ex = parse_refflat_line(line)
            # Skip antisense RNA annotations
            if name.endswith('-AS1'):
                continue
            genedict[name].append((chrom, strand, start, end))

    chromdict = collections.defaultdict(list)
    for name, locs in genedict.iteritems():
        locs = list(set(locs))
        if len(locs) == 1:
            chrom, strand, start, end = locs[0]
            chromdict[(chrom, strand)].append((start, end, name))
        else:
            # Check locs for overlap; merge if so
            locs.sort()
            chroms, strands, starts, ends = zip(*locs)
            starts = map(int, starts)
            ends = map(int, ends)
            curr_chrom, curr_strand, curr_start, curr_end = (
                chroms[0], strands[0], starts[0], ends[0])
            for chrom, strand, start, end in zip(chroms[1:], strands[1:],
                                                 starts[1:], ends[1:]):
                if (chrom != curr_chrom or
                    strand != curr_strand or
                    start > curr_end + 1 or
                    end < curr_start - 1):
                    chromdict[(curr_chrom, curr_strand)].append(
                        (curr_start, curr_end, name))
                    curr_chrom, curr_start, curr_end = chrom, start, end
                else:
                    curr_start = min(start, curr_start)
                    curr_end = max(end, curr_end)
            # Emit the final interval in this group
            chromdict[(curr_chrom, curr_strand)].append(
                (curr_start, curr_end, name))

    # Finally, sort the keys, and return the results
    for key in list(chromdict.keys()):
        chromdict[key].sort()
    return chromdict


def parse_refflat_line(line):
    """Parse one line of refFlat.txt; return relevant info.

    Pair up the exon start and end positions. Add strand direction to each
    chromosome as a "+"/"-" suffix (it will be stripped off later).
    """
    fields = line.split('\t')
    name, refseq, chrom, strand = fields[:4]
    start, end = fields[4:6]
    # start, end = fields[6:8]
    exon_count, exon_starts, exon_ends = fields[8:11]
    exons = zip(exon_starts.rstrip(',').split(','),
                exon_ends.rstrip(',').split(','))
    assert len(exons) == int(exon_count), (
        "Exon count mismatch at %s: file says %s, but counted %d intervals"
        % (name, exon_count, len(exons)))
    return name, refseq, chrom, strand, int(start), int(end), exons


# _____________________________________________________________________________
# Clean/shorten interval names

def shorten_labels(interval_rows):
    """Reduce multi-accession interval labels to the minimum consistent.

    So: BED or interval_list files have a label for every region. We want this
    to be a short, unique string, like the gene name. But if an interval list is
    instead a series of accessions, including additional accessions for
    sub-regions of the gene, we can extract a single accession that covers the
    maximum number of consecutive regions that share this accession.

    e.g.

    ...
    chr1	879125	879593	+	mRNA|JX093079,ens|ENST00000342066,mRNA|JX093077,ref|SAMD11,mRNA|AF161376,mRNA|JX093104
    chr1	880158	880279	+	ens|ENST00000483767,mRNA|AF161376,ccds|CCDS3.1,ref|NOC2L
    ...

    becomes:

    chr1	879125	879593	+	mRNA|AF161376
    chr1	880158	880279	+	mRNA|AF161376
    """
    longest_name_len = 0
    curr_names = set()
    curr_gene_coords = []

    for row in interval_rows:
        next_coords = row[:-1]
        next_names = set(row[-1].rstrip().split(','))
        assert len(next_names)
        overlap = curr_names.intersection(next_names)
        if overlap:
            # Continuing the same gene; update shared accessions
            curr_names = filter_names(overlap)
            curr_gene_coords.append(next_coords)
        else:
            # End of the old gene -- emit coords + shared name(s)
            for coords in curr_gene_coords:
                out_row = emit(coords, curr_names)
                yield out_row
                longest_name_len = max(longest_name_len, len(out_row[-1]))

            # Start of a new gene
            curr_gene_coords = [next_coords]
            curr_names = next_names
    # Final emission
    for coords in curr_gene_coords:
        out_row = emit(coords, curr_names)
        yield out_row
        longest_name_len = max(longest_name_len, len(out_row[-1]))

    ngfrills.echo("Longest name length:", longest_name_len)


def filter_names(names, exclude=('mRNA',)):
    """Remove less-meaningful accessions from the given set."""
    if len(names) > 1:
        ok_names = set(n for n in names
                       if not any(n.startswith(ex) for ex in exclude))
        if ok_names:
            return ok_names
    # Names are not filter-worthy; leave them as they are for now
    return names


def emit(coords, names):
    """Try filtering names again. Format the row for yielding."""
    try:
        final_name = shortest_name(filter_names(names))
        out_row = list(coords) + [final_name]
    except ValueError:
        raise ValueError(coords)
    return out_row


def shortest_name(names):
    """Return the shortest trimmed name from the given set."""
    name = min(names, key=len)
    if len(name) > 2 and '|' in name[1:-1]:
        # Split 'DB|accession' and extract the accession sans-DB
        name = name.split('|')[-1]
    return name


# _____________________________________________________________________________
# Split targets

# ENH - fix overlapping bins at midpoint of overlap? try to equalize bin size?
#   - or just concatenate the bins & divide evenly?
#       - do this for adjacent bins too?
#       e.g. --balance-adjacent
def split_targets(region_rows, avg_size):
    """Split large tiled intervals into smaller, consecutive targets.

    For each of the tiled regions:

        - Divide into equal-size (tile_size/avg_size) portions
        - Emit the (chrom, start, end) coords of each portion

    Bin the regions according to avg_size.
    """
    prev_end = -1
    prev_chrom = None
    for chrom, start, end, name in region_rows:
        if chrom == prev_chrom and start <= prev_end:
            # DBG
            # ngfrills.echo("Bin overlap, updating start", start, "to", prev_end)
            assert end > prev_end, "end=%d, prev_end=%d" % (end, prev_end)
            start = prev_end
        prev_chrom = chrom
        span = end - start
        if span >= avg_size * 1.5:
            ngfrills.echo("Splitting:", name.ljust(15),
                          str(end - start + 1).rjust(6))
            # Divide the background region into equal-sized bins
            nbins = round(span / avg_size) or 1
            bin_size = span / nbins
            # Locate & emit background bins
            bin_start = start
            while bin_start < (end - 2):
                bin_end = bin_start + bin_size
                yield (chrom, int(bin_start), int(bin_end), name)
                prev_end = int(bin_end)
                bin_start = bin_end
        else:
            yield (chrom, start, end, name)
            prev_end = end

