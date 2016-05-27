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
 

if __name__ == '__main__' :
    unittest.main()

