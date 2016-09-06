CC=g++
CFLAGS=-std=c++11 -O3

all: columnar compare

columnar:
	$(CC) columnar.cc $(CFLAGS) -lz -lbz2 -o columnar

compare:
	$(CC) fastqcmp.cc $(CFLAGS) -o fastqcmp
	$(CC) samcmp.cc $(CFLAGS) -o samcmp
