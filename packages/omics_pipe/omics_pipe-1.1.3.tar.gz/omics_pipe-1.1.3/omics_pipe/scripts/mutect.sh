#!/bin/bash
set -x

#Source modules for current shell
source $MODULESHOME/init/bash

#Move tmp dir to scratch 
export TMPDIR=$3  #TEMP_DIR

#Loads specified module versions
module load mutect/$4


####INPUTS: $1: BWA_RESULTS $2 SAMPLE $3: TEMP_DIR $4 MUTECT_VERSION $5 GENOME $6 DBSNP $7 COSMIC $8 MUTECT_INTERVALS_BAM $9 MUTECT_RESULTS


`which GenomeAnalysisTK.jar` 
java -Xmx2g -jar `which muTect.jar`
--analysis_type MuTect
--reference_sequence $5
--cosmic $7
--dbsnp $6
--intervals $8
--input_file:normal $1/$2/$2_normal.bam
--input_file:tumor $1/$2/$2_tumor.bam
--out $9/$2/call_stats.txt
--coverage_file $9/$2/coverage.wig.txt

exit 0