.. index:: omics_pipe; parameters

====================
Omics Pipe Tutorial -- Configuring the Parameter File
====================

Before running Omics Pipe, you must configure the parameters file, 
which is a `YAML`_ document.  Example parameters files are located within 
the omics_pipe/test folder for each pipeline.  Copy one of these 
parameters files into your working directory, and edit the parameters to 
work with your sample names, directory structure, software options and software versions. 
Make sure to keep the formatting and parameter names exactly the same
as in the example parameters files. 

.. note::
	Make sure to follow the YAML format exactly. Ensure that there is only one space after each colon.
	
.. note::
	For parameters in quotes in the test parameters file, please make sure to keep them in quotes in your custom parameter file. 

The STEP parameter should be the function name of the last step in the pipeline 
that you want to run (e.g. run_tophat). To run the pre-installed pipelines all the 
way through, this should be “last_function.”  

.. warning::
	Do not change the STEPS or STEPS_DE parameters for a pre-installed pipeline.   


.. note::
	Fastq files: paired end: 2 files, “Name_1.fastq” and “Name_2.fastq” representing read 1 and read 2.  
	Have all fastq files in same raw data folder

Example Omics Pipe Parameter File
=======================

test_params.yaml in omics_pipe/tests::

	SAMPLE_LIST: [test1, test2, test3]
	
	STEP: last_function
	
	STEPS: [fastqc, star, htseq, last_function]

	RAW_DATA_DIR: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests

	FLAG_PATH: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/flags

	HTSEQ_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/counts

	LOG_PATH: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/logs

	QC_PATH: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run

	RESULTS_PATH: /gpfs/home/kfisch/test

	STAR_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/star

	WORKING_DIR: /gpfs/home/kfisch/scripts/omics_pipeline-devel/omics_pipe/scripts

	REPORT_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run

	ENDS: SE

	FASTQC_VERSION: '0.10.1'

	GENOME: /gpfs/group/databases/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/genome.fa

	HTSEQ_OPTIONS: -m intersection-nonempty -s no -t exon

	PIPE_MULTIPROCESS: 100

	PIPE_REBUILD: 'True'

	PIPE_VERBOSE: 5

	REF_GENES: /gpfs/group/databases/Homo_sapiens/UCSC/hg19/Annotation/Genes/genes.gtf

	RESULTS_EMAIL: kfisch@scripps.edu

	STAR_INDEX: /gpfs/group/databases/Homo_sapiens/UCSC/hg19/star_genome

	STAR_OPTIONS: --readFilesCommand cat --runThreadN 8 --outSAMstrandField intronMotif --outFilterIntronMotifs RemoveNoncanonical

	STAR_VERSION: '2.3.0'

	TEMP_DIR: /scratch/kfisch

	QUEUE: workq

	USERNAME: kfisch 

	DRMAA_PATH: /opt/applications/pbs-drmaa/current/gnu/lib/libdrmaa.so

	DPS_VERSION: '1.3.1111'

	BAM_FILE_NAME: Aligned.out.bam

	PARAMS_FILE: '/gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_params_RNAseq_counts.yaml'

	DESEQ_META: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/counts_meta.csv

	DESIGN: '~ condition'

	PVAL: '0.05'

	DESEQ_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/DESEQ

	SUMATRA_DB_PATH: /gpfs/home/kfisch/sumatra

	SUMATRA_RUN_NAME: test_counts_sumatra_project

	REPOSITORY: https://kfisch@bitbucket.org/sulab/omics_pipe

	HG_USERNAME: Kathleen Fisch <kfisch@scripps.edu>

	
Explanation of Variables in Omics Pipe Parameter File 
=======================
These parameters are for the RNAseq Count Based Pipeline. Parameters vary by pipeline. See examples in the tests/ folder. 

