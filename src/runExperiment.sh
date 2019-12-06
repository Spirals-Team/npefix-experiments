#!/bin/bash

# constants 
lapse=100
epsilon=0.8
mode=mono

path_npefix="`pwd`/../npefix-0-4.jar"

# clone dataset
[ ! -d "npe-dataset" ] && git clone https://github.com/Spirals-Team/npe-dataset

for project in "sling_4982" "felix-4960" "lang-304" "lang-587" "math-290" "math-369" "math-988a" "math-988b" "math-1115" "math-1117" "pdfbox_2812" "pdfbox_2965" "pdfbox_2995"
do

echo "Repair bug: $project"
cd npe-dataset/${project}
export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true; mvn -Dhttps.protocols=TLSv1.2 test -DskipTests;
mvn dependency:resolve -q > /dev/null 2> /dev/null
cd ../..

clean_project="`echo ${project} | sed "s@_@@" | sed "s@-@@"`"

java -jar $path_npefix \
	--project ${clean_project}\
	--laps ${lapse} \
	--epsilon ${epsilon} \
	--seed 10 \
	--working /tmp/npefix/ \
	--output results/current \
	--npedataset npe-dataset \
	--mode ${mode}
# java -jar $path_npefix \
# 	--project ${clean_project}\
# 	--laps ${lapse} \
# 	--epsilon ${epsilon} \
# 	--seed 10 \
# 	--working /tmp/npefix/ \
# 	--output results/current \
# 	--npedataset npe-dataset \
# 	--mode Template
done

ls results/current
python src/generateResultsTable.py