# Benchmarking (Virtualization or Amazon Web Services)

### Instance creation

For testing purposes, we recommend using either VirtualBox or VMware image, or firing up Ubuntu EC2 t2.micro instance on AWS. For real benchmarking, it is recommended to use dedicated instance with high I/O performance and lots of available RAM and disk space.

> For now, some tools are having problems running on t2.micro node on AWS (e.g. SCALCE, Fastqz, DeeZ etc.). We are looking into this issue.

### Initial set-up

First launch your Ubuntu instance, and set up necessary dependencies as follows (assuming you are using Ubuntu 14.04):

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

First, prepare the reference file in FASTQ format for various tools:

```
# In this example, reference is called "test.fa"
cd compression-benchmark/sample
PATH=${PATH}:../tools ../ref.py test.fa
```

Now you can fire up benchmark suite by running:

```
# Enter
cd compression-benchmark
# Evaluate sample SAM file "test_sam.sam"
python benchmark.py -i sample/test_sam.sam -r sample/test.fa
# Evaluate sample FASTQ file "test_sam.sam"
python benchmark.py -i sample/test_fq.fq -r sample/test.fa
```
