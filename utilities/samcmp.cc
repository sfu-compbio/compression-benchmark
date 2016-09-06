#include <unordered_set>
#include <unordered_map>
#include <iostream>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <string>
using namespace std;

#define L(c,...)\
	fprintf(stdout, c"\n", ##__VA_ARGS__)
#define E(c,...)\
	fprintf(stderr, c"\n", ##__VA_ARGS__)

const int MAXLEN = 16 * 1024 * 1024;
int MAXLINE = 1000000;

bool sf (char *a, char *b) {
	return (strcmp(a,b) < 0);
}

struct Record {
    char *line;
    char *fields[50];
    int f;

    // Lazy version to avoid rule of three
    void assign (char *buff) {
    	line = strdup(buff);
		char *c = fields[0] = line;
		f = 1;
		while (*c) {
			if (*c == '\t') 
				*c = 0, fields[f++] = c + 1;
			c++;
		}	
		assert(f>=11);
		if (f > 11) 
			sort(fields + 11, fields + f, sf);
		assert(f<50);
    }

    Record(): line(0) {}
    ~Record() {
    	if (line) free(line);
    }

	bool operator<(const Record &r) const {
    	if (int x = strcmp(fields[2], r.fields[2])) return x < 0;
    	return atoi(fields[3]) < atoi(r.fields[3]);
    }    

    bool operator==(const Record &r) const {
    	if (!strcmp(fields[0], r.fields[0])) return false;
    	if (!strcmp(fields[2], r.fields[2])) return false;
    	if (!strcmp(fields[3], r.fields[3])) return false;
    	if (!strcmp(fields[9], r.fields[9])) return false;
    	return true;
    }
};

size_t readfile(FILE *f, vector<Record> &vec, string &comment) {
	static char *buffer(0);
	if (!buffer) buffer = (char*)malloc(MAXLEN);
	size_t rd = 0;
	vec.clear();
	vec.reserve(MAXLINE);
	while (fgets(buffer, MAXLEN, f)) {
		if (buffer[0] == '@') 
			comment += buffer;
		else {
			int l = strlen(buffer) - 1;
			while (l && (buffer[l] == '\r' || buffer[l] == '\n'))
				buffer[l--] = 0;
			rd++;
			vec.push_back(Record());
			vec.back().assign(buffer);
		}
		if (vec.size() >= MAXLINE) break;
	}
	return rd;
}

// How many B's items are different from A's?
int main (int argc, char **argv) 
{
	std::ios_base::sync_with_stdio(false);
	if (argc != 4) {
		E("Usage: samcmp <original> <copy> <maxline>");
		exit(1);
	}

	FILE *fa = fopen(argv[1], "r");
	FILE *fb = fopen(argv[2], "r");
	MAXLINE = atoi(argv[3]);
	E("Reading %s, %s; maxline=%d", argv[1], argv[2], MAXLINE);
	vector<Record> A, B;
	string cA, cB;

	char buf[1000];
	sprintf(buf, "cmp %s %s", argv[1], argv[2]);
	int ret = system(buf);
	if (!ret) {
		L("Equal cmp\nDone %s\n", argv[1]);
		exit(0);
	}

	vector<int> unequal(11, 0);
	unordered_map<int, int> 
		missing_optA, 
		missing_optB,
		unequal_opt;
	unordered_set<int> optionals;

	int missA = 0, missB = 0;
	int linesA = 0, linesB = 0;
	while (1) {
		size_t szA, szB;
		linesA += (szA = readfile(fa, A, cA));
		linesB += (szB = readfile(fb, B, cB));
		if (!szA && !szB) break;
		L("Read %d (%d) / %d (%d) lines, %d", szA, linesA, szB, linesB, A.size());

		int iA = 0, iB = 0;
		while (1) {
			while (iA < A.size() && (iB == B.size() || A[iA] < B[iB])) 
				missB++, iA++;
			while (iB < B.size() && (iA == A.size() || B[iB] < A[iA]))
				missA++, iB++;
			if (iA == A.size() || iB == B.size())
				break;

			/* 	Assume that they are equal
				Due to the speed concerns, we won't do any matching... */
			for (int i = 0; i < 11; i++)
				unequal[i] += (strcmp(A[iA].fields[i], B[iB].fields[i]) != 0);

			int oa = 11, ob = 11;
			while (oa < A[iA].f && ob < B[iB].f) {
				auto &xa = A[iA].fields[oa];
				auto &xb = B[iB].fields[ob];
				int ya = xa[0] * 128l + xa[1];
				int yb = xb[0] * 128l + xb[1];
				optionals.insert(ya);
				optionals.insert(yb);

				if (ya < yb) missing_optB[ya]++, oa++;
				else if (yb < ya) missing_optA[yb]++, ob++;
				else {
					if (strcmp(xa, xb)) unequal_opt[ya]++;
					oa++, ob++;
				}
			}	

			iA++, iB++;
		}
	}

	for (auto &i: missing_optA) 
		optionals.insert(i.first);
	for (auto &i: missing_optB) 
		optionals.insert(i.first);
	for (auto &i: unequal_opt) 
		optionals.insert(i.first);

	const char *fields[] = { "QUERYNAME", "FLAG", "REFNAME", "POS", "MAPQUAL", "CIGAR", "REFNEXT", "POSNEXT", "TLEN",  "SEQ",  "QUAL" }; 	
	
	E("> ORIG    %10d (%s)", linesA, argv[1]);
	E("< COPY    %10d (%s)", linesB, argv[2]);

	bool q= linesA!=linesB;
	if (cA != cB) E("Comments  %10s", "not equal"), q=1;
	if (missB) E("Miss      %10d lines", missB), q=1;
	if (missA) E("Extra     %10d lines", missA), q=1;
	
	E("");
	for (int i = 0; i < 11; i++) if (unequal[i])
		E("%-9s %10d lines unequal", fields[i], unequal[i]), q=1;
	for (auto &i: optionals) 
		if (missing_optB[i]|| missing_optA[i]|| unequal_opt[i])
			E("%c%-8c %10d missing, %10d extra, %10d unequal", i/128, i%128, missing_optB[i], missing_optA[i], unequal_opt[i]), q=1;

	if (!q) E("Equal");

	L("Done %s", argv[1]);
	return 0;
}
