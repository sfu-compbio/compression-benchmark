# Usage

All Python scripts require at least Python 2.7.

## benchmark.py

This script performs the evaluation of the tools specified in `tools.py` file on a given dataset.

Please check the directory `sample` for sample output.

> Complete `tools.py` documentation will be available sometimes later. The most of the file schema is pretty much self-explanatory. Just make sure that all tools are stored in `tools` directory (i.e. `cmd` parameter is evaluated as `tools/${cmd}`).

#### Parameters:

 - `--input/-i <file>`

    `<file>` denotes input FASTQ or SAM file. File type should be auto-detected.

 - `--ref/-r <reference>`

    Path to reference FASTA file. Some tools require pre-processed reference. Please check `ref.py` for details.

 - `--threads/-t <list>`

    Specify how many different thread configurations you want to evaluate. Default is `1` (evaluate in single-threaded mode). Different threads are separated with comma.

 - `--force/-f`

    If enabled, do not resume the experiment, but repeat it again. This will overwrite the previous logs.

 - `--copy/-c`

    Copy the input files in the current directory. Useful if your data is on NFS drives.
    
    **BUG WARNING**: for paired-end data, you will need to manually copy second paired-end file. We plan to update our script to do this automatically later.

 - `--rt/-R`

    Use `SCHED_FIFO` real-time priority via `chrt`. Requires root permissions.

 - `--clear-cache/-C`

    Clear file system cache before every experiment. Requires root.

 - `--output-dir/-o`

    Move successfully compressed and decompressed files to the another directory. Useful if the main hard disk is not large enough to keep all the files. By default, nothing is moved.

 - `--email/-e <address>`

    Send an e-mail detailing th ebenchmark process when the script is completed.

#### Examples:

 -  `$ ref.py test.fa`

    Prepares the reference file `test.fa`.

    `# benchmark.py -i test_sam.sam -r test.fa -C -e test@localhost -t 1,4`

    Evaluates `test_fq.sam` with reference `test.fa` in single-threaded and 4-threaded mode. Disk cache will be cleared before invocation of each tool (root is required for this to work). After the completion, log will be mailed to `test@localhost`.

 - `$ benchmark.py -i test_fq.sam -r test.fa`

    Evaluates `test_fq.fq` with reference file `test.fa` in single-threaded mode. No e-mail will be sent.


## ref.py

This script will prepare the references for the following tools:

 - Any tool requiring indexed reference (`ref.fai`)
 - sam_comp (`ref.sc`)
 - CBC (`ref.cbc`)

It requires Samtools to be available in `PATH`.

#### Invocation:

    ref.py <reference.fa>


## columnar.cc

This tool prints per-column compression ratio of Gzip and bzip2 for FASTQ and BAM/SAM files.

#### Compilation:

	g++ -std=c++11 -lz -lbz2 -O3 columnar.cc -o columnar


#### Invocation:

    columnar <file.fq or file.sam>

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
