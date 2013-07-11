#!/usr/bin/env python

INPUT_FOLDER = 'clean-pages'
OUTPUT_FOLDER = '.'
WORKING_FOLDER = 'hyphenation'
UNIGRAM_FOLDER = 'google-unigrams'
BIGRAM_FOLDER = 'google-bigrams'
TOTAL_PAGES = 662

##==-----------------------------------------------------------------------==##

import re
import argparse

def readParagraphs():
	paragraph_regex = r"<p>([^<]*)</p>"
	paragraphs = []
	for page in range(1,TOTAL_PAGES+1):
		filename = "{}/fcic_final_report_full--{}.html".format(INPUT_FOLDER,page)
		with open( filename, 'r' ) as f:
			content = f.read().decode( 'utf-8' )
		paragraphs += re.findall( paragraph_regex, content )
	return paragraphs

def splitParagraph( paragraph ):
	lines = re.split( r"[\n\r]+", paragraph )
	lines = [ line.strip() for line in lines ]
	return lines

def splitLine( line ):
	# Skip empty lines
	if len(line) == 0:
		return None
	
	line = re.sub( "---", " ", line )
	isHyphenated = ( line[-1] == "-" )
	words = re.findall( r"\w+", line )
	
	# Skip lines without a word
	if len(words) == 0:
		return None
	
	if isHyphenated:
		words[-1] = words[-1] + "-"
	return words

def writeCandidates( candidates ):
	with open( "{}/candidates.txt".format(WORKING_FOLDER), 'w' ) as f:
		for candidate in candidates:
			f.write( u"{}\t{}\n".format( candidate[0], candidate[1] ).encode( 'utf-8' ) )

def readCandidates():
	with open( "{}/candidates.txt".format(WORKING_FOLDER), 'r' ) as f:
		candidates = f.read().decode( 'utf-8' ).splitlines()
		candidates = [ candidate.split( '\t' ) for candidate in candidates ]
	return candidates

def writeCandidatesAndFreqs( candidates, unigramCounts, bigramCounts ):
	with open( "{}/candidates-freqs.txt".format(WORKING_FOLDER), 'w' ) as f:
		for candidate in candidates:
			unigram = "{}{}".format( candidate[0][:-1], candidate[1] )
			bigram = "{} {}".format( candidate[0][:-1], candidate[1] )
			unigramCount = 0
			bigramCount = 0
			if unigram in unigramCounts:
				unigramCount = unigramCounts[ unigram ]
			if bigram in bigramCounts:
				bigramCount = bigramCounts[ bigram ]
			f.write( u"{}\t{}\t{}\t{}\n".format( candidate[0], candidate[1], unigramCount, bigramCount ).encode( 'utf-8' ) )

def readCandidatesAndFreqs():
	with open( "{}/candidates-freqs.txt".format(WORKING_FOLDER), 'r' ) as f:
		candidates = f.read().decode( 'utf-8' ).splitlines()
		candidates = [ candidate.split( '\t' ) for candidate in candidates ]
		candidatesAndFreqs = { "{}{}".format( candidate[0], candidate[1] ) : { 'unigramCount' : int(candidate[2]), 'bigramCount' : int(candidate[3]) } for candidate in candidates }
	return candidatesAndFreqs

def scanUnigrams( vocab ):
	dictionary = {}
	with open( '{}/1gm-0000'.format(UNIGRAM_FOLDER), 'r' ) as f:
		print '    Scanning 1gm-0000...'
		for line in f.read().decode( 'utf-8' ).splitlines():
			if line.find( '\t' ) >= 0:
				word, freq = line.split( '\t' )
				if word in vocab:
					dictionary[ word ] = freq
	return dictionary

def scanBigrams( vocab ):
	dictionary = {}
	for n in range(0, 32):
		with open( '{}/2gm-{:04d}'.format(BIGRAM_FOLDER,n), 'r' ) as f:
			print '    Scanning 2gm-{:04d}...'.format(n)
			for line in f.read().decode( 'utf-8' ).splitlines():
				if line.find( '\t' ) >= 0:
					word, freq = line.split( '\t' )
					if word in vocab:
						dictionary[ word ] = freq
	return dictionary

##==-----------------------------------------------------------------------==##

def dehyphendateStepOne():
	print "[Step 1 of 3]"
	
	# All hyphenation candidates
	candidates = []
	
	# Split document into paragraphs
	paragraphs = readParagraphs()
	print "Processing {} paragraphs...".format( len(paragraphs) )
	for paragraph in paragraphs:
		
		# All words in the paragraphs
		words = []
		
		# Process each line of the paragraph
		lines = splitParagraph( paragraph )
		for line in lines:
			
			# Split lines into words
			w = splitLine( line )
			if w is None:
				continue
			words += w
		
		# Examine pairs of words
		firstWord = None
		for secondWord in words:
			if firstWord is not None:
				# Check for words hyphenated across consecutive lines
				if firstWord[-1] == "-":
					candidates.append( [ firstWord, secondWord ] )
				# Check for words where the previous word ends in '-fi'
				if len(firstWord) >= 2:
					if firstWord[-2:] == "fi":
						candidates.append( [ firstWord, secondWord ] )
			firstWord = secondWord
	
	print "    Candidate terms: {}".format( len(candidates) )
	writeCandidates( candidates )

