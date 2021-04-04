#!/usr/bin/python
import re
import os
import sys, getopt
import codecs
import subprocess

class GlobalParameters :
	fontsize = "11"
	transpose = 0
	columns = 1


class ChordProcessor :
	def __init__(self, type = 'en') :
		self.output_format = None
		# semitones
		self.distance = [2, 2, 1, 2, 2, 2, 1]
		if type == 'en' :
			self.chord_list = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
		else:
			self.chord_list = ['DO', 'RE', 'MI', 'FA', 'SOL', 'LA', 'SI']

		# Builds the regular expression for detecting chords
		chlist = '('
		flag = True
		for c in self.chord_list :
			if not flag :
				chlist = chlist + '|'
			flag = False
			chlist = chlist+'('+c+')'
		chlist = chlist + ')'

		cdies = '(#|b)?'
		cmode = '(m(aj7)?)?'
		cadd = '(dim|sus4|sus2|add|(b)?(4|5|6|7|9|11|13)(\\+|b|#)?)'
		caddf = '(' + cadd + ')*'
		clast = '(/('+chlist+cdies+'|'+cadd+'))?'
		csep = '(\\|(x[1-9])?)'

		self.regex_chord_en = csep + '|' + '(' + chlist + cdies + cmode + caddf + clast + ')'
		#print self.regex_chord_en
		self.pattern_en = re.compile(self.regex_chord_en)
		
		self.verse = ["verse", "chorus", "pre-chorus", "solo", "break", "intro", "ending", "outro", "pre-outro", "bridge", "interlude"] 
		
		return

	def is_special(self, l) :
		for x in self.verse :
			y = '[' + x
			if l.strip().lower().startswith(y) :
				return True
		return False;
		

	def parse_chordbox(self, l) :
		w = l.split()
		chordname = w[0]
		fret = 1
		if len(w) == 3 :
			fret = int(w[1])
			s = w[2]
		else:
			s = w[1]
		self.output_format.print_chord_box(chordname, fret, s)
		return
		
		
	# If the patterns matches
	def is_a_chord(self, str) :
		m = self.pattern_en.match(str)
		if m :
			return m.group() == str
		else :
			return False


	# If the line "str" is composed entirely of chords and separations (|), then it
	# returns a list of pairs (chord, position), otherwise it returns None
	def chord_line(self, str) :
		words = str.split()
		last_pos = -1
		cs = []
		for w in words :
			if self.is_a_chord(w) :
				new_pos = str.find(w, last_pos+1)
				#if new_pos < last_pos :
				#	 new_pos = last_pos + len(w)
				pair = w, new_pos
				cs.append(pair)
				last_pos = new_pos
			else :
				return None

		return cs	
		
		
	def process_song(self,lines) :
		# search title
		local_title = lines[0]
		local_transpose = GlobalParameters.transpose
		local_columns = GlobalParameters.columns

		in_verse = False;
		in_tab = False;
		in_chordbox = False;
		x = 1  # index of first line

		while not lines[x].startswith('---') :
			l = lines[x].strip()
			if re.match('transpose', l) :
				i = l.find(':')
				local_transpose = int(l[i+1:])
			elif re.match('columns', l) :
				i = l.find(':')
				local_columns = int(l[i+1:])
			else :
				self.output_format.print_textline(lines[x])
			x = x + 1

		# start of the song 
		self.output_format.columns = local_columns
		self.output_format.start_song(lines[0])

		x = x + 1
		chord_sequence = None

		self.output_format.start_block()
		
		for l in lines[x:] :
			l = l[:-1]	# remove \n

			if not in_tab and l.strip() == '[tab]' :
				in_tab = True
				if in_verse : 
					in_verse = False 
					self.output_format.end_verse()
				self.output_format.end_block()
				self.output_format.start_verbatim()
			elif l.strip() == '[/]' and in_tab :
				in_tab = False
				self.output_format.end_verbatim()
				self.output_format.start_block()
			elif in_tab :
				self.output_format.print_textline(l)
			elif not in_chordbox and l.strip() == '[chord]' :
				in_chordbox = True
				if in_verse : 
					in_verse = False
					self.output_format.end_verse()
				self.output_format.end_block()
				self.output_format.start_chord_box()
			elif in_chordbox and l.strip() == '[/]' :
				in_chordbox = False
				self.output_format.end_chord_box()
				self.output_format.start_block()
			elif in_chordbox :
				self.parse_chordbox(l)
			elif l.strip() == '' and chord_sequence == None:	# an empty line ends the verse
				if in_verse:
					self.output_format.end_verse()
					in_verse = False
					chord_sequence = None
				else :
					#self.output_format.print_textline("\\\\")
					continue
			elif self.is_special(l) :
				if in_verse :
					self.output_format.end_verse();
					in_verse = False;
				self.output_format.bold(l.strip())
			elif chord_sequence != None :	# a verse with a chord sequence on top
				# mix chords with words
				final = u''
				q = 0
				prev_chord = u''
				for c, p in chord_sequence :  #c: chord, p:position
					if (local_transpose != 0) :
						c = self.transpose(c, local_transpose)
					if p > 0 :
						if p >= len(l) :
							if q < len(l) and len(l[q:].strip())>0 :
								final = final + self.output_format.print_chord(prev_chord, l[q:])
							else :
								final = final + self.output_format.print_chord(prev_chord, '~')
						else :
							if len(l[q:p].strip()) > 0 :
								final = final + self.output_format.print_chord(prev_chord, l[q:p])
								if l[p-1] == ' ' :
									final = final + ' '
							else : 
								final = final + self.output_format.print_chord(prev_chord, '~')

					q = p
					prev_chord = c

				if q < len(l) and len(l[q:].strip()) : final = final + self.output_format.print_chord(prev_chord, l[q:])
				else : final = final + self.output_format.print_chord(prev_chord, '~') 
				self.output_format.print_verse(final)
				in_verse = True
				chord_sequence = None
			else :
				# I should find the chords here
				if not in_verse:
					in_verse = True
					self.output_format.start_verse()
				chord_sequence = self.chord_line(l)
				if chord_sequence == None :
					self.output_format.print_verse(l)

		if in_verse:
			self.output_format.end_verse()
		self.output_format.end_song()
		self.output_format.columns = GlobalParameters.columns


	def transpose(self, chord, position) :
		#first, find the chord, I consider English for the moment
		for i in range(len(self.chord_list)) :
			if re.match(self.chord_list[i], chord, re.I) :
				break
		# print('Found : ' + self.chord_list[i])
		# print('i : ', i)

		modif = chord[len(self.chord_list[i]):]
		#print("Modif : ", modif)

		if re.match(self.chord_list[i] + '#', chord, re.I) :
			position = position + 1
			modif = chord[len(self.chord_list[i]) + 1:]
		if re.match(self.chord_list[i] + 'b', chord, re.I) :
			position = position - 1
			modif = chord[len(self.chord_list[i]) + 1:]

		#print("Position : ", position)

		if position > 0 :
			while position >= self.distance[i] :
				position = position - self.distance[i]
				i += 1
				if i >= len(self.chord_list) : i = 0
		else :
			while position <= -self.distance[i-1] :
				position = position + self.distance[i-1]
				i -= 1
				if i <= 0 : i = len(self.chord_list)-1
		#print("New chord i : ", i)

		newchord = self.chord_list[i]
		if position == 1 :
			newchord = newchord + '#' + modif
		elif position == -1 :
			newchord = newchord + 'b' + modif
		else :
			newchord = newchord + modif

		return newchord

