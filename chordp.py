#!/usr/bin/python
import re
import sys, getopt
import codecs


class ChordProcessor :
    def __init__(self, type = 'en') :
        self.output_format = None
        self.type = type
        if type == 'en' :
            self.chord_list = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        else:
            self.chord_list = ['DO', 'RE', 'MI', 'FA', 'SOL', 'LA', 'SI']

        chlist = '('
        flag = True
        for c in self.chord_list :
            if not flag :
                chlist = chlist + '|'
            flag = False
            chlist = chlist+c        
        chlist = chlist + ')'

        cdies = '(#|b)?'
        cmode = '(m(aj7)?)?'
        cadd = '(4|5|6|7|9|11|13)'
        caddf = cadd + '?'
        clast = '(/('+chlist+'|'+cadd+'))?'

        self.regex_chord_en = chlist + cdies + cmode + caddf + clast
        #print self.regex_chord_en
        self.pattern_en = re.compile(self.regex_chord_en)        
        return 


    def is_a_chord(self, str) :
        m = self.pattern_en.match(str)
        if m :
            return m.group() == str 
        else :
            return False

    def get_chord_number(self, str) :
        """ 
        returns the pair (chord number, the rest of the chord)
        it may be useful for transposing chords
        """
        if self.is_a_chord(str) :
            m = self.pattern_en.match(str)
            gr = m.groups()
            # print gr
            ch_index = self.chord_list.index(gr[0])
            if ch_index < 3 : ch_index = ch_index * 2
            else : ch_index = 5 + (ch_index - 3) * 2
            # print ch_index
            if gr[1] != None :
                if gr[1] == '#' :
                    ch_index = ch_index + 1
                elif gr[1] == 'b' :
                    ch_index = ch_index - 1
                else :
                    print 'Error!!' 
                    sys.exit (-2)

            while ch_index < 0 : ch_index += 12
            while ch_index > 11 : ch_index -= 12
            rest = ''
            for x in gr[2:] :
                if x != None :
                    rest = rest + x # rest = ''.join(list(gr)[1:])
            # print rest        
            return ch_index, rest
        else :
            return None

            
    def transpose(self, chord, delta, dies = True) :
        if self.is_a_chord(chord) :
            n, r = self.get_chord_number(chord)
            n = (n + delta) % 12
            i = 0 
            d = 0

            if n < 5 : 
                i = n / 2
                d = n % 2
            else: 
                i = (n-5)/2+3
                d = (n-5) % 2

            if d == 0 :
                final = self.chord_list[i]
            else :
                if dies :
                    final = self.chord_list[i]
                    final = final + '#'
                else :
                    final = self.chord_list[(i+1)%7]
                    final = final + 'b'

            return final + r
        else :
            return None


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
            if l.strip() == '' :
                if in_verse > 0:
                    self.output_format.end_verse()
                    in_verse = 0
                    chord_sequence = None
                else :
                    continue
            elif chord_sequence != None :
                # print 'Mixing chords ', chord_sequence, ' with line ', l
                # mix chords with words
                final = u''
                q = 0
                for c, p in chord_sequence :
                    #print '%%% DEBUG %%% q =', q, ' p =', p, ' c =', c
                    if p >= len(l) :
                        if q < len(l) :
                            final = final + l[q:] + '  ' + self.output_format.get_formatted_chord(c)
                        else :
                            final = final + ' ' + self.output_format.get_formatted_chord(c)
                        q = p
                    else :
                        final = final + l[q:p] + self.output_format.get_formatted_chord(c)
                        q = p
                    #print '%%% DEBUG %%% final =', final
                if q < len(l) : final = final + l[q:]
                print final
                in_verse = in_verse + 1
                chord_sequence = None
            else :
                # I should find the chords here
                if in_verse == 0:
                    in_verse = 1
                    self.output_format.start_verse()
                chord_sequence = self.chord_line(l)
                if chord_sequence == None :
                    #print '%%% DEBUG %%% : chords not found'
                    print l
                #else :
                    #print '%%% DEBUG %%% : chords found!'

        if in_verse > 0 :
            self.output_format.end_verse()
        self.output_format.end_song()


