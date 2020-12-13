#!/usr/bin/python
import re
import sys, getopt
import codecs
import subprocess

class GlobalParameters :
	fontsize = "11"


class ChordProcessor :
	def __init__(self, type = 'en') :
		self.output_format = None
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
		cadd = '(sus4|sus2|4|5|6|7|9|11|13)'
		caddf = cadd + '?'
		clast = '(/('+chlist+cdies+'|'+cadd+'))?'

		self.regex_chord_en = chlist + cdies + cmode + caddf + clast
		#print self.regex_chord_en
		self.pattern_en = re.compile(self.regex_chord_en)
		return


	# If the patterns matches
	def is_a_chord(self, str) :
		m = self.pattern_en.match(str)
		if m :
			return m.group() == str
		else :
			return False


	# If the line "str" is composed entirely of chords, then it
	# returns a list of pairs (chord, position), otherwise it returns None
	# @todo add the possibility to add more symbols, like repetitions, etc.
	def chord_line(self, str) :
		words = str.split()
		last_pos = 0
		cs = []
		for w in words :
			if self.is_a_chord(w) :
				new_pos = str.find(w, last_pos)
				if new_pos < last_pos :
					new_pos = last_pos + len(w)
				pair = w, new_pos
				cs.append(pair)
				last_pos = new_pos
			else :
				return None

		return cs


	def process_song(self,lines) :
		# search title
		self.output_format.start_song(lines[0])

		in_verse = 0;
		x = 1  # index of first line

		while not lines[x].startswith('---') :
			self.output_format.print_textline(lines[x])
			x = x + 1

		x = x + 1
		chord_sequence = None

		for l in lines[x:] :
			l = l[:-1]  # remove \n
			if l.strip() == '' :    # an empty line ends the verse
				if in_verse > 0:
					self.output_format.end_verse()
					in_verse = 0
					chord_sequence = None
				else :
					continue
			elif chord_sequence != None :   # a verse with a chord sequence on top
				# mix chords with words
				final = u''
				q = 0
				for c, p in chord_sequence :  #c: chord, p:position
					if p >= len(l) :                        # the position is beyond the lenght of the verse
						if q < len(l) :                     # and the previos position was within the verse
							# put the chord at the end
							final = final + l[q:] + ' ' + self.output_format.get_formatted_chord(c)
						else :
							# put some extra space in it
							final = final + ' ' + self.output_format.get_space(4) + self.output_format.get_formatted_chord(c)
						q = p
					else :
						final = final + l[q:p] + self.output_format.get_formatted_chord(c)
						q = p

				if q < len(l) : final = final + l[q:]
				self.output_format.print_verse(final)
				in_verse = in_verse + 1
				chord_sequence = None
			else :
				# I should find the chords here
				if in_verse == 0:
					in_verse = 1
					self.output_format.start_verse()
				chord_sequence = self.chord_line(l)
				if chord_sequence == None :
					self.output_format.print_verse(l)

		if in_verse > 0 :
			self.output_format.end_verse()
		self.output_format.end_song()


class LaTexOutputFormat :
	def __init__(self, inter, columns, fname) :
		self.filename = fname
		self.interline = inter
		self.columns = columns
		self.of = open(fname, "w")

	def print_header(self) :
		self.of.write('\\documentclass{article}\n')
		self.of.write('\\usepackage[chorded]{songs}\n')
		self.of.write('\\usepackage[textwidth=17cm,textheight=20cm]{geometry}\n')
		self.of.write('\\usepackage{tikz}\n')
		self.of.write('\\usepackage[utf8]{inputenc}\n')
		self.of.write('\\renewcommand{\\printchord}[1]{\\rmfamily\\bf#1}\n')
		self.of.write('\\noversenumbers\n')
		self.of.write('\\songcolumns{'+str(self.columns)+'}\n')
		self.of.write('\\begin{document}\n')

	def start_song(self,t) :
		self.of.write('\\begin{song}{' + t[0:-1] +'}\n')

	def start_verse(self) :
		self.of.write('\\begin{verse}\n')

	def end_verse(self) :
		self.of.write('\\end{verse}\n')

	def end_song(self) :
		self.of.write('\\end{song}\n')

	def end_file(self) :
		self.of.write('\\end{document}\n')
		self.of.close()

	def get_formatted_chord(self, c) :
		return '\\['+c+']'

	def print_textline(self,x) :
		self.of.write(x+'\n')

	def print_verse(self, l) :
		self.of.write(l+'\n')


