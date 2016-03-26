sam = [
	{
		"name": "pigz",
		"params": {
			"cmd": 		"pigz-2.3.3/pigz",
			"cmparg": 	"-c -p {threads}",
			"decarg":	"-c -d -p {threads}",
			"stdin":	"{in}",
			"stdout":	"{out}",
			"ext":		"gz"	
		}
	},
	{
		"name": "samtools",
		"params": {
			"cmd": 		"samtools/samtools",
			"cmparg": 	"view -b {in} -o {out}",
			"decarg":	"view -h {in} -o {out}",
			"ext":		"bam"
		}
	},
	{
		"name": "deez",
		"params": {
			"cmd": 		"deez/deez",
			"cmparg": 	"-v1 -t {threads} -r {ref} -! {in} -o {out}",
			"decarg":	"-v1 -t {threads} -r {ref} -! {in} -o {out}",
			"ext":		"dz",
			"modes": {
				"qual": "-q1",
			}
		}
	},
	{
		"name": "cramtools",
		"params": {
			"pre":		"java -jar",
			"cmd":		"cramtools/cramtools-2.1.jar",
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
			"cmd": 		"pigz-2.3.3/pigz",
			"cmparg": 	"-c -p {threads}",
			"decarg":	"-c -d -p {threads}",
			"stdin":	"{in}",
			"stdout":	"{out}",
			"ext":		"gz",
			"paired":	True,
		}
	},
	{
		"name": "scalce-single",
		"params": {
			"cmd": 		"scalce/scalce",
			"cmparg": 	"-T {threads} {in} -o {out}",
			"decarg":	"-d -T {threads} {in}_1.scalcer -o {out}",
			"ext":		"scalce-single",
			"paired":	False,
			"multi":	True,
		}
	},
	{
		"name": "slimfastq",
		"params": {
			"cmd": 		"slimfastq/slimfastq",
			"cmparg": 	"-u {in} -f {out} -O",
			"decarg":	"-d {in}  {out} -O",
			"ext":		"slimfastq",
			"paired":	True,
		}
	},
]
