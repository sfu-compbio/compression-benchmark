/// 786

#include <bits/stdc++.h>
using namespace std;

#define L(c,...)\
	fprintf(stdout, c"\n", ##__VA_ARGS__)
#define E(c,...)\
	fprintf(stderr, c"\n", ##__VA_ARGS__)
#define EN(c,...)\
	fprintf(stderr, c, ##__VA_ARGS__)

const int MAXLEN = 16 * 1024 * 1024;
int MAXLINE = 1000000;

// SC
// Seq; Name; Qual; Comment

int COMPARE_BY = 0; // compare by names by default

int USE_RNAME = 1;
int USE_SEQ = 1;
int USE_QUAL = 1;
int USE_COMMENT = 1;

int CALC_MISSING = 1;

char revcmp(char c) 
{
	if (c >= 'A' && c <= 'U')
		return "TBGDEFCHIJKLMNOPQRSAU"[c - 'A'];
	return c;
}

struct Record {
    string content;
    int fields[5];

	void assign () {
		int f = 0, s = 0;
		for (int i = 0; i < content.size(); i++) 
			if (content[i] == '\n') {
				fields[f++] = s;
				s = i + 1;
				content[i] = 0;
				if (f >= 4) break;
			}
		while (f < 4) 
			fields[f++] = s;
		assert(f == 4);

		fields[4] = fields[0];
		for (int i = 0; i < fields[1]; i++)
			if (isspace(content[i])) {
				fields[4] = i + 1;
				content[i] = 0;
				break;
			}
    }

    bool operator<(const Record &r) const {
    	if (int x = strcmp(content.c_str() + fields[COMPARE_BY], r.content.c_str() + r.fields[COMPARE_BY])) return x < 0; // check seq
    	return false;
    }

    bool operator==(const Record &r) const {
    	if (!strcmp(content.c_str() + fields[COMPARE_BY], r.content.c_str() + r.fields[COMPARE_BY])) return true; // check seq
    	return false;
    }

    void pr(){
    	E("%s|%s|%s",content.c_str() + fields[1], content.c_str() + fields[0],content.c_str() + fields[3]);
	}
};

size_t readfile(ifstream &f, vector<Record> &vec) {
	size_t rd = 0;
	vec.clear();
	vec.reserve(MAXLINE);
	string p = "";
	string l;
	while (getline(f, l)) {	
		Record r;
		if (p.size()) l += p + '\n', p = "";
		r.content = l + '\n';
		//L("%d: %s", rd, l.c_str());

		for (int i = 1; i < USE_RNAME + USE_SEQ + USE_COMMENT + USE_QUAL; i++) {
			auto ft = f.tellg();
			getline(f, l);
			if (l[0] == '@') { 
				f.seekg(ft, f.beg);
				break;
			}
			else r.content += l + '\n';
		}
		
		rd++;
		vec.push_back(r);
		vec.back().assign();
		if (vec.size() >= MAXLINE) break;
	}
	return rd;
}

// How many B's items are different from A's?
int main (int argc, char **argv) 
{
	std::ios_base::sync_with_stdio(false);

	if (argc < 4) {
		E("Usage: fastqcmp <original> <copy> <maxline> <fields> <compare_function>");
		exit(1);
	}

	ifstream fa(argv[1]);
	if (!fa.is_open()) throw "file 1 invalid";
	
	ifstream fb(argv[2]);
	if (!fb.is_open()) throw "file 2 invalid";
	MAXLINE = atoi(argv[3]);
	if (!MAXLINE) throw "MAXLINE invalid";

	if (argc > 4) {
		char *use = argv[4];
		if (strlen(use) != 4)
			throw "invalid use string";
		USE_RNAME = (use[0] == '1');
		USE_SEQ = (use[1] == '1');
		USE_COMMENT = (use[2] == '1');
		USE_QUAL = (use[3] == '1');

		if (argc > 5) {
			COMPARE_BY = atoi(argv[5]);
			assert(COMPARE_BY < 4);
		}
	}
	
	E("Reading %s, %s; maxline=%d", argv[1], argv[2], MAXLINE);

	if (COMPARE_BY) {
		vector<const char*> c = { "RNAME", "SEQ", "QUAL" }; 
		E("Comparing by %s", c[COMPARE_BY]);
	}

	char buf[1000];
	sprintf(buf, "cmp %s %s", argv[1], argv[2]);
	int ret = system(buf);
	if (!ret) {
		L("Equal cmp\nDone %s\n", argv[1]);
		exit(0);
	}

	vector<Record> A, B;

	vector<size_t> unequal(5, 0);
	map<size_t, size_t> eqchar[5];
	vector<int64_t> nucmis(128,0);
	size_t missA = 0, missB = 0;
	size_t linesA = 0, linesB = 0, Nneq = 0, Ntot = 0;

	size_t numRCd = 0, lineA = 0, lineB = 0;
	while (1) {
		size_t szA = readfile(fa, A);
		size_t szB = readfile(fb, B);
		linesA += szA;
		linesB += szB;
		if (!szA && !szB) break;
		L("Read %lu (%lu) / %lu (%lu) lines, %lu", szA, linesA, szB, linesB, A.size());
		fflush(stdout);

		size_t iA = 0, iB = 0;
		while (1) {
			if (CALC_MISSING) {
				while (iA < A.size() && (iB == B.size() || A[iA] < B[iB])) { 
					//L("Skipping block %lu from file 1: %s", lineA, A[iA].content.c_str());
					missB++, iA++, lineA++;
				}
				while (iB < B.size() && (iA == A.size() || B[iB] < A[iA])) {
					//L("Skipping block %lu from file 2: %s", lineB, B[iB].content.c_str());
					missA++, iB++, lineB++;
				}
			}
			if (iA == A.size() || iB == B.size())
				break;
			/* 	Assume that they are equal
				Due to the speed concerns, we won't do any matching... */
			for (int i = 0; i < 5; i++) {
				if (i == 1 || i == 3) { // Seq, Qual
					int la = strlen(A[iA].content.c_str()+ A[iA].fields[i]);
					int lb = strlen(B[iB].content.c_str()+ B[iB].fields[i]);
					int ll = min(la, lb);
					int uneq = max(la,lb) - ll;
					for (int k = 0; k < ll; k++) if (*(A[iA].content.c_str()+A[iA].fields[i]+k) != *(B[iB].content.c_str()+B[iB].fields[i]+k)) {
						uneq++;
						if (i == 1) { 
							nucmis[B[iB].content[B[iB].fields[i]+k]]++;
						} else {
							if (*(A[iA].content.c_str()+A[iA].fields[1]+k) == 'N')
								Nneq++;
							Ntot++;
						}
					}
					if (uneq) {	
						eqchar[i][uneq]++, unequal[i]++;
					}
				} else {
					unequal[i] += (strcmp(A[iA].content.c_str() + A[iA].fields[i], B[iB].content.c_str() + B[iB].fields[i]) != 0);
				}
			}
			iA++, iB++, lineA++, lineB++; 
		}
	}

	const char *fields[] = { "NAME", "SEQ", "COMMENT", "QUAL", "COMMENTX" }; 	
	
	E("> ORIG    %10lu (%s)", linesA, argv[1]);
	E("< COPY    %10lu (%s)", linesB, argv[2]);

	bool q= linesA!=linesB;
	if (missB) E("Miss      %10lu lines", missB), q=1;
	if (missA) E("Extra     %10lu lines", missA), q=1;
	
	E("");
	for (int i = 0; i < 5; i++) if (unequal[i]) {
		E("%-9s %10lu lines unequal", fields[i], unequal[i]), q=1;
		if (eqchar[i].size()) {
			size_t cnt = 0;
			for (auto &c: eqchar[i]) {
				if (cnt++ == 101) {
					EN("...");
					break;
				}
				EN("%20s %lu mismatches: %lu lines\n", "", c.first, c.second);
			}
			E("");
		}
	}

	for (int i = 0; i < nucmis.size(); i++) if (nucmis[i]) 
		E("Nucleotide %c missed: %lu", i, nucmis[i]);
	if (Nneq)
		E("Wrong N quality: %lu of %lu", Nneq, Ntot);
	if (numRCd) 
		E("Wrong reverse complement: %lu", numRCd);

	if (!q) E("Equal");

	L("Done %s", argv[1]);
	return 0;
}
