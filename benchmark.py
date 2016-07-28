#!/usr/bin/env python
# 786

import os, sys, errno, argparse, subprocess as sp, fnmatch, struct, time, datetime, glob, signal, tempfile, shutil, shlex
import tools

class Logger(object):
	def __init__(self, f, sample, mail):
		self.sample = sample
		self.term = sys.stdout
		self.mail = mail
		self.f = f
		if f != '':
			self.log = open(f, 'w+')
		else:
			self.log = None
	def __del__(self):
		if self.log is not None:
			self.log.close()
		with open(self.f) as f:
			text = 'Complete!\n\n' + f.read()
			if self.mail != '':
				mail(text, self.sample, self.mail)
	def write(self, message):
		self.term.write(message)
		self.term.flush()
		if self.log is not None:
			self.log.write(message) 
			self.log.flush()

def mkdir(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST or not os.path.isdir(path):
			raise

def timefmt(sec):
	sec = round(sec, 1)
	return '{1} ({0} ms)'.format(sec, time.strftime('%H:%M:%S', time.gmtime(sec)))

def callcmd(cmd):
	return sp.Popen(cmd, shell=True).wait()

def reset_cache(): # requires root
	callcmd('sync && echo 3 > /proc/sys/vm/drop_caches')

def mail(msg, subject, to):
	text  = 'From: Benchmark Script <benchmark@localhost>\n'
	text += 'To: {}\n'.format(to)
	text += 'Subject: {}\n'.format(subject)
	text += 'MIME-Version: 1.0\nContent-Type: text/html\nContent-Disposition: inline\n'
	text += '<html><body><pre style="font: monospace">{}</pre></body></html>'.format(msg)

	callcmd('echo "{}" | sendmail {}'.format(text, to))

proc = None
def execute(cmd, fin, fout, ferr, exclusive=False, single_thread=False):
	fi = sp.PIPE
	if fin != '':
		fi = open(fin, 'r')	
	fo = open(fout, 'w')
	fe = open(ferr, 'w')
	
	if exclusive and single_thread: # requires root
		cmd = 'chrt -f 99 ' + cmd
	if single_thread: # bind to cpu #3 by default
		cmd = 'taskset 1 ' + cmd
	cmd = '/usr/bin/time -p -o _time_ ' + cmd

	global proc
	proc = sp.Popen(shlex.split(cmd), stdin=fi, stdout=fo, stderr=fe, env=os.environ.copy())

	tm = time.time()

	try:
		ru = os.wait4(proc.pid, 0)
	except:
		raise
	finally:
		tm = time.time() - tm
		proc = None
		if fi != sp.PIPE:
			fi.close()
		fo.close()
		fe.close()
		#if ru[1] != 0:
		#	raise Exception('Command "{}" failed with exit code {}'.format(cmd, ru[1])
 			
	ru = list(ru) + [float(tm), [], cmd]
	with open('_time_') as ft:
		for l in ft:
			l = l.strip().split()
			try:
				t = (l[0], float(l[1]))	
				ru[-2].append(t)
			except ValueError:
				pass
	os.remove('_time_')

	return ru

def signal_handler(signal, frame):
	if proc is not None:
		proc.kill()
	else:
		sys.exit(0)

def is_glob(f):
	p = glob.glob(f)
	return len(p) != 1 or p[0] != f

def run_tool(sample_name, input_file, input_glob, tool_name, tool_params, params, args, output_extension):
	threads = params['threads']
	input_name = os.path.basename(input_file)
	control_dir = '{}/control'.format(sample_name)
	mkdir(control_dir)
	log_dir = '{}/log'.format(sample_name)
	mkdir(log_dir)
	output_dir = '{}/output'.format(sample_name)
	mkdir(output_dir)
	mkdir('{}/compressed/{}'.format(output_dir, tool_name))
	mkdir('{}/decompressed/{}'.format(output_dir, tool_name))

	exepath = 'tools/{}'.format(tool_params['cmd'])
	if 'pre' in tool_params:
		exepath = '{} {}'.format(tool_params['pre'], exepath);

	for mode in [ 'cmp', 'dec' ]:
		control_file = '{}/{}.{}.{}.{}'.format(control_dir, input_name, tool_name, threads, mode)
		if os.path.isfile(control_file) and not args.force:
			print 'Already completed'
			continue
		if os.path.isfile(control_file):
			os.remove(control_file)

		params['in'] = input_file
		params['out'] = '{}/compressed/{}/{}.{}'.format(output_dir, tool_name, input_name, tool_params['ext'])
		if mode == 'dec': # set compressions's OUT to decompression's IN
			params['in'] = params['out']
			params['out'] = '{}/decompressed/{}/{}.{}'.format(output_dir, tool_name, input_name, output_extension)
			
		fe = '{}/{}.{}.{}.{}.log'.format(log_dir, input_name, tool_name, threads, mode)
		fo = '{}/{}.{}.{}.{}.out'.format(log_dir, input_name, tool_name, threads, mode)
		if 'stdout' in tool_params:
			fo = tool_params['stdout'].format(**params)
		fi = ''
		if 'stdin' in tool_params:
			fi = tool_params['stdin'].format(**params)

		if input_glob != '' and mode == 'cmp':
			params['in'] = ' '.join(sorted(glob.glob(input_glob)))
		cmd = '{}{}{}'.format(exepath, ' ' if exepath[-1] != '/' else '', tool_params[mode + 'arg'].format(**params))

		if args.clear_cache:
			reset_cache()
		try:
			print '***', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '***', 
			ru = execute(cmd, fi, fo, fe, args.rt, threads == 1)
			# concatenate stderr and stdout to single file
			if 'stdout' not in tool_params:
				with open(fe, 'a') as f:
					print >>f
					print >>f, "#" * 80
					print >>f
					with open(fo) as foh:
						for l in foh:
							print >>f, l
				os.remove(fo)

			if mode + 'post' in tool_params:
				callcmd(tool_params[mode + 'post'].format(**params))

			print '*** {} ***'.format('OK' if ru[1] == 0 else 'FAIL')
			print '  Command:      ', ru[-1]
			if fi != '':
				print '    stdin:       ' + fi
			if 'stdout' in tool_params:
				print '    stdout:      ' + fo
			print '    stderr:      ' + fe
			print '  Process PID:  ', ru[0]
			print '  Exit code:    ', ru[1]
			print '  Wall time:    ', timefmt(ru[3])
			print '  Memory (MB):  ', round(ru[2].ru_maxrss / 1024.0, 1)
			print '  Resources:    '
			for l in str(ru[2])[23:-1].split(', '):
				l = l.strip().split('=')
				if l[1] != '0':
					print '    {:<12}'.format(l[0] + ':'), 
					if 'time' in l[0]:
						print timefmt(float(l[1]))
					else:
						print l[1]
			print '  GNU time:     '
			for l in ru[4]:
				print '    {:<12}'.format(l[0] + ':'), timefmt(float(l[1]))
			print '  Size (MB):    ', 
			try:
				f = []
				for g in glob.glob(params['out'] + '*'): # all files with same prefix
					# print mode, g, os.path.isdir(g)
					if os.path.isdir(g):
						for R, D, F in os.walk(g):
							f += [os.path.join(R, ff) for ff in F]
					else:
						f.append(g)
				sz = sum([os.path.getsize(ff) for ff in f])
			except:
				f = []
				sz = 0
			finally:
				print '?' if sz == 0 else '{1:,.2f} ({0} bytes)'.format(sz, sz / (1024 * 1024.0)),
				print '({})'.format(', '.join(f))
			print '  Free space:     ',
			print os.popen('df -h {} | tail -1'.format(output_dir)).read().strip()
			if ru[1] == 0:
				os.mknod(control_file)
				# move completed files to large storage so that main storage doesn't get full
				# useful when testing gigantic files on multiple tools
				if mode == 'dec' and args.output_dir != '': 
					try:
						os.system('rsync -Pva --remove-source-files {}/compressed/{} {}/compressed/'.format(output_dir, tool_name, args.output_dir))
						os.system('rsync -Pva --remove-source-files {}/decompressed/{} {}/decompressed/'.format(output_dir, tool_name, args.output_dir))
					except Exception as e:
						print e
			else:
				break
		except OSError as e:
			print 'Process terminated with {}'.format(e)
			break
	print

def run(sample_name, tools, args, threads, param_fn):
	title = '{} with {} threads'.format(sample_name, threads)
	print '+' * 72, '\n', '+{:^70}+'.format(title), '\n', '+' * 72
	print 

	for tool in tools:
		if 'modes' not in tool['params']:
			tool['params']['modes'] = {}
		if '' not in tool['params']['modes']:
			tool['params']['modes'][''] = ''

		for m, mode_params in tool['params']['modes'].iteritems():
			name, params = tool['name'], tool['params']
			if m != '': name += '-' + m

			cmpmode = ''
			decmode = ''
			if '{cmpmode}' not in params['cmparg']:
				params['cmparg'] += ' {cmpmode}'
			if '{decmode}' not in params['decarg']:
				params['decarg'] += ' {decmode}'
			# support for decompression mode arguments
			if isinstance(mode_params, list) and len(mode_params) > 1:
				cmpmode = mode_params[0]
				decmode = mode_params[1]
			elif not isinstance(mode_params, list):
				cmpmode = mode_params

			if name[:4] == 'quip':
				if threads != 4:
					continue
			elif threads > 1 and '{threads}' not in params['cmparg']:
				continue
			
			print '#' * 72, '\n', '#{:^70}#'.format(name), '\n', '#' * 72

			input_params = {
				'ref': args.ref,
				'threads': threads,	
				'cmpmode': cmpmode,
				'decmode': decmode,
			}

			(input_files, output_extension, glob) = param_fn(args, tool, input_params)
			for input_index, input_file in enumerate(input_files):
				print ">>> {} (File {}: {})".format(name, input_index + 1, input_file)
				input_params['cmpmode'] = input_params['cmpmode'].format(**input_params)
				input_params['decmode'] = input_params['decmode'].format(**input_params)
				run_tool(sample_name, input_file, glob, name, params, input_params, args, output_extension)


def getrevcmp(path):
	p = os.path.basename(path)
	f = p.rfind("_1")
	r = "_2"
	if f == -1:
		f = p.rfind(".1")
		r = ".2"
	if f != -1:
		path2 = os.path.dirname(path) + '/' + p[:f] + r + p[f + 2:]
		#print path2
		if os.path.isfile(path2):
			return path2
		return ''
	return ''

def get_fastq_params(args, tool, params):
	infiles = [ args.input ]
	if args.glob == '':
		input_glob = ''
		infilerev = getrevcmp(infiles[0]) if tool['params']['paired'] else ''
		if infilerev != '':
			if 'revcmp' in tool['params']:
				params['cmpmode'] += ' ' + tool['params']['revcmp'].format(revcmp=infilerev)
			if 'decrevcmp' in tool['params']:
				params['decmode'] += ' ' + tool['params']['decrevcmp'].format(revcmp=infilerev)
			else: 
				infiles.append(infilerev)
	else:
		input_glob = args.glob
		if 'multi' not in tool['params'] or not tool['params']['multi']:
			infiles = sorted(glob.glob(input_glob))
			input_glob = ''
	return (infiles, 'fq', input_glob)

def get_fasta_params(arg, tools, params):
	return (get_fastq_params(arg, tools, params)[0], 'fa')

def get_sam_params(args, tool, params):
	return ([ args.input ], 'sam', '')
	
def getargs():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', '-i', help="Input file for sample (FASTQ, FASTA or SAM)")
	parser.add_argument('--glob', '-g', default='', help="Input files glob for multi-FASTQ samples (NOT SUPPORTED!)")
	parser.add_argument('--ref', '-r', help="Folder containing reference files")
	parser.add_argument('--force', '-f', action='store_true', help="Re-run all tools")
 	parser.add_argument('--rt', '-R', action='store_true', help='Use SCHED_FIFO real-time priority (requires root)')
 	parser.add_argument('--clear-cache', '-C', action='store_true', help='Clear filesystem cache before tests (requires root)')
 	parser.add_argument('--output-dir', '-o', default='', help="Move output to this directory after finished decompression")
 	parser.add_argument('--copy', '-c', action='store_true', help='Copy input files to the current directory first')
 	parser.add_argument('--email', '-e', default='')
 	parser.add_argument('--threads', '-t', default='1')
	return parser.parse_args()

signal.signal(signal.SIGINT, signal_handler)

ts = time.time()
arg = getargs()

#callcmd('service puppet stop')

if arg.copy: # TODO copy reverse complement!
	new_input = '{}/{}'.format(os.getcwd(), os.path.basename(arg.input))
	if not os.path.isfile(new_input):
		print 'Copying new file...'
		shutil.copy(arg.input, os.getcwd())
	vars(arg)['input'] = new_input

if arg.ref != '':
	vars(arg)['ref'] = os.path.abspath(arg.ref)

sample_name, sample_ext = os.path.splitext(os.path.basename(arg.input))
if len(sample_ext) > 1:
	sample_ext = sample_ext[1:]
if sample_ext in [ 'fastq', 'fq' ]:
	param_fn = get_fastq_params
	tools = tools.fastq
	print 'Detected FASTQ file'
	if len(sample_name) > 2 and sample_name[-2] == '_':
		sample_name = sample_name[:-2]
elif sample_ext in [ 'fasta', 'fa' ]:
	param_fn = get_fasta_params
	tools = tools.fasta
	print 'Detected FASTA file'
	if len(sample_name) > 2 and sample_name[-2] == '_':
		sample_name = sample_name[:-2]
elif sample_ext in [ 'sam' ]:
	param_fn = get_sam_params
	tools = tools.sam
	print 'Detected SAM file'
else:
	print 'Unknown file format for: {}'.format(arg.input)
	exit(1)

if arg.output_dir != '':
	try:
		mkdir(arg.output_dir)
	except Exception as e:
		print 'Cannot make output directory; continuing'
if arg.output_dir != '':
	mkdir(arg.output_dir + '/compressed')
	mkdir(arg.output_dir + '/decompressed')

mkdir(sample_name)
sys.stdout = Logger('{}/benchmark.log_{}'.format(sample_name, datetime.datetime.now().strftime("%y%m%d%H%M")), sample_name, arg.email)

print arg
threads = map(int, arg.threads.split(','))
for thread in threads:
	tx = time.time()
	run(sample_name, tools, arg, thread, param_fn)
	tx = time.time() - tx
	print

ts = time.time() - ts

print 'Done!'
