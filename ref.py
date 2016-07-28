#!/usr/bin/env python
# 786

import sys, os, errno

# ref.fa.sc -- reference chromosomes in special files
# ref.fa.fai -- samtools index
# ref.fa.cbc -- reference for CBC

def mkdir(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST or not os.path.isdir(path):
			raise

ref = sys.argv[1]
os.system('samtools faidx {}'.format(ref))
os.system('cat {0} | gzip -c > {0}.gz'.format(ref))

mkdir('{}.sc'.format(ref))
fo = 0
with open('{}.cbc'.format(ref), 'w') as fcbc:
	with open(ref) as f:
		for l in f:
			l = l.strip()
			if l[0] == '>':
				if fo != 0: 
					fo.close()
				loc = '{}.sc/{}.fa'.format(ref, l[1:].split()[0])
				print loc
				fo = open(loc, 'w')
				print >>fcbc, loc
			print >>fo, l
fo.close()
