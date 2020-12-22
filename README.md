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
	
- The end of the local option is marked by a line starting with at least three dashes 
  '---'. The rest of the line is ignored. 

- A line containing only chords is visualized in bold / blue color

- If the line following the chords is a verse line, the chords will 
  be aligned to the words at the correct position. 
  This feature does not work correctly if the chords are "too close" to each other. 
  Please add some fake space to your text by using the tilde ~ or some other 
  character.   

- You can write tablatures. They will be visualised as verbatim. To do so, 
  you need to enclose the tablature within two text lines starting with 
  [tab] and [/].


## Command line 

TBD. 


