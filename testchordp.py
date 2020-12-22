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

	# def test_ch_index_en(self) :
		# ch = chordp.ChordProcessor('en')
		# n, r = ch.get_chord_number('F')
		# self.assertTrue(n == 5)
		# n, r = ch.get_chord_number('F#')
		# self.assertTrue(n == 6)
		# n, r = ch.get_chord_number('Gb')
		# self.assertTrue(n == 6)
		# n, r = ch.get_chord_number('Fb')
		# self.assertTrue(n == 4)
		# n, r = ch.get_chord_number('E#')
		# self.assertTrue(n == 5)
		# n, r = ch.get_chord_number('B#')
		# self.assertTrue(n == 0)
		# n, r = ch.get_chord_number('Cb')
		# self.assertTrue(n == 11)

	# def test_ch_index_it(self) :
		# ch = chordp.ChordProcessor('it')
		# n, r = ch.get_chord_number('FA')
		# self.assertTrue(n == 5)
		# n, r = ch.get_chord_number('FA#')
		# self.assertTrue(n == 6)
		# n, r = ch.get_chord_number('SOLb')
		# self.assertTrue(n == 6)
		# n, r = ch.get_chord_number('FAb')
		# self.assertTrue(n == 4)
		# n, r = ch.get_chord_number('MI#')
		# self.assertTrue(n == 5)
		# n, r = ch.get_chord_number('SI#')
		# self.assertTrue(n == 0)
		# n, r = ch.get_chord_number('DOb')
		# self.assertTrue(n == 11)

	def test_transpose_en(self) :
		ch = chordp.ChordProcessor('en')
		self.assertTrue(ch.transpose('C', 2) == 'D')
		self.assertTrue(ch.transpose('C#', 2) == 'D#')
		self.assertTrue(ch.transpose('E', 1) == 'F')
		self.assertTrue(ch.transpose('F', -1) == 'E')
		self.assertTrue(ch.transpose('F', -2) == 'Eb')
		self.assertTrue(ch.transpose('C', -2) == 'Bb')
		self.assertTrue(ch.transpose('D', 4) == 'F#')
		self.assertTrue(ch.transpose('D', 3) == 'F')
		self.assertTrue(ch.transpose('D', 2) == 'E')
		self.assertTrue(ch.transpose('C', 9) == 'A')
		self.assertTrue(ch.transpose('C#m7', 9) == 'A#m7') 

	def test_transpose_it(self) :
		ch = chordp.ChordProcessor('it')
		self.assertTrue(ch.transpose('Do', 2) == 'RE')
		self.assertTrue(ch.transpose('DO#', 2) == 'RE#')
		self.assertTrue(ch.transpose('Mi', 1) == 'FA')
		self.assertTrue(ch.transpose('Fa', -1) == 'MI')
		self.assertTrue(ch.transpose('FA', -2) == 'MIb')
		self.assertTrue(ch.transpose('Do', -2) == 'SIb')
		self.assertTrue(ch.transpose('DO', 6) == 'FA#')
		self.assertTrue(ch.transpose('RE', 3) == 'FA')
		self.assertTrue(ch.transpose('RE', 2) == 'MI')
		self.assertTrue(ch.transpose('DO', 9) == 'LA')
		self.assertTrue(ch.transpose('DO#m7', 9) == 'LA#m7') 

		
if __name__ == '__main__' :
	unittest.main()

