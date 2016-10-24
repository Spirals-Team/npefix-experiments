#!/bin/bash

# constants 
lapse=100
epsilon=0.8
mode=mono

# clone dataset
git clone https://github.com/Spirals-Team/npe-dataset

# clone npefix
git clone https://github.com/Spirals-Team/npefix
cd npefix
mvn package -Dmaven.test.skip=true -q
cd ../

for project in "sling_4982" "felix-4960" "lang-304" "lang-587" "math-290" "math-369" "math-988a" "math-988b" "math-1115" "math-1117" "pdfbox_2812" "pdfbox_2965" "pdfbox_2995"
do

cd npe-dataset/${project}
mvn dependency:resolve -q > /dev/null 2> /dev/null
cd ../..

clean_project="`echo ${project} | sed "s@_@@" | sed "s@-@@"`"

java -jar npefix/target/npefix-0.4-SNAPSHOT-jar-with-dependencies.jar \
	--project ${clean_project}\
	--laps ${lapse} \
	--epsilon ${epsilon} \
	--seed 10 \
	--working /tmp/npefix/ \
	--output results/current \
	--npedataset npe-dataset \
	--mode ${mode}

java -jar npefix/target/npefix-0.4-SNAPSHOT-jar-with-dependencies.jar \
	--project ${clean_project}\
	--laps ${lapse} \
	--epsilon ${epsilon} \
	--seed 10 \
	--working /tmp/npefix/ \
	--output results/current \
	--npedataset npe-dataset \
	--mode Template

done

ls results/current
python src/generateResultsTable.py