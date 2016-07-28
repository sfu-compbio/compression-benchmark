# Benchmarking Quickstart

### Instance creation

For testing purposes, we recommend using either [Vagrant](https://www.vagrantup.com) with [VirtualBox](https://www.virtualbox.org) image, or firing up Ubuntu EC2 t2.micro instance on [Amazon Web Services E2](https://aws.amazon.com/ec2/) (AWS). On the other hand, it is recommended to use dedicated instance with high I/O performance and lots of available RAM and disk space for real, camera-ready benchmarking.

### Initial set-up

First launch your Ubuntu instance, either via AWS control panel, or by invoking:

```
mkdir benchmarking
cd benchmarking
vagrant init ubuntu/trusty64
vagrant up
vagrant ssh
```

We suggest editing your `Vagrantfile` and adding 4 GB of memory to the virtual machine.

Now, set up necessary dependencies as follows (assuming you are using Ubuntu 14.04):

```
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-add-repository ppa:brightbox/ruby-ng
sudo apt-get update
sudo apt-get install make git gcc g++ gcc-5 g++-5 libtbb2 libz-dev \
  libbz2-dev libcurl4-openssl-dev default-jre lzip plzip ruby2.2 \
  ruby-switch libc6-dev-i386 g++-multilib gdb
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 60 \
  --slave /usr/bin/g++ g++ /usr/bin/g++-5
sudo ruby-switch --set ruby2.2
```

Afterwards, clone our benchmark repositories and set up default tool configuration as follows:

```
git clone https://github.com/sfu-compbio/compression-benchmark
git clone https://github.com/sfu-compbio/compression-benchmark-tools
ln -s `pwd`/compression-benchmark-tools/tools `pwd`/compression-benchmark/tools
cp compression-benchmark-tools/tools.py compression-benchmark/tools.py
```

### Benchmarking

Before you start, it is recommended to add a `tools` directory to your `PATH`:

```
export PATH=${PATH}:`pwd`/compression-benchmark-tools/tools
```

First, prepare the reference file in FASTQ format for various tools:

```
# In this example, reference is called "test.fa"
cd compression-benchmark/sample
../ref.py test.fa
```

You should end up with the following files:

```
$ ls -l
test.fa  test.fa.cbc  test.fa.fai

test.fa.sc:
EcoliDH10B.fa.fa
```

Now you can fire up benchmark suite by running:

```
# Enter
cd .. # or cd compression-benchmark if you are in your root directory
# Evaluate sample SAM file "test_sam.sam"
python benchmark.py -i sample/test_sam.sam -r sample/test.fa
# Evaluate sample FASTQ file "test_sam.sam"
python benchmark.py -i sample/test_fq.fq -r sample/test.fa
```

The results will be placed in `test_sam` and `test_fq` directories for `test_sam.sam` and `test_fq.fq` respectively.
Within those directories, you will find:

- `benchmark.log_<date>`: detailed log about each run
- `log/`: output of executed commands for each tool
- `output/`: compressed and decompressed files produced by evaluated tools

## Known issues and caveats

By default, test script will run all tools in single-threaded mode. Additionaly, many tools require *quite a lot of memory*, if run with default settings. This might cause them to stop working on low-memory instances (e.g. default Vagrant configuration or AWS t2.micro instance). Known tools which might stop working are sam_comp, Fqzcomp, SCALCE, DeeZ, Mince etc.

Many tools also use hard-coded paths to some executables. Some are also not able to compress or decompress any file lying outside the executable directory, or having "wrong" extension. In addition, some tools consist of multiple stages. We have tried to fix those shortcomings, and binaries provided here incorporate those fixes. In order to make such tools compatible with our benchmarking system, we have added multiple Bash scripts for problematic tools. For example, Orcom or LW-FQZip are invoked via `orcom.sh` and `lwfqzip.sh` recpectively.

Few caveats we have observed so far:

- CBC fails on decompression
- LFQC might require recompilation of `zpaq` and `lpaq` binaries. In addition to that, `lpaq` cannot compress files larger than 2 GB.
- SCALCE by default allocates 4 GB buckets. For low-memory systems (e.g. AWS t2.micro instance), we tuned the bucket allocation size to 1 GB with `-B 1G` parameter. Note that this will affect its compression performance; run SCALCE without this parameter in real-world benchmarking.
- DeeZ uses SSE 4.1 for faster execution. The version provided here is compiled with SSE 4.1 support; it might not work on systems without SSE 4.1 support. Also, the version used for benchmarking is bit behind the current GitHub release, and is not intended to be used in production environments.
- KIC and k-Path do not support single-threaded mode. You need to add at least `-t 2` to `benchmark.py` to be able to run those tools.
