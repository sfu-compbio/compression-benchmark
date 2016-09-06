#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <fstream>
#include <zlib.h>
#include <bzlib.h>
using namespace std;

#define CHUNK 16384

size_t line = 0;

void zopen(z_stream *strm) 
{
	strm->zalloc = Z_NULL;
	strm->zfree = Z_NULL;
	strm->opaque = Z_NULL;
	deflateInit(strm, Z_DEFAULT_COMPRESSION);
}

size_t zclose(z_stream *strm) 
{
	unsigned char c = ' ';
	strm->avail_in = 1;
	strm->next_in = &c;
	unsigned char out[CHUNK];
	size_t have = 0;
	do {
		strm->avail_out = CHUNK;
		strm->next_out = out;
		int ret = deflate(strm, Z_FINISH);
		assert(ret != Z_STREAM_ERROR);
		have += CHUNK - strm->avail_out;
	} while (strm->avail_out == 0);
	deflateEnd(strm);
	return have;
}

void bopen(bz_stream *strm) 
{
	strm->bzalloc = Z_NULL;
	strm->bzfree = Z_NULL;
	strm->opaque = Z_NULL;
	BZ2_bzCompressInit(strm, 9, 0, 0);
}

size_t bclose(bz_stream *strm) 
{
	char out[CHUNK];
	char c = ' ';
	strm->avail_in = 1;
	strm->next_in = &c;
	size_t have = 0;
	do {
		strm->avail_out = CHUNK;
		strm->next_out = out;
		int ret = BZ2_bzCompress(strm, BZ_FINISH);
		assert(ret == BZ_STREAM_END || ret == BZ_FINISH_OK || ret == BZ_PARAM_ERROR);
		have += CHUNK - strm->avail_out;
	} while (strm->avail_out == 0);
	BZ2_bzCompressEnd(strm);
	return have;
}

size_t bcompress(bz_stream *strm, void *in, size_t insize)
{
	int ret;
	size_t have = 0;
	char out[CHUNK];

	strm->avail_in = insize;
	strm->next_in = (char*)in;
	do {
		strm->avail_out = CHUNK;
		strm->next_out = out;
		ret = BZ2_bzCompress(strm, BZ_RUN);
		assert(ret == BZ_RUN_OK || ret == BZ_STREAM_END || ret == BZ_PARAM_ERROR);
		have += CHUNK - strm->avail_out;
	} while (strm->avail_out == 0);
	return have;
}

size_t zcompress(z_stream *strm, void *in, size_t insize)
{
	int ret;
	size_t have = 0;
	unsigned char out[CHUNK];

	strm->avail_in = insize;
	strm->next_in = (unsigned char*)in;
	do {
		strm->avail_out = CHUNK;
		strm->next_out = out;
		ret = deflate(strm, Z_NO_FLUSH);
		assert(ret != Z_STREAM_ERROR);
		have += CHUNK - strm->avail_out;
	} while (strm->avail_out == 0);
	return have;
}