##==-----------------------------------------------------------------------==##

def dehyphendateStepTwo():
	print "[Step 2 of 3]"
	
	candidates = readCandidates()
	print "    Candidate terms: {}".format( len(candidates) )
	
	unigrams = [ "{}{}".format( A[:-1], B ) for A, B in candidates ]
	bigrams = [ "{} {}".format( A[:-1], B ) for A, B in candidates ]
	unigrams = frozenset( unigrams )
	bigrams = frozenset( bigrams )
	unigramCounts = scanUnigrams( unigrams )
	bigramCounts = scanBigrams( bigrams )
	
	writeCandidatesAndFreqs( candidates, unigramCounts, bigramCounts )

##==-----------------------------------------------------------------------==##

def dehyphendateStepThree():
	
	def preferUnigram( firstWord, secondWord ):
		key = "{}{}".format( firstWord, secondWord )
		unigramCount = candidatesAndFreqs[ key ][ "unigramCount" ]
		bigramCount = candidatesAndFreqs[ key ][ "bigramCount" ]
		if unigramCount > bigramCount:
			return True
		elif unigramCount < bigramCount:
			return False
		else:
			# Second word starts with a captial letter
			if re.search( '[A-Z]', secondWord ) is not None:
				return False
			else:
				return True

	def mergeWords( firstWord, secondWord ):

		# Check for words hyphenated across consecutive lines
		if firstWord[-1] == "-":
			original = "{} {}".format( firstWord[:-1], secondWord )
			if preferUnigram( firstWord, secondWord ):
				unigram = "{}{}".format( firstWord[:-1], secondWord )
				print "    {:20s} : {:20s} {:20s}".format( original, unigram, "--" )
				return unigram
			else:
				print "    {:20s} : {:20s} {:20s}".format( original, "--", "{}{}".format( firstWord, secondWord ) )
				
		# Check for words where the previous word ends in '-fi'
		if len(firstWord) >= 2:
			if firstWord[-2:] == "fi" and firstWord != "Cioffi":
				original = "{} {}".format( firstWord, secondWord )
				if preferUnigram( firstWord, secondWord ):
					unigram = "{}{}".format( firstWord, secondWord )
					print "    {:20s} : {:20s} {:20s}".format( original, unigram, "--" )
					return unigram
				else:
					print "    {:20s} : {:20s} {:20s}".format( original, "--", "{}{}".format( firstWord, secondWord ) )
					
		return None
	
	document = []
	candidatesAndFreqs = readCandidatesAndFreqs()
	
	# Split document into paragraphs
	paragraphs = readParagraphs()
	print "Processing {} paragraphs...".format( len(paragraphs) )
	for paragraph in paragraphs:
		
		# All words in the paragraphs
		words = []
		
		# Process each line of the paragraph
		lines = splitParagraph( paragraph )
		for line in lines:
			
			# Split lines into words
			w = splitLine( line )
			if w is None:
				continue
			words += w
		
		# Examine pairs of words
		paragraphWords = []
		firstWord = None
		for secondWord in words:
			if firstWord is not None:
				mergedWord = mergeWords( firstWord, secondWord )
				if mergedWord is None:
					paragraphWords.append( firstWord )
					firstWord = secondWord
				else:
					paragraphWords.append( mergedWord )
					firstWord = None
			else:
				firstWord = secondWord
		if firstWord is not None:
			paragraphWords.append( firstWord )
		
		if len(paragraphWords) == 0:
			continue
		document.append( " ".join(paragraphWords) )
	
	with open( "{}/fcic_final_report_full.txt".format(OUTPUT_FOLDER), 'w' ) as f:
		for index, paragraph in enumerate(document):
			f.write( u"p{:04d}\t{}\n".format( index+1, paragraph ) )

##==-----------------------------------------------------------------------==##

def main():
	parser = argparse.ArgumentParser( description = 'Disambiguate hyphenated words vs. linebreaks, etc.' )
	parser.add_argument( '--one',   action = 'store_true', help = 'Execute step one: Extract all candidate terms.' )
	parser.add_argument( '--two',   action = 'store_true', help = 'Execute step two: Look up candidate term freqs.' )
	parser.add_argument( '--three', action = 'store_true', help = 'Execute step three: Disambiguate.'             )
	args = parser.parse_args()
	
	# Extract all words "A-\nB", "-fi B" that need to be looked up
	if args.one:
		dehyphendateStepOne()
	
	# Extract the frequency of unigram "AB" and bigram "A B" from Google NGram Corpus
	if args.two:
		dehyphendateStepTwo()
	
	# Determine the more likely construction of "AB" vs "A-B"
	if args.three:
		dehyphendateStepThree()

if __name__ == '__main__':
	main()