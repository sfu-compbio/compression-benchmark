sam = [
	{
		"name": "pigz",
		"params": {
			"cmd": 		"pigz",
			"cmparg": 	"-c -p {threads}",
			"decarg":	"-c -d -p {threads}",
			"stdin":		"{in}",
			"stdout":	"{out}",
			"ext":		"gz"	
		}
	},
	{
		"name": "pbzip2",
		"params": {
			"cmd": 		"pbzip2",
			"cmparg": 	"-c -p{threads}",
			"decarg":	"-c -d -p{threads}",
			"stdin":		"{in}",
			"stdout":	"{out}",
			"ext":		"bz2"	
		}
	},
	{
		"name": "samtools",
		"params": {
			"cmd": 		"samtools",
			"cmparg": 	"view -b {in} -o {out}",
			"decarg":	"view -h {in} -o {out}",
			"ext":		"bam"
		}
	},
	{
		"name": "scramble",
		"params": {
			"cmd": 		"scramble",
			"cmparg": 	"-I sam -O cram -t {threads} {in} {out}",
			"decarg":	"-I cram -O sam -t {threads} {in} {out}",
			"ext":		"scramble.cram",
			"modes": {
				"": "-r {ref}",
				"noref": "-x",
				"bzip2": "-j -7 -r {ref}"
			}
		}
	},
	{
		"name": "sambamba",
		"params": {
			"cmd": 		"sambamba",
			"cmparg": 	"view -S -f bam -t {threads} {in} -o {out}",
			"decarg":	"view -h -t {threads} {in} -o {out}",
			"ext":		"sambamba.bam"
		}
	},
	{
		"name": "sam_comp",
		"params": {
			"cmd": 		"sam_comp",
			"cmparg": 	"-r {ref}.sc",
			"decarg":	"-d -r {ref}.sc",
			"stdin":		"{in}",
			"stdout":	"{out}",
			"ext":		"zam"
		},
	},
	{
		"name": "cbc",
		"params": {
			"cmd": 		"cbc",
			"cmparg": 	"{in} {out}",
			"decarg":	"{in} {ref}.cbc {out}", 
			"ext":		"cbc"
		}
	},
	{
		"name": "quip",
		"params": {
			"cmd": 		"quip",
			"cmparg": 	"-c -v {in}",
			"decarg":	"-c -v -d -o sam {in}",
			"stdout":	"{out}",
			"ext":		"qp",
			"modes": {
				"ref": "-r {ref}",
				"asm": "-a",
			}
		}
	},
	{
		"name": "deez",
		"params": {
			"cmd": 		"deez",
			"cmparg": 	"-t {threads} -r {ref} -! {in} -o {out}",
			"decarg":	"-t {threads} -r {ref} -! {in} -o {out}",
			"ext":		"dz",
			"modes": {
				"qual": "-q1",
			}
		}
	},
	{
		"name": "picard",
		"params": {
			"pre":		"java -jar",
			"cmd":		"picard.jar",
			"cmparg": 	"SamFormatConverter I={in} O={out} VALIDATION_STRINGENCY=SILENT",
			"decarg":	"SamFormatConverter I={in} O={out} VALIDATION_STRINGENCY=SILENT",
			"ext":		"picard.bam"
		},
	},
	{
		"name": "cramtools",
		"params": {
			"pre":		"java -jar",
			"cmd":		"cramtools.jar",
			"cmparg": 	"cram --ignore-md5-mismatch --capture-all-tags --input-is-sam -Q -n -R {ref} -I {in} -O {out}",
			"decarg":	"bam --ignore-md5-mismatch --print-sam-header -R {ref} -I {in} -O {out}",
			"ext":		"cram"
		},
	}
]

