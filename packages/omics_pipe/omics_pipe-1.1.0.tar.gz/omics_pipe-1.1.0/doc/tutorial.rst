.. index:: omics_pipe; tutorial

====================
Omics Pipe Tutorial --  Installation
====================

Installation
=======

:doc:`Installation instructions <installation>`

Before Running Omics Pipe: Configuring Parameters File
=============================

.. note::
	Before running omics_pipe, you must configure the parameters file, 
	which is a YAML document.   Follow the instructions here: :doc:`Configuring the parameters file <parameter_file>`

Running Omics Pipe
===================
When you are ready to run omics pipe, simply type the command::

	omics_pipe RNAseq_count_based /path/to/parameter_file.yaml  

To run the basic RNAseq_count_based pipeline with your parameter file. Additional usage instructions below and are available by typing omics_pipe –h.::  

	omics_pipe [-h] [--custom_script_path CUSTOM_SCRIPT_PATH]
                  [--custom_script_name CUSTOM_SCRIPT_NAME]
				  [--compression {gzip, bzip}]
                  {RNAseq_Tuxedo, RNAseq_count_based, RNAseq_cancer_report, RNAseq_TCGA, RNAseq_TCGA_counts, 
				  Tumorseq_MUTECT, miRNAseq_count_based, miRNAseq_tuxedo, WES_GATK, WGS_GATK, SomaticInDels, ChIPseq_MACS, ChIPseq_HOMER,  custom} 
                  parameter_file

If your .fastq files are compressed, please use the compression option and indicate the type of compression used for your files. Currently supported compression types are gzip and bzip.  


Running Omics Pipe with the Test Data and Parameters
====================================
To run Omics Pipe with the test parameter files and data, type the commands below to run each pipeline. 

.. note::
	Replace the ~ with the path to your Omics Pipe installation. 


**RNA-seq (Tuxedo)**::

	omics_pipe RNAseq_Tuxedo ~/tests/test_params_RNAseq_Tuxedo.yaml

**RNA-seq(Anders 2013)**::

	omics_pipe RNAseq_count_based ~/tests/test_params_RNAseq_counts.yaml

**Whole Exome Sequencing (GATK)**::

	omics_pipe WES_GATK ~/tests/test_params_WES_GATK.yaml

**Whole Genome Sequencing (GATK)**::

	omics_pipe WGS_GATK ~/tests/test_params_WGS_GATK.yaml

**Whole Genome Sequencing (MUTECT)**::

	omics_pipe Tumorseq_MUTECT ~/tests/test_params_MUTECT.yaml


**ChIP-seq (MACS)**::

	omics_pipe ChIPseq_MACS ~/tests/test_params_MACS.yaml

**ChIP-seq (HOMER)**::

	omics_pipe ChIPseq_HOMER ~/tests/test_params_HOMER.yaml

**Breast Cancer Personalized Genomics Report- RNAseq**::

	omics_pipe RNAseq_cancer_report ~/tests/test_params_RNAseq_cancer.yaml

**TCGA Reanalysis Pipeline - RNAseq**::

	omics_pipe RNAseq_TCGA ~/tests/test_params_RNAseq_TCGA.yaml

**TCGA Reanalysis Pipeline - RNAseq Counts**::

	omics_pipe RNAseq_TCGA_counts ~/tests/test_params_RNAseq_TCGA_counts.yaml

**miRNAseq Counts (Anders 2013)**::

	omics_pipe miRNAseq_count_based ~/tests/test_params_miRNAseq_counts.yaml

**miRNAseq (Tuxedo)**::

	omics_pipe miRNAseq_tuxedo ~/tests/test_params_miRNAseq_Tuxedo.yaml
