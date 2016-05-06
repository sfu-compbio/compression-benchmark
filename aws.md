# Amazon Web Services Setup

### Instance creation

For testing purposes, we recommend firing up Ubuntu EC2 t2.micro instance. For real benchmarking, it is recommended to use dedicated instance with high I/O performance and lots of available RAM and disk space.

> For now, some tools are having problems running on t2.micro node on AWS (e.g. SCALCE, Fastqz, DeeZ etc.). We are looking into this issue.

### Initial set-up

After creating Ubuntu instance, set up necessary dependencies as follows (assuming Ubuntu 14.04):

```
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install make git gcc g++ gcc-5 g++-5 libtbb2 libz-dev libbz2-dev libcurl4-openssl-dev default-java
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

First, prepare reference file for various tools:

```
cd compression-benchmark/sample
PATH=${PATH}:../tools ../ref.py test.fa
```

Then you can fire up benchmark suite by running:

```
cd compression-benchmark
python benchmark.py -i sample/test_sam.sam -r sample/test.fa
python benchmark.py -i sample/test_fq.fq -r sample/test.fa
```