class LaTexOutputFormat :
	def __init__(self, interline, columns, fname) :
		self.in_block = False
		self.filename = fname
		self.interline = interline
		self.columns = columns
		self.of = codecs.open(fname, "w", "utf-8")

	def print_header(self) :
		self.of.write(u'\\documentclass[' + GlobalParameters.fontsize + 'pt]{extarticle}\n')
		self.of.write(u'\\usepackage[utf8]{inputenc}\n')
		self.of.write(u'\\usepackage{setspace}\n')
		self.of.write(u'\\usepackage{gchords}\n')
		self.of.write(u'\\usepackage{multicol}\n')
		self.of.write(u'\\usepackage{color}\n')
		self.of.write(u'\\usepackage[textwidth=19cm,textheight=25cm]{geometry}\n')
		self.of.write(u'\\usepackage[T1]{fontenc}\n')
		self.of.write(u'\\usepackage{lmodern}\n')
		self.of.write(u'\\newcommand\\textchord[2]{%\n')
		self.of.write(u'\\mbox{\\begin{tabular}[b]{@{}l@{}}\\textbf{\\tt\\small\\color{blue}#1~}\\\\#2\\end{tabular}}}\n')
		self.of.write(u'\\renewcommand{\\sfdefault}{lmss}\n')
		#self.of.write('\\renewcommand{\\familydefault}{\\sfdefault}\n')
		self.of.write(u'\\begin{document}\n')

	def print_title(self, t) :
		self.of.write(u'\\section*{'+ t+ '}\n')

	def start_song(self,t) :
		self.print_title(t)
		self.of.write(u'\\begin{spacing}{'+str(self.interline)+'}\n')

	def start_block(self) :
		if not self.in_block :
			self.in_block = True
			if self.columns > 1 : self.of.write(u'\\begin{multicols}{'+str(self.columns)+u'}\n')
		
	def end_block(self) :
		if self.in_block : 
			self.in_block = False
			if self.columns > 1 : self.of.write(u'\\end{multicols}\n')
		
	def start_verbatim(self) :
		self.of.write(u'\\begin{verbatim}\n')

	def end_verbatim(self) :
		self.of.write(u'\\end{verbatim}\n')

	def start_verse(self) :
		self.of.write(u'\\begin{verse}\n')

	def end_verse(self) :
		self.of.write(u'\\end{verse}\n')

	def end_song(self) :
		self.end_block()
		self.of.write(u'\\end{spacing}\n')
		self.of.write(u'\\newpage\n\n')

	def end_file(self) :
		self.of.write(u'\\end{document}\n')
		self.of.close()

	def print_chord(self, c, t) :
		if c == '' : return u'\\textchord{~}{'+t+'}'
		else : return u'\\textchord{'+c.replace('#', '\\#').replace('|','$\\vert$') +'}{'+t+'}'
		
	def print_textline(self, x) :
		self.of.write(x+u'\n')

	def print_verse(self, l) :
		self.of.write(l + u'\\\\\n')

	def bold(self, l) :
		self.of.write(u'\\textbf{'+l+u'}\n')

	def start_chord_box(self) :
		self.of.write('\\chords{')
		
	def end_chord_box(self) :
		self.of.write('}')
		
	def print_chord_box(self, cn, f, cb) :
		self.of.write(u'\\chord')
		if f > 1 :
			if f > 9 :
				self.of.write(u'{{'+str(f)+'}}')
			else :
				self.of.write(u'{'+str(f)+'}')
		else :
			self.of.write(u'{t}')
		schema = cb[0]
		for c in cb[1:] :
			if c == 'x' :
				schema = schema + ',x'
			elif c == '0' :
				schema = schema + ',o'
			else :
				schema = schema + ',p' + c

		self.of.write(u'{'+schema+'}{'+cn.replace('#', '\\#')+'}\n')

