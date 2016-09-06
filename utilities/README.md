# Utilities

To build utilities, just run

    make

Make assumes that zlib and bzlib2 are installed. 

### columnar

This tool prints per-column compression ratio of Gzip and bzip2 for FASTQ and BAM/SAM files.

Usage: `columnar <file.fq or file.sam>`

#### Sample output:

First column describes the size of raw ASCII column. Second column describes the size of Gzip-compressed column, while third describes the bzip2-compressed size.

##### SAM:

    $ columnar test_sam.sam
    SAM file test_sam.sam
    test_sam.sam
    LINES:                 9996
     HEAD:                  185                  171                  204
    QNAME:               177289                50206                44664
     FLAG:                24970                 4479                 3652
      REF:               129948                  295                   89
      POS:                36613                 6351                 7906
     MAPQ:                29962                  263                  209
    CIGAR:                40041                  175                  140
    RNEXT:                 9996                  352                  343
    PNEXT:                36337                16570                15224
     TLEN:                34338                14547                12633
      SEQ:              1499400                41113                53511
     QUAL:              1499400               685964               608293
       OF:               660584                81314                52321

    SIZE: 4299019

##### FASTQ:

    $ columnar test_fq.fq
    FASTQ file test_fq.fq
    test_fq.fq
    RECORDS:                 9996
    RNAME:               187285                50563                44677
      SEQ:              1499400                41113                53511
      AUX:                 9996                   35                   45
     QUAL:              1499400               685964               608293

    SIZE: 3236065

## Comparison utilities

We provided two convenience tools for comparing the SAM and FASTQ files.

Both tools first invoke UNIX's `cmp` utility to check whether the two files are byte-identical. If `cmp` returns negative answer,
they will load `<maxline>` lines from each file and compare them line by line. 

**Important:** Both files should be sorted with same criteria (e.g. both should be sorted by read name)

**Warning:** These tools are NOT as accurate as diff or similar tools, but they are much faster on large files. As long as
two files are not significantly different, they will accurately report the differences between them. They are quite handy
in finding out the differences between the output of compression tool and original files.

### samcmp

This tool compares the contents of two SAM files. 

Usage: `samcmp <original.sam> <copy.sam> <maxline>`, where `<maxline>` is the number of lines `samcmp` will load in each iteration.
If you have a machine with large amount of spare RAM, you can use high values of `<maxline>` for speed-up.

#### Output

If UNIX `cmp` succeeds, output will be:

    $ ./samcmp a.sam b.sam 10000                          
    Reading a.sam, b.sam; maxline=10000
    Equal cmp
    Done a.sam

If it doesn't, output will be similar to the following example:

    $ ./samcmp a.sam b.sam 10000                          

    Reading a.sam, b.sam; maxline=10000
    a.sam b.sam differ: byte 1, line 1
    Read 1000 (1000) / 900 (900) lines, 1000
    > ORIG          1000 (a.sam)
    < COPY           900 (b.sam)
    Comments   not equal
    Miss             100 lines

    SEQ                1 lines unequal
    BI                 0 missing,          0 extra,          1 unequal
    AM                 1 missing,          0 extra,          0 unequal
    Done a.sam
    
This output tell us that:

 - File `a.sam` has 1000 records, while file `b.sam` has 900 records 
 - Both files have different SAM comments
 - File `b.sam` misses 100 lines (in case `b.sam` has more records than `a.sam`, message would show `Extra xx lines`)
 - Sequences (SEQ) do not match in one record
 - BI tags do not match in 1 record
 - One AM tag is missing from `b.sam`
 
### fastqcmp

This tool compares the contents of two FASTQ files. 

Usage: `fastqcmp <original.sam> <copy.sam> <maxline> <fields>`, where `<maxline>` is the number of lines `fastqcmp` will load in each iteration.
`<fields>` is an optional parameter denoting which fields will be compared against each other.

Default `<fields>` value is `1111`, meaning that read names, sequences, comments and quality scores (in this order)
will be used during the comparison.
If you wish to ignore quality scores, you should unset 4th byte of bitmask (e.g. pass 1110 as `<fields>`).

#### Output

If UNIX `cmp` fails, output will be similar to the following example:

    $ ./fastqcmp a.fq b.fq 10000                          

    Reading a.fq, b.fq; maxline=100000
    a.fq b.fq differ: byte 63, line 2
    Read 25 (25) / 25 (25) lines, 25
    > ORIG            25 (a.fq)
    < COPY            25 (b.fq)

    SEQ                2 lines unequal
                         2 mismatches: 1 lines
    COMMENT            1 lines unequal
    QUAL               1 lines unequal
                         2 mismatches: 1 lines

    Nucleotide A missed: 1
    Nucleotide C missed: 1
    Wrong N quality: 2 of 2
    Done a.fq  

This output tell us that:

 - Files `a.fq` and `b.fq` have 25 records
 - Two records share non-equal sequences with 2 mismatches (number of mismatches is calculated as a Hamming distance of two sequences)
 - One record has different comments in two files
 - One record has different quality scores in two files
 - 2 quality score mismatches were due to the N quality score.
 
 Many tools assume that quality scores for N nucleotides will be the lowest possible quality scores available. 
 This is not always the case, and we detect those tools by counting the number of wrong N quality scores and making sure
 that number of wrong quality scores is the same as number of wrong N quality scores
 