void parse_bam (const char *path)
{
	fprintf(stderr, "BAM file %s\n", path);
	char *data = (char*)malloc(10 * 1024 * 1024);
	
	const int F = 16;
	z_stream zf[F];
	bz_stream bf[F];
	for (int i = 0; i < F; i++) {
		zopen(zf + i);
		bopen(bf + i);
	}

	vector<long long> zfields(F, 0), bfields(F, 0);
	auto xwrite = [&](int f, void *c, size_t sz) {
		zfields[f] += zcompress(zf + f, c, sz);
		bfields[f] += bcompress(bf + f, c, sz);
		return sz;
	};

	gzFile fi = gzopen(path, "rb");
	gzread(fi, data, 4);

	int32_t l_text;
	gzread(fi, &l_text, sizeof(int32_t));
	gzread(fi, data, l_text);

	int32_t n_ref;
	gzread(fi, &n_ref, sizeof(int32_t));
	xwrite(0, &n_ref, sizeof(int32_t));
	while (n_ref--) {
		int32_t l_name, l_ref;
		gzread(fi, &l_name, sizeof(int32_t));
		gzread(fi, data, l_name);
		gzread(fi, &l_ref, sizeof(int32_t));
		xwrite(0, &l_name, sizeof(int32_t));
		xwrite(0, data, l_name);
		xwrite(0, &l_ref, sizeof(int32_t));
	}

	int32_t block_size;
	while (gzread(fi, &block_size, sizeof(int32_t)) == sizeof(int32_t)) {
		gzread(fi, data, block_size);

		int i = 0, p = 0;

		p += xwrite(i++, data + p, sizeof(int32_t));
		p += xwrite(i++, data + p, sizeof(int32_t));

		uint16_t bin = ((*(uint32_t*)(data + p)) >> 16) & 0xffff;
		uint8_t MAPQ = ((*(uint32_t*)(data + p)) >> 8) & 0xff;
		uint8_t l_read_name = (*(uint32_t*)(data + p)) & 0xff;
		xwrite(i++, &bin, sizeof(uint16_t));
		p += sizeof(uint32_t);

		xwrite(13, &MAPQ, sizeof(uint8_t));
		xwrite(14, &l_read_name, sizeof(uint8_t));

		uint16_t FLAG = ((*(uint32_t*)(data + p)) >> 16) & 0xffff;
		uint16_t n_cigar_op = (*(uint32_t*)(data + p)) & 0xffff;
		xwrite(i++, &FLAG, sizeof(uint16_t));
		p += sizeof(uint32_t);

		xwrite(15, &n_cigar_op, sizeof(uint16_t));

		int32_t l_seq = *(int32_t*)(data + p); 
		p += xwrite(i++, data + p, sizeof(int32_t));

		p += xwrite(i++, data + p, sizeof(int32_t));
		p += xwrite(i++, data + p, sizeof(int32_t));
		p += xwrite(i++, data + p, sizeof(int32_t));
		p += xwrite(i++, data + p, sizeof(char) * l_read_name);
		p += xwrite(i++, data + p, sizeof(uint32_t) * n_cigar_op);
		p += xwrite(i++, data + p, sizeof(uint8_t) * (l_seq + 1) / 2);
		p += xwrite(i++, data + p, sizeof(char) * l_seq);
		p += xwrite(i++, data + p, block_size - p);

		line++;
	}

	for (int i = 0; i < F; i++) {
		bfields[i] += bclose(bf + i);
		zfields[i] += zclose(zf + i);
	}

	vector<string> N { 
		"REF", "POS", "BIN", // 0
		"FLAG", "SEQLEN", "PREF", // 3
		"PNEXT", "TLEN", "QNAME",  // 6
		"CIGAR", "SEQ", "QUAL",  // 9
		"OF", "MAPQ", "RNAMELEN",  // 12
		"CIGARLEN"  // 15
	};
	printf("%s\n", path);
	for (int i = 0; i < F; i++) 
		printf("%20s: %20lld %20lld\n", N[i].c_str(), zfields[i], bfields[i]);
	free(data);
}

