#!/usr/bin/python
import unittest
import chordp

class TestChordProcessor(unittest.TestCase) :
    
    def test_basic(self) :
        ch = chordp.ChordProcessor('en')
        self.assertTrue(ch.is_a_chord('F'))
        self.assertTrue(ch.is_a_chord('Fmaj7'))
        self.assertTrue(ch.is_a_chord('Fm'))
        self.assertTrue(ch.is_a_chord('F7'))
        self.assertTrue(ch.is_a_chord('G9'))
        self.assertTrue(ch.is_a_chord('A7/4'))
        self.assertTrue(ch.is_a_chord('F/A'))
        self.assertTrue(ch.is_a_chord('A7/4'))

    def test_ch_index_en(self) :
        ch = chordp.ChordProcessor('en')
        n, r = ch.get_chord_number('F')
        self.assertTrue(n == 5)
        n, r = ch.get_chord_number('F#')
        self.assertTrue(n == 6)
        n, r = ch.get_chord_number('Gb')
        self.assertTrue(n == 6)
        n, r = ch.get_chord_number('Fb')
        self.assertTrue(n == 4)
        n, r = ch.get_chord_number('E#')
        self.assertTrue(n == 5)
        n, r = ch.get_chord_number('B#')
        self.assertTrue(n == 0)
        n, r = ch.get_chord_number('Cb')
        self.assertTrue(n == 11)

    def test_ch_index_it(self) :
        ch = chordp.ChordProcessor('it')
        n, r = ch.get_chord_number('FA')
        self.assertTrue(n == 5)
        n, r = ch.get_chord_number('FA#')
        self.assertTrue(n == 6)
        n, r = ch.get_chord_number('SOLb')
        self.assertTrue(n == 6)
        n, r = ch.get_chord_number('FAb')
        self.assertTrue(n == 4)
        n, r = ch.get_chord_number('MI#')
        self.assertTrue(n == 5)
        n, r = ch.get_chord_number('SI#')
        self.assertTrue(n == 0)
        n, r = ch.get_chord_number('DOb')
        self.assertTrue(n == 11)

    def test_transpose_en(self) :
        ch = chordp.ChordProcessor('en')
        self.assertTrue(ch.transpose('C', 2) == 'D')
        self.assertTrue(ch.transpose('C#', 2) == 'D#')
        self.assertTrue(ch.transpose('E', 1) == 'F')
        self.assertTrue(ch.transpose('F', -1) == 'E')
        self.assertTrue(ch.transpose('F', -2) == 'D#')
        self.assertTrue(ch.transpose('C', -2) == 'A#')
        self.assertTrue(ch.transpose('C', -2, False) == 'Bb')
        self.assertTrue(ch.transpose('D', 4, False) == 'Gb')
        self.assertTrue(ch.transpose('D', 3, False) == 'F')
        self.assertTrue(ch.transpose('D', 2, False) == 'E')
        self.assertTrue(ch.transpose('C', 9) == 'A')

 

if __name__ == '__main__' :
    unittest.main()

