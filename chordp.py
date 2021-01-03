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
        cadd = '(sus4|sus2|4|5|6|7(\\+)?|9|11|13)'
        caddf = cadd + '?'
        clast = '(/('+chlist+cdies+'|'+cadd+'))?'
        csep = '\\|'

        self.regex_chord_en = csep + '|' + '(' + chlist + cdies + cmode + caddf + clast + ')'
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
                #    new_pos = last_pos + len(w)
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

        in_verse = 0;
        in_tab = 0;
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

        self.output_format.columns = local_columns
        self.output_format.start_song(lines[0])

        x = x + 1
        chord_sequence = None

        self.output_format.start_block()
        
        for l in lines[x:] :
            l = l[:-1]  # remove \n

            if l.strip() == '[tab]' :
                in_tab = 1
                self.output_format.end_block()
                self.output_format.start_verbatim()
            elif l.strip() == '[/]' :
                in_tab = 0
                self.output_format.end_verbatim()
                self.output_format.start_block()
            elif in_tab > 0 :
                self.output_format.print_textline(l)
            elif l.strip() == '' :    # an empty line ends the verse
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
        self.of = open(fname, "w")

    def print_header(self) :
        self.of.write('\\documentclass[' + GlobalParameters.fontsize + 'pt]{extarticle}\n')
        self.of.write('\\usepackage{setspace}\n')
        self.of.write('\\usepackage{multicol}\n')
        self.of.write('\\usepackage{color}\n')
        self.of.write('\\usepackage[textwidth=19cm,textheight=22cm]{geometry}\n')
        self.of.write('\\usepackage[T1]{fontenc}\n')
        self.of.write('\\usepackage{lmodern}\n')
        self.of.write('\\newcommand\\textchord[2]{%\n')
        self.of.write('\\mbox{\\begin{tabular}[b]{@{}l@{}}\\textbf{\\tt\\small\\color{blue}#1~}\\\\#2\\end{tabular}}}\n')
        self.of.write('\\renewcommand{\\sfdefault}{lmss}\n')
        #self.of.write('\\renewcommand{\\familydefault}{\\sfdefault}\n')
        self.of.write('\\begin{document}\n')

    def print_title(self, t) :
        self.of.write('\\section*{'+ t+ '}\n')

    def start_song(self,t) :
        self.print_title(t)
        self.of.write('\\begin{spacing}{'+str(self.interline)+'}\n')

    def start_block(self) :
        if not self.in_block :
            self.in_block = True
            if self.columns > 1 : self.of.write('\\begin{multicols}{'+str(self.columns)+'}\n')
        
    def end_block(self) :
        if self.in_block : 
            self.in_block = False
            if self.columns > 1 : self.of.write('\\end{multicols}\n')
        
    def start_verbatim(self) :
        self.of.write('\\begin{verbatim}\n')

    def end_verbatim(self) :
        self.of.write('\\end{verbatim}\n')

    def start_verse(self) :
        self.of.write('\\begin{verse}\n')

    def end_verse(self) :
        self.of.write('\\end{verse}\n')

    def end_song(self) :
        self.end_block()
        self.of.write('\\end{spacing}\n')
        self.of.write('\\newpage\n\n')

    def end_file(self) :
        self.of.write('\\end{document}\n')
        self.of.close()

    def print_chord(self, c, t) :
        if c == '|' : return '\\textchord{$\\vert$}{'+t+'}'
        else : return '\\textchord{'+c.replace('#', '\\#')+'}{'+t+'}'
        
    def print_textline(self, x) :
        self.of.write(x+'\n')

    def print_verse(self, l) :
        self.of.write(l + '\\\\\n')



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
            print (' -h     : help')
            print (' -i n   : lineskip (default = 1)')
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
        with codecs.open(fname, "rU", encoding='utf-8') as f:
            lines = f.readlines()
            cp.process_song(lines)

    cp.output_format.end_file()

    subprocess.run(["pdflatex", "-jobname="+outfile, outfilename], shell=True, check=True)

    #os.remove(outfilename)
    os.remove(outfile + ".aux")
    os.remove(outfile + ".log")

if __name__ == '__main__' :
    main(sys.argv[1:])


