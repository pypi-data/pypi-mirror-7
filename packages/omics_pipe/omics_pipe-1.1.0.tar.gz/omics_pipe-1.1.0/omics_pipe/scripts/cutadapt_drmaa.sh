#!/bin/bash
set -x

#Source modules for current shell
source $MODULESHOME/init/bash

#Loads specified python addons module for cutadapt
module load python-addons

#Make assemblies output director if it doesn't exist
mkdir -p $3

#Runs cutadapt with $1=SAMPLE, $2=RAW_DATA_DIR, $3=ADAPTER, $4=TRIMMED_DATA_PATH
cutadapt -a $3 $2/$1.fastq > $4/$1_trimmed.fastq

exit 0