class LeadsheetOutputFormat :
	def __init__(self, interline, columns, fname) :
		self.filename = fname
		self.interline = interline
		self.columns = columns
		self.of = open(fname, "w")

	def print_header(self) :
		self.of.write('\\documentclass[' + GlobalParameters.fontsize + ']{article}\n')
		self.of.write('\\usepackage{setspace}\n')
		self.of.write('\\usepackage{multicol}\n')
		self.of.write('\\usepackage{color}\n')
		self.of.write('\\usepackage[textwidth=18cm,textheight=22cm]{geometry}\n')
		self.of.write('\\newcommand\\chord[2][l]{%\n')
		self.of.write('\\makebox[0pt][#1]{\\begin{tabular}[b]{@{}l@{}}\\textbf{\color{blue}#2}\\\\\\mbox{}\\end{tabular}}}\n')
		self.of.write('\\renewcommand{\\familydefault}{\\sfdefault}\n')
		self.of.write('\\begin{document}\n')

	def print_title(self, t) :
		self.of.write('\\section*{'+ t+ '}\n')

	def start_song(self,t) :
		self.print_title(t)
		if self.columns > 1 : self.of.write('\\begin{multicols}{'+str(self.columns)+'}\n')
		self.of.write('\\begin{spacing}{'+str(self.interline)+'}\n')


	def start_verse(self) :
		self.of.write('\\begin{verse}\n')

	def end_verse(self) :
		self.of.write('\\end{verse}\n')

	def end_song(self) :
		self.of.write('\\end{spacing}\n')
		if self.columns > 1 : self.of.write('\\end{multicols}\n')
		self.of.write('\\newpage\n\n')

	def end_file(self) :
		self.of.write('\\end{document}\n')
		self.of.close()

	def get_formatted_chord(self, c) :
		return '\\chord{'+c.replace('#','\\#')+'}'

	def get_space(self,x) :
		return '\\hspace{'+str(12*x)+'pt}\n'

	def print_textline(self,x) :
		self.of.write(x)

	def print_verse(self, l) :
		self.of.write(l + '\\\\\n')


class OrgOutputFormat :
	def __init__(self, inter, columns, fname) :
		self.filename = fname
		self.interline = inter
		self.columns = columns
		self.of = open(fname, "w")

	def print_header(self) :
		self.of.write('#+OPTIONS: toc:nil num:nil\n')
		self.of.write('#+LaTeX_CLASS_OPTIONS: [11pt,a4paper]\n')
		self.of.write("#+LATEX_HEADER: \\usepackage{setspace}\n")
		self.of.write('#+LATEX_HEADER: \\usepackage{multicol}\n')
		self.of.write('#+LATEX_HEADER: \\usepackage[textwidth=18cm,textheight=22cm]{geometry}\n')
		self.of.write('\n')


	def print_title(self,t) :
		self.of.write('* ' + t)

	def start_song(self,t) :
		self.print_title(t)
		self.of.write('#+BEGIN_EXPORT latex\n')
		if self.columns > 1 : self.of.write('\\begin{multicols}{'+str(self.columns)+'}\n')
		self.of.write('\\sffamily\n')
		self.of.write('\\begin{spacing}{'+str(self.interline)+'}\n')
		self.of.write('#+END_EXPORT\n')


	def end_song(self) :
		self.of.write('#+BEGIN_EXPORT latex\n')
		self.of.write('\\end{spacing}\n')
		if self.columns > 1 : self.of.write('\\end{multicols}\n')
		self.of.write('\\newpage\n')
		self.of.write('#+END_EXPORT\n')


	def start_verse(self) :
		# self.of.write('#+LaTeX: \\begin{spacing}{1.5}'
		self.of.write('#+BEGIN_VERSE\n')
		return


	def end_verse(self) :
		self.of.write('#+END_VERSE\n')
		# print '#+LaTeX: \\end{spacing}'


	def end_file(self) :
		self.of.close()
		return


	def get_formatted_chord(self, c) :
		return '\\textbf{[' + c.replace('#','\\#') + ']}'

	def print_textline(self,x) :
		self.of.write(x+'\n')

	def print_verse(self,x) :
		self.of.write(x+'\n')



def main(argv) :
	try :
		ops, args = getopt.getopt(argv,"ht:i:l:c:o:f:")
	except getopt.GetoptError:
		print ('chordp.py [-ht:i:l:c:o:f:] inputfile')
		sys.exit(2)

	otype = 'lead'
	lang = 'en'
	interline = 1.0
	columns = 2
	outfile = "out"
	outfilename = "out.tex"

	for o, a in ops:
		if o == '-t' :
			if a != 'org' and a != 'song' and a != 'lead' :
				print ('type can be "org" or "song" or "lead"')
				exit(2)
			else :
				otype = a
		elif o == '-h' :
			print ('Usage : chord.py [-h,-t type,-l lang, -c cols] files')
			print (' -h     : help')
			print (' -t type: type of output (org, song, lead)')
			print (' -i n   : lineskip (default = 1)')
			print (' -l lang: language (en or it, default = en)')
			print (' -c cols: number of columns (default = 2)')
			print (' -f size: font size (default = 11)')
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
			columns = int(a)
		elif o == '-o' :
			outfile = a
		elif o == '-f' :
			if (int(a) < 10 or int(a) > 14) :
				print('Unsupported font size')
				exit(-3)
			else :
				GlobalParameters.fontsize = a


	cp = ChordProcessor(lang)
	if otype == 'org' :
		outfilename = outfile + ".org"
		cp.output_format = OrgOutputFormat(interline, columns, outfilename)
	elif otype == 'song' :
		outfilename = outfile + ".tex"
		cp.output_format = LaTexOutputFormat(interline, columns, outfilename)
	else :
		outfilename = outfile + ".tex"
		cp.output_format = LeadsheetOutputFormat(interline, columns, outfilename)

	cp.output_format.print_header()

	for fname in args :
		with codecs.open(fname, "rU", encoding='utf-8') as f:
			lines = f.readlines()
			cp.process_song(lines)

	cp.output_format.end_file()

	if otype == 'song' or otype == 'lead' :
		subprocess.call(["pdflatex", "-jobname="+outfile, outfilename])

if __name__ == '__main__' :
	main(sys.argv[1:])