void parse_sam (const char *path)
{
	fprintf(stderr, "SAM file %s\n", path);
	const int F = 13;
	z_stream zf[F];
	bz_stream bf[F];
	for (int i = 0; i < F; i++) {
		zopen(zf + i);
		bopen(bf + i);
	}

	vector<long long> fields(F, 0);
	vector<long long> zfields(F, 0), bfields(F, 0);
	
	long long cnt = 0, nl = 0;
	string s;
	ifstream fin(path);
	while (getline(fin, s)) {
		if (s[0] == '@') { 
			cnt += s.size(); 
			bfields[F-1] += bcompress(bf + F-1, (void*)(s.c_str()), s.size());
			zfields[F-1] += zcompress(zf + F-1, (void*)(s.c_str()), s.size());
			continue; 
		}
		nl++;
		line++;
		for (int i = 0, j = 0, pi = 0; i < s.size(); i++) {
			if (s[i] == '\t') {
				bfields[j] += bcompress(bf + j, (void*)(s.c_str() + pi), i - pi);
				zfields[j] += zcompress(zf + j, (void*)(s.c_str() + pi), i - pi);
				fields[j] += i - pi;
				pi = i + 1;
				j++;
				if (j == 11) {
					fields[j] += s.size() - i - 1;
					bfields[j] += bcompress(bf + j, (void*)(s.c_str() + pi), s.size() - i - 1);
					zfields[j] += zcompress(zf + j, (void*)(s.c_str() + pi), s.size() - i - 1);
					break;
				}
			}
		}
	}
	fin.close();

	vector<string> NF { "QNAME", "FLAG", "REF", "POS", "MAPQ", "CIGAR", "RNEXT", "PNEXT", "TLEN", "SEQ", "QUAL", "OF"};
	printf("%s\n", path);
	printf("%5s: %20lld\n", "LINES", nl);

	for (int i = 0; i < F; i++) {
		bfields[i] += bclose(bf + i);
		zfields[i] += zclose(zf + i);
	}
	printf("%5s: %20lld %20lld %20lld\n", "HEAD", cnt, zfields[F-1], bfields[F-1]);
	for (int i = 0; i < F-1; i++) {
		printf("%5s: %20lld %20lld %20lld\n", NF[i].c_str(), fields[i], zfields[i], bfields[i]);
	}
}

void parse_fastq (const char *path)
{
	fprintf(stderr, "FASTQ file %s\n", path);
	const int F = 4;
	z_stream zf[F];
	bz_stream bf[F];
	for (int i = 0; i < F; i++) {
		zopen(zf + i);
		bopen(bf + i);
	}

	vector<long long> fields(F, 0);
	vector<long long> zfields(F, 0), bfields(F, 0);
	
	long long nl = 0;
	string s;
	ifstream fin(path);
	while (getline(fin, s)) {
		int i = 0;
		do {
			bfields[i] += bcompress(bf + i, (void*)(s.c_str()), s.size());
			zfields[i] += zcompress(zf + i, (void*)(s.c_str()), s.size());
			fields[i] += s.size();
			i++;
			if (i != 4) getline(fin, s);
		} while (i != 4);
		nl++;
		line++;
 	}
	fin.close();

	vector<string> NF { "RNAME", "SEQ", "AUX", "QUAL"};
	printf("%s\n", path);
	printf("%5s: %20lld\n", "RECORDS", nl);
	for (int i = 0; i < F; i++) {
		bfields[i] += bclose(bf + i);
		zfields[i] += zclose(zf + i);
	}
	for (int i = 0; i < F; i++) {
		printf("%5s: %20lld %20lld %20lld\n", NF[i].c_str(), fields[i], zfields[i], bfields[i]);
	}
}


int main (int argc, char **argv) 
{
	std::ios_base::sync_with_stdio(false);

	if (argc != 2) {
		fprintf(stderr, "Usage: columnar <file.fq|file.sam|file.bam>\n", argv[1]);
		return 1;
	}

	ifstream in(argv[1], ifstream::ate | ifstream::binary);
	if (!in.is_open()) {
		fprintf(stderr, "File %s is not valid file!\n", argv[1]);
		return 1;
	}
	size_t sz = in.tellg(); 
	in.close();

	string arg = argv[1];
	if ((arg.size() >= 3 && arg.substr(arg.size() - 3) == ".fq") ||
		(arg.size() >= 6 && arg.substr(arg.size() - 6) == ".fastq"))
	{
		parse_fastq(argv[1]);
	}
	else
	{
		ifstream fin(argv[1]);
		char magic[5] = {0};
		fin.read(magic, 2);
		fin.close();
		if (magic[0] == 0x1f && (unsigned char)magic[1] == 0x8b) 
			parse_bam(argv[1]);
		else
			parse_sam(argv[1]);
	}

	printf("\nSIZE: %lu\n", sz);

	return 0;
}