class LaTexOutputFormat :
    def __init__(self, inter, columns) :
        self.interline = inter
        self.columns = columns

    def print_header(self) :
        print '\\documentclass{article}'
        print '\\usepackage[chorded]{songs}'
        print '\\usepackage[textwidth=17cm,textheight=20cm]{geometry}'
        print '\\usepackage{tikz}'
        print '\\usepackage[utf8]{inputenc}'
        print '\\renewcommand{\\printchord}[1]{\\rmfamily\\bf#1}'
        print '\\noversenumbers'
        print '\\begin{document}'


    def start_song(self,t) :
        print '\\begin{song}{' + t[0:-1] +'}'
        
    def start_verse(self) :
        print '\\begin{verse}'
            
    def end_verse(self) :
        print '\\end{verse}'
        
    def end_song(self) :
        print '\\end{song}'

    def end_file(self) :
        print '\\end{document}'
        
    def get_formatted_chord(self, c) :
        return '\\['+c+']'

    def print_textline(self,x) :
        print x




class OrgOutputFormat :
    def __init__(self, inter, columns) :
        self.interline = inter
        self.columns = columns

    def print_header(self) :
        print '#+OPTIONS: toc:nil num:nil'
        print '#+LaTeX_CLASS_OPTIONS: [11pt,a4paper]'
        print "#+LATEX_HEADER: \\usepackage{setspace}"
        print '#+LATEX_HEADER: \\usepackage{multicol}'
        print '#+LATEX_HEADER: \\usepackage[textwidth=18cm,textheight=22cm]{geometry}'
        print 


    def print_title(self,t) :
        print '*', t

    def start_song(self,t) :
        self.print_title(t)
        print '#+BEGIN_EXPORT latex'
        if self.columns > 1 : print '\\begin{multicols}{'+str(self.columns)+'}'
        print '\\sffamily'
        print '\\begin{spacing}{'+str(self.interline)+'}'
        print '#+END_EXPORT'


    def end_song(self) :
        print '#+BEGIN_EXPORT latex'
        print '\\end{spacing}'
        if self.columns > 1 : print '\\end{multicols}'
        print '\\newpage'
        print '#+END_EXPORT'
                

    def start_verse(self) :
        # print '#+LaTeX: \\begin{spacing}{1.5}'
        print '#+BEGIN_VERSE'
        return 


    def end_verse(self) :
        print '#+END_VERSE'
        # print '#+LaTeX: \\end{spacing}'


    def end_file(self) :
        return 


    def get_formatted_chord(self, c) :
        return '\\textbf{[' + c.replace('#','\\#') + ']}'

    def print_textline(self,x) :
        print x
        


def main(argv) :
    try :
        ops, args = getopt.getopt(argv,"ht:i:l:c:")
    except getopt.GetoptError:
        print 'chordp.py [-ht:i:l:c:] inputfile'
        sys.exit(2)
        
    otype = 'org'
    lang = 'en'
    interline = 1.0
    columns = 2

    for o, a in ops:
        if o == '-t' :
            if a != 'org' and a != 'song':
                print 'type can only be "org" or "song"'
                exit(2)
            else :
                otype = a
        elif o == '-h' :
            print 'Usage : chord.py [-h,-t type,-l lang, -c cols] files'
            print ' -h     : help'
            print ' -t type: type of output (org or song)'
            print ' -i n   : lineskip (default = 1)'
            print ' -l lang: language (en or it, default = en)'
            print ' -c cols: number of columns (default = 2)'
            exit(2)
        elif o == '-i' :
            interline = float(a)
        elif o == '-l' :
            if a != 'en' and a != 'it' : 
                print 'Unsupported language: chose between en or it' 
                exit(2)
            else :
                lang = a
        elif o == '-c' :
            columns = int(a)
        
    
    cp = ChordProcessor(lang)
    if otype == 'org' :
        cp.output_format = OrgOutputFormat(interline, columns)
    else :
        cp.output_format = LaTexOutputFormat(interline, columns)

    cp.output_format.print_header()

    for fname in args :

        with codecs.open(fname, encoding='utf-8') as f:
            lines = f.readlines()
            cp.process_song(lines)

    cp.output_format.end_file()



if __name__ == '__main__' :
    main(sys.argv[1:])


