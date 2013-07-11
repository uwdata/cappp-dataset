#!/bin/bash

OUTPUT=raw-pages
TOTAL_PAGES=662

echo "Extracting individual papges from PDF..."

if [ ! -d $OUTPUT ]
then
    echo "    Making directory: $OUTPUT"
	mkdir $OUTPUT
fi

for (( PAGE=1; PAGE<=$TOTAL_PAGES; PAGE++ ))
do
	echo "    Extracting page $PAGE..."
	java -jar pdfbox-app-1.8.2.jar ExtractText -html -encoding utf-8 -startPage $PAGE -endPage $PAGE fcic_final_report_full.pdf $OUTPUT/fcic_final_report_full--$PAGE.html
done