test_params.yaml in omics_pipe/tests::

	#sample names ie “Name” for paired and single end reads. So, “Name” for paired-end would expect two fastq files named “Name_1. Fastq” and Name_2.fastq”
	SAMPLE_LIST: [test1, test2, test3]	
	
	#Function to be run within pipeline. If you want to run the whole pipeline, leave this as last_function
	STEP: last_function	
	
	#All steps within the pipeline. Do not change this parameter for pre-installed pipelines. If you create your own pipeline, you will need to modify this by listing all of the steps in your pipeline. 
	STEPS: [fastqc, star, htseq, last_function]	

	#Directory where your raw .fastq files are located.
	RAW_DATA_DIR: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests	

	#Directory where you would like to have the flag files created. Flag files are empty files that indicate if a step in the pipeline has completed successfully. 
	FLAG_PATH: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/flags	

	#Directory for HTSEQ results
	HTSEQ_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/counts	

	#Directory where log files will be written
	LOG_PATH: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/logs	

	#Directory for QC results
	QC_PATH: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run	

	#Upper level results directory. Sumatra will check all subfolders of this directory for new files to add to the run tracking database. 
	RESULTS_PATH: /gpfs/home/kfisch/test	

	#Directory where STAR results will be written
	STAR_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/star	
	
	#Where omics_pipe is installed, this path will be pointing to ~/omics_pipe/scripts. 
	WORKING_DIR: /gpfs/home/kfisch/scripts/omics_pipeline-devel/omics_pipe/scripts	

	#Directory for the summary report
	REPORT_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run	

	#SE is single end, PE is paired-end sequencing reads
	ENDS: SE	

	#Version number of FASTQC
	FASTQC_VERSION: '0.10.1'	

	#Full path to Genome fasta file
	GENOME: /gpfs/group/databases/Homo_sapiens/UCSC/hg19/Sequence/WholeGenomeFasta/genome.fa	

	#Options for HTSEQ
	HTSEQ_OPTIONS: -m intersection-nonempty -s no -t exon	

	#Number of multiple processes you want Ruffus to spawn at once
	PIPE_MULTIPROCESS: 100

	#Ruffus parameter. No need to change.
	PIPE_REBUILD: 'True'		

	#Ruffus parameter. No need to change. 
	PIPE_VERBOSE: 5		

	#Full path to reference gene annotations
	REF_GENES: /gpfs/group/databases/Homo_sapiens/UCSC/hg19/Annotation/Genes/genes.gtf	

	#Your email. 
	RESULTS_EMAIL: kfisch@scripps.edu	

	#Directory pointing to STAR_INDEX (you may have to create this)
	STAR_INDEX: /gpfs/group/databases/Homo_sapiens/UCSC/hg19/star_genome	

	#Options for STAR
	STAR_OPTIONS: --readFilesCommand cat --runThreadN 8 --outSAMstrandField intronMotif --outFilterIntronMotifs RemoveNoncanonical	

	#Version number of STAR
	STAR_VERSION: '2.3.0'	

	#Path to temporary directory
	TEMP_DIR: /scratch/kfisch	

	#Name of the queue on your local cluster you wish to use
	QUEUE: workq	

	#Username for local cluster
	USERNAME: kfisch		

	#Path to your local cluster installation of DRMAA (ask your sys admin for this)
	DRMAA_PATH: /opt/applications/pbs-drmaa/current/gnu/lib/libdrmaa.so		

	#Version number of Drug Pair Seeker
	DPS_VERSION: '1.3.1111'		

	#Name of create Bam file. Will be Aligned.out.bam if you are using STAR and accepted_hits.bam if you are using TopHat
	BAM_FILE_NAME: Aligned.out.bam		

	#Full path to your parameter file. Make sure to include the single quotes. 
	PARAMS_FILE: '/gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_params_RNAseq_counts.yaml' 	

	#Location of the meta data csv file for DESEQ. See tests/counts_meta.csv for an example. 
	DESEQ_META: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/counts_meta.csv		

	#Design for DESEQ differential expression. Leave as is if you use the exact design as in the counts_meta.csv file. 
	DESIGN: '~ condition'		

	#P-value threshold
	PVAL: '0.05'		

	#Directory for DESEQ results
	DESEQ_RESULTS: /gpfs/home/kfisch/scripts/omics_pipeline-devel/tests/test_run/DESEQ		

	#Directory where you want to store your Sumatra database. Once you run this once, you do not have to change this. 
	SUMATRA_DB_PATH: /gpfs/home/kfisch/sumatra		

	#Name of your project. You do not need to change this for subsequent runs of the pipeline, but you can if you wish. 
	SUMATRA_RUN_NAME: test_counts_sumatra_project		

	#Location of omics pipe repository (you can leave this)
	REPOSITORY: https://kfisch@bitbucket.org/sulab/omics_pipe		

	#Your Mercurial username
	HG_USERNAME: Kathleen Fisch <kfisch@scripps.edu>		
	
.. _`YAML`: http://www.yaml.org/