fastq = [
	{
		"name": "pigz",
		"params": {
			"cmd": 		"pigz",
			"cmparg": 	"-c -p {threads}",
			"decarg":	"-c -d -p {threads}",
			"stdin":		"{in}",
			"stdout":	"{out}",
			"ext":		"gz",
			"paired":	True,
		}
	},
	{
		"name": "pbzip2",
		"params": {
			"cmd": 		"pbzip2",
			"cmparg": 	"-c -p{threads}",
			"decarg":	"-c -d -p{threads}",
			"stdin":		"{in}",
			"stdout":	"{out}",
			"ext":		"bz2",
			"paired":	True,
		}
	},
	{
		"name": "scalce",
		"params": {
			"cmd": 		"scalce",
			"cmparg": 	"-T {threads} {in} -o {out} -B 1G",
			"revcmp":	"-r",
			"decarg":	"-d -T {threads} {in}_1.scalcer -o {out}",
			"decrevcmp":"-r",
			"ext":		"scalce",
			"paired":	True,
		}
	},
	{
		"name": "scalce-single",
		"params": {
			"cmd": 		"scalce",
			"cmparg": 	"-T {threads} {in} -o {out} -B 1G",
			"decarg":	"-d -T {threads} {in}_1.scalcer -o {out}",
			"ext":		"scalce-single",
			"paired":	False,
			"multi":		True,
		}
	},
	{
		"name": "dsrc",
		"params": {
			"cmd": 		"dsrc",
			"cmparg": 	"c -v -t{threads} {cmpmode} {in} {out}",
			"decarg":	"d -v -t{threads} {in} {out}",
			"ext":		"dsrc",
			"modes": {
				"m2": "-m2"
			},
			"paired":	True,
		}
	},
	{
		"name": "orcom",
		"params": {
			"cmd": 		"orcom.sh",
			"cmparg": 	"e {threads} '{in}' {out}",
			"decarg":	"d {threads} {in} {out}",
			"ext":		"orcom",
			"paired":	False,
			"multi":	True,
		}
	},
	{
		"name": "quip",
		"params": {
			"cmd": 		"quip",
			"cmparg": 	"-c -v {in}",
			"decarg":	"-c -v -d -o fastq {in}",
			"stdout":	"{out}",
			"ext":		"qp",
			"modes": {
				"asm": "-a"
			},
			"paired": True,
		}
	},
	{
		"name": "fqzcomp",
		"params": {
			"cmd": 		"fqzcomp",
			"cmparg": 	"{cmpmode} -P {in} {out}", # P ~ no multith
			"decarg":	"-d -P {in} {out}",
			"ext":		"fqz",
			"modes": {
				"extra": "-s9+ -q3 -n2 -e"
			},
			"paired":	True,
		}
	},
	{
		"name": "fastqz",
		"params": {
			"cmd": 		"fastqz",
			"cmparg": 	"c {in} {out}",
			"decarg":	"d {in} {out}",
			"ext":		"fastqz",
			"paired":	True,
		}
	},
	{
		"name": "slimfastq",
		"params": {
			"cmd": 		"slimfastq",
			"cmparg": 	"-u {in} -f {out} -O",
			"decarg":	"-d {in}  {out} -O",
			"ext":		"slimfastq",
			"paired":	True,
		}
	},
	{
		"name": "kpath",
		"params": {
			"cmd": 		"kpath",
			"cmparg": 	"encode -p={threads} -ref={ref}.gz -reads={in} -out={out}",
			"decarg":	"decode -p={threads} -ref={ref}.gz -reads={in} -out={out}",
			"ext":		"kpath",
			"paired":	False,
		}
	},	
	{
		"name": "lfqc",
		"params": {
			"cmd": 		"lfqc/lfqc/",
			"cmparg": 	"lfqc.rb -solexa {in}",
			"cmppost":	"mv {in}.lfqc {out}",
			"decarg":	"lfqcd.rb {in} {out}",
			"ext":		"lfqc",
			"paired":	False,
		}
	},
	{
		"name": "leon",
		"params": {
			"cmd": 		"leon.sh",
			"cmparg": 	"e {in} {out} {threads}",
			"decarg":	"d {in} {out} {threads}",
			"ext":		"leon",
			"paired":	False,
			"multi":    False,
		}
	},
	{
		"name": "fqc",
		"params": {
			"cmd": 		"fqc.sh",
			"cmparg": 	"e {in} {out}",
			"decarg":	"d {in} {out}",
			"ext":		"fqc",
			"paired":	True,
			"multi":    False,
		}
	},
	{
		"name": "mince",
		"params": {
			"cmd": 		"mince.sh",
			"cmparg": 	"e {in} {out} {threads}",
			"decarg":	"d {in} {out} {threads}",
			"revcmp":   "{revcmp}",
			"ext":		"mince",
			"paired":	True,
			"multi":    False,
		}
	},
	{
		"name": "mince-single",
		"params": {
			"cmd": 		"mince.sh",
			"cmparg": 	"e {in} {out} {threads}",
			"decarg":	"d {in} {out} {threads}",
			"ext":		"mince",
			"paired":	False,
			"multi":    False,
		}
	},
	{
		"name": "lw-fqzip",
		"params": {
			"cmd": 		"lwfqzip.sh",
			"cmparg": 	"e {in} {out} {ref}",
			"decarg":	"d {in} {out} {ref}",
			"ext":		"lz",
			"paired":	False,
			"multi":    False,
		}
	},
	{
		"name": "kic",
		"params": {
			"cmd":		"kic.sh",
			"cmparg":	"e {in} {out} {threads}",
			"decarg":	"d {in} {out} {threads}",
			"ext":		"kic",
			"paired":	True,
			"multi":		False,
		}
	},
	{
		"name": "beetl",
		"params": {
			"cmd":		"beetl.sh",
			"cmparg":	"e {in} {out} 1",
			"decarg":	"d {in} {out} 1",
			"ext":		"beetl",
			"paired":	True,
			"multi":    False,
		}
	},
]
