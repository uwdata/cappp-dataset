#!/usr/bin/env python

INPUT_FOLDER = 'raw-pages'
OUTPUT_FOLDER = 'clean-pages'

HTML_HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html><head><title>untitled</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
<div style="page-break-before:always; page-break-after:always"><div>"""

HTML_FOOTER = """</div></div>
</body></html>"""

REPLACEMENTS = {
	"&#63043;" : "0",
	"&#63044;" : "1",
	"&#63045;" : "2",
	"&#63046;" : "3",
	"&#63047;" : "4",
	"&#63048;" : "5",
	"&#63049;" : "6",
	"&#63050;" : "7",
	"&#63051;" : "8",
	"&#63052;" : "9",
	"&#8220;" : "``",
	"&#8221;" : "''",
	"&#8217;" : "'",
	"&#63059;" : "$",
	"&#63042;" : "%",
	"&#8212;" : "---",
	"&#8226;" : "*"
}

##==-----------------------------------------------------------------------==##

import glob
import re

def readHtml( path ):
	with open( path, 'r' ) as f:
		content = f.read().decode( 'utf-8' )
	return content

def writeHtml( path, content ):
	with open( path, 'w' ) as f:
		f.write( content.encode( 'utf-8' ) )

##==-----------------------------------------------------------------------==##

# Document-specific cleanup
print "Cleaning up all extracted pages..."

# Loop through all pages
paths = glob.glob( '{}/*.html'.format(INPUT_FOLDER) )
for path in paths :
	
	# Read from disk
	filename = path[len(INPUT_FOLDER)+1:]
	content = readHtml( path )
	print "    Processing {}".format( filename )

	# Remove HTML header and footer
	assert content[:len(HTML_HEADER)] == HTML_HEADER
	assert content[-len(HTML_FOOTER):] == HTML_FOOTER
	content = content[len(HTML_HEADER):-len(HTML_FOOTER)]
	
	# Replace numbers
	for before_text, after_text in REPLACEMENTS.iteritems():
		content = re.sub( before_text, after_text, content )
	
	# Write to disk
	writeHtml( '{}/{}'.format(OUTPUT_FOLDER,filename), content )