def main(argv) :
	try :
		ops, args = getopt.getopt(argv,"hi:l:c:o:f:r:")
	except getopt.GetoptError:
		print ('chordp.py [-ht:i:l:c:o:f:] inputfile')
		sys.exit(2)

	otype = 'lead'
	lang = 'en'
	interline = 1.0
	GlobalParameters.columns = 1
	outfile = "out"
	outfilename = "out.tex"

	for o, a in ops:
		if o == '-h' :
			print ('Usage : chord.py [-h,-t type,-l lang, -c cols] files')
			print (' -h		: help')
			print (' -i n	: lineskip (default = 1)')
			print (' -l lang: language (en or it, default = en)')
			print (' -c cols: number of columns (default = 2)')
			print (' -f size: font size (default = 11)')
			print (' -r rel : transpose by rel semitones (pos. or neg.)')
			exit(2)
		elif o == '-i' :
			interline = float(a)
		elif o == '-l' :
			if a != 'en' and a != 'it' :
				print ('Unsupported language: chose between en or it')
				exit(2)
			else :
				lang = a
		elif o == '-c' :
			GlobalParameters.columns = int(a)
		elif o == '-o' :
			outfile = a
		elif o == '-f' :
			if (int(a) < 8 or int(a) > 14) :
				print('Unsupported font size')
				exit(-3)
			else :
				GlobalParameters.fontsize = a
		elif o == '-r' :
			GlobalParameters.transpose = int(a)


	cp = ChordProcessor(lang)
	outfilename = outfile + ".tex"
	cp.output_format = LaTexOutputFormat(interline, GlobalParameters.columns, outfilename)

	cp.output_format.print_header()

	for fname in args :
		if os.path.isdir(fname) :
			for x in os.listdir(fname) :
				args.append(os.path.join(fname, x))
			continue
		with codecs.open(fname, "rU", encoding='utf-8') as f:
			lines = f.readlines()
			cp.process_song(lines)

	cp.output_format.end_file()

	subprocess.run(["pdflatex", "-jobname="+outfile, outfilename], shell=True, check=True)

	os.remove(outfilename)
	os.remove(outfile + ".aux")
	os.remove(outfile + ".log")

if __name__ == '__main__' :
	main(sys.argv[1:])


