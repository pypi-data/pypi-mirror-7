#!/bin/bash
set -x

#Source modules for current shell
source $MODULESHOME/init/bash

#Make assemblies output director if it doesn't exist
mkdir -p $2

#Move tmp dir to scratch 
export TMPDIR=$6  #TEMP_DIR
 
#Load specified module versions
module load python
module load rseqc/$5
module load picard/$8

####INPUTS: $1: STAR_RESULTS $2 QC_PATH $3 BAM_FILE_NAME $4 RSEQC_REF $5 RSEQC_VERSION $6 TMP_DIR $7 SAMPLE $8 PICARD_VERSION


java -jar `which CollectRnaSeqMetrics.jar` REF_FLAT=$4 STRAND_SPECIFICITY=NONE INPUT=$1/$7/$3 OUTPUT=rnaseqmetrics &

java -jar `which CollectInsertSizeMetrics.jar` HISTOGRAM_FILE=$2/$7/insertSizeHist.pdf INPUT= $1/$7/$3 OUTPUT=$2/$7/insertSize.txt &

wait

exit 0