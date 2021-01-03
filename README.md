## Chord Processor (Chordp)

---
Author: Giuseppe Lipari
Email : giulipari@gmail.com
---

Python script for processing text files containing song lyrics and chords. 
It produces a LaTeX file as an intermediate step towards a nice pdf file.

This is still in alpha, lot of work is needed before a clean script. 

# Documentation 

## Chords

- The first line of a text file is the title of the song (and of the section)

- After the first line, you can put local options. 

- Local options: 
  - transpose: rel 

    Transpose the song by rel semitones (up if positive, down if negative). 
	This is the same as the command line option, but only local to this song.

  - columns: c

	Write the song on c columns. This option overrides the global option. 
	Please notice that tablatures always go on a single column. 

  
- The end of the local option is marked by a line starting with at least three dashes 
  '---'. The rest of the line is ignored. 

- A line containing only chords is visualized in bold / blue color

- If the line following the chords is a verse line, the chords will 
  be aligned to the words at the correct position. 
  
- If the line following the chords is completely empty, the chords will 
  not be displayed. Please add at least a character (for example a .)

- You can write tablatures. They will be visualised as verbatim. To do so, 
  you need to enclose the tablature within two text lines starting with 
  [tab] and [/].


## Characters

Please, make sure your text file is encoded into UTF-8. 

Opening and closing brackets [] are not allowed in the verse, because latex  
could interpret them as special macro characters (for optional parameters). 
Please, use them only to denote special commands like :

- [tab] ... [/]
- [Chorus], [Intro], [Verse], etc. (these will be shown in special form)

The interpret expects them to be alone on a single line.  

Similarly, braces {} are not allowed, use parenthesis instead. 
  
## Command line 

TBD. 


