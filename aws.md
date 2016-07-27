# Benchmarking (Virtualization or Amazon Web Services)

### Instance creation

For testing purposes, we recommend using either [Vagrant](https://www.vagrantup.com) with [VirtualBox](https://www.virtualbox.org) image, or firing up Ubuntu EC2 t2.micro instance on [Amazon Web Services E2](https://aws.amazon.com/ec2/) (AWS). On the other hand, it is recommended to use dedicated instance with high I/O performance and lots of available RAM and disk space for real, camera-ready benchmarking.

> For now, some tools are having problems running on t2.micro node on AWS (e.g. SCALCE, Fastqz, DeeZ etc.). We are looking into this issue.

### Initial set-up

First launch your Ubuntu instance, either via AWS control panel, or by invoking:

```
mkdir benchmarking
cd benchmarking
vagrant init ubuntu/trusty64
vagrant up
vagrant ssh
```

Now, set up necessary dependencies as follows (assuming you are using Ubuntu 14.04):

```
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install make git gcc g++ gcc-5 g++-5 libtbb2 libz-dev libbz2-dev libcurl4-openssl-dev default-jre
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 60 --slave /usr/bin/g++ g++ /usr/bin/g++-5
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
export PATH=${PATH}:../tools
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
