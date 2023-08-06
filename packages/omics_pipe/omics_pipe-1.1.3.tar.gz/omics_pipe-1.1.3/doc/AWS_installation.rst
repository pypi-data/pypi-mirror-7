.. index:: omics_pipe; AWS_installation

=================================================
OmicsPipe on the Amazon Cloud (AWS EC2) Tutorial
=================================================

OmicsPipe on AWS uses a custom `StarCluster`_ image, created with `docker.io`_ ( which installs `docker.io`_, `environment-modules`_, and `easybuild`_ on an AWS EC2 cluster.
All you have to do is get the docker image, upload your data, launch the Amazon cluster and run a single command to analyze all of your data according to published, best-practice methods.

.. _docker.io: https://www.docker.io/
.. _environment-modules: http://modules.sourceforge.net/)
.. _easybuild: https://github.com/hpcugent/easybuild)

Step 1: Create an AWS Account
======================

1. Create an AWS account by following the instructions at `Amazon-AWS`_

2. Note your AWS ACCESS KEY ID, AWS SECRET ACCESS KEY and AWS USER ID

Step 2: Load the the OmicsPipe on AWS docker image on your machine
=========================================
.. note::
   If you are on a local Ubuntu installation, skip this step and `install`_ the StarCluster client directly. 

.. _install: http://web.mit.edu/Star/cluster/docs/latest/installation.html
   
1. Download `docker.io`_ following the instructions for your operating system at `Get-Docker`_  

.. rst-class:: floater

.. note::
   If you are using Windows, please update your BIOS to enable virtualization before installing Docker 
    
2. From inside the Docker environment, run the command::
	
	docker run -i -t omicspipe/aws_readymade /bin/bash

.. _Get-Docker: http://docs.docker.io/introduction/get-docker/

.. note::
   If you want to share a file from your local computer with the docker container, follow the instructions for `Docker Folder Sharing`_, put your desired file within the shared folder and run the command below (this is recommended for saving your /.starcluster/config file from the next step::
      
        docker run -it --volumes-from NameofSharedDataFolder omicspipe/aws_readymade /bin/bash

.. note::
   If you need to pull a recently updated docker container, from your terminal (before starting boot2docker start) run the following command before starting docker::
    
        boot2docker delete
      
.. _Docker Folder Sharing: https://github.com/boot2docker/boot2docker#folder-sharing

Step 3: Configure StarCluster
=============================
1. After running the omicspipe/aws_readymade Docker container, run the command below to edit the StarCluster configuration file::

	nano ~/.starcluster/config 
	
    Or if you prefer vim::
    
        vim ~/.starcluster/config
    
2. Enter your "AWS ACCESS KEY ID", "AWS SECRET ACCESS KEY", and "AWS USER ID"

3. Change the AWS REGION NAME and AWS REGION HOST variables if you do not live in the AWS us-west region to the appropriate region `AWS Regions`_.

4. Select your desired pre-configured cluster by editing the "DEFAULT_TEMPLATE" variable or creating a custom cluster. The default is a test cluster with 5 c3.large nodes.  

5. Save the edited file (Instructions for `Nano`_ and for `Vim`_)

6. Created your starcluster SSH key by running the command::
	
	starcluster createkey omicspipe -o ~/.ssh/omicspipe.rsa

.. note::
   If you have already created a key or you get an error at Step 6, run the command below to clear the existing key first and the repeat step 6::
      
      starcluster removekey omicspipe

.. rst-class:: floater

.. note::
   For more information on editing the StarCluster configuration file, see the `StarCluster`_ website.  

.. _AWS Regions: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
.. _Nano: http://mintaka.sdsu.edu/reu/nano.html
.. _Vim: http://www.fprintf.net/vimCheatSheet.html
.. _StarCluster: http://star.mit.edu/cluster/

Step 4: Create AWS Volumes
===========================
1. Create AWS volumes to store the raw data and results of your analyses. From within the Docker environment, run::

	starcluster createvolume --name=data -i ami-52112317 -d -s <volume size in GB> us-west-1a
		
	starcluster createvolume --name=results -i ami-52112317 -d -s <volume size in GB> us-west-1a

.. note::
   * Specify the <volume size in GB> as a number large enough to accomodate all of your raw data and ~4x that size for your results folder
   * Change us-west-1b to your region as described in `AWS Regions`_.

2. Make a snapshot of the provided reference databases (currently only supports H. sapiens)
 * Go to the `AWS-Console`_
 * Click on the `EC2 option`_
 * Click on Volumes
 * Click on "Create Volume"
 * Set availability zone
 * In Snapshot ID search for "omicspipe_db" and click on the resulting Snapshot ID
 * Click Create
 * From the Volumes tab, note the "VOLUME_ID" of the database snapshot
 
3. Edit your StarCluster configuration file to add your volume IDs. Run the command below and edit the VOLUME_ID variables for data, results, and database::

	nano ~/.starcluster/config 
    
   # Edit the fields below::
    
       [volume results]
       VOLUME_ID = 
       MOUNT_PATH = /data/results

       [volume data]
       VOLUME_ID = 
       MOUNT_PATH = /data/data
    
       [volume database]
       VOLUME_ID = 
       MOUNT_PATH = /data/database

4. Save your StarCluster configuration file. 

.. note::
   If you have a Shared Folder mounted in your Docker container and you have your edited StarCluster config file within it, make sure to copy it over to ~/.starcluster/config .

.. _Amazon-AWS: http://aws.amazon.com/getting-started/?sc_ichannel=ha&sc_icountry=en&sc_icampaigntype=general_info&sc_icampaign=ha_en_GettingStarted&sc_ipage=homepage&sc_iplace=ha_en_ed&sc_icategory=none&sc_iproduct=none&sc_isegment=none&sc_icontent=default&sc_idetail=none/
.. _AWS-Console: https://console.aws.amazon.com
.. _EC2 option: https://console.aws.amazon.com/ec2

Step 5: Launch the Cluster
============================
1. From the Docker container, run the command below to start a new cluster with the name "mypipe"::

	starcluster start mypipe
    
2. Optional but Recommended: To load balance the cluster, type the command below::

    starcluster loadbalance mypipe 
    
   (see `_load balance`_ for configuration options. Note: make sure to keep at least one woker node attached to the cluster)
   

3. SSH into the cluster by running the command below::

    starcluster sshmaster mypipe

.. _load balance: http://star.mit.edu/cluster/docs/0.95.5/manual/load_balancer.html

Step 6: Upload data to the cluster
===================================
Now that you are in your cluster, you can use it like any other cluster. Before running omics pipe on your own data (you can skip this step if you are running the test
data, you will want to upload your data. There are two options to upload your data:

1. Upload data from your local machine or cluster using `StarCluster put`_::

	starcluster put mypipe <myfile> /data/raw

.. note::
   * If you are using the Docker container, you must have your files loaded into the Docker container through the Shared Folder option above

2. Use `Webmin`_ to transfer files from your local system to the cluster (recommended for small files only, like parameter files). 

    * In the AWS Management Console go to "Security Groups"
    * Select the "StarCluster-0_95_5" group associated with your cluster's name
    * On the Inbound tab click on "Edit"
    * Click on "Add Rule" and a new "Custom TCP Rule" will apear. On "Port Range" enter "10000" and on "Source" select "My IP"
    * Hit "Save"
    * Selct Instances in the AWS managemnt console and note the "Public IP" of your instance
    * In a Web browser, enter https://the_public_ip:10000. Type in the Login info when prompted: user: root password: sulab
    * This will take a few seconds to load, and once it does, you can navigate your cluster's file structure with the tabs on the left
    * To upload a file from your local file system, click "upload" and specify the directory /data/data to upload your data. 


.. _StarCluster put: http://star.mit.edu/cluster/docs/0.93.3/manual/putget.html
.. _Webmin: http://www.webmin.com/

Installing extra software
==========================================================
Both the `GATK`_ and `MuTect`_ software are used by OmicsPipe, but they require licenses from The Broad Institute and cannot be distributed with the OmicsPipe software.
GATK and MuTect are free to download after accepting the license agreement.

.. _GATK: https://www.broadinstitute.org/gatk/
.. _MuTect: http://www.broadinstitute.org/cancer/cga/mutect

To install GATK:

1. `Download GATK`_
2. Upload the GenomeAnalysisTK.jar file to the /root/.local/easybuild/software/gatk/3.2-2 using either `Webmin`_ or `StarCluster put`_
3. Make the jar file executable by running the command: chmod +x /root/.local/easybuild/software/gatk/3.2-2/GenomeAnalysisTK.jar

To install MuTect:

1. `Download MuTect`_
2. Upload the muTect-1.1.4.jar file to the /root/.local/easybuild/software/mutect/1.1.4 using either `Webmin`_ or `StarCluster put`_
3. Make the jar file executable by running the command: chmod +x /root/.local/easybuild/software/mutect/1.1.4/muTect-1.1.4.jar

.. _Download GATK: https://www.broadinstitute.org/gatk/download
.. _Download MuTect: http://www.broadinstitute.org/cancer/cga/mutect_download
.. _Webmin: http://www.webmin.com/
.. _StarCluster put: http://star.mit.edu/cluster/docs/0.93.3/manual/putget.html

Adding software that OmicsPipe was not built with might require a little more configuration, but OmicsPipe is designed as a foundation to which new software can be added.
New software can obviously be added in any manner that the user prefers, but to follow the structure that was used to build OmicsPipe, please refer to the "custombuild" scripts.

.. important:: 
   * If you configure software that you think extends the functionality of OmicsPipe, please create a pull request on our `Bitbucket`_ page.

.. _Bitbucket: https://bitbucket.org/sulab/omics_pipe/pull-requests


To build your own docker image
==========================================================
1. Download docker.io following the instructions at `Get-Docker`_ 

2. Run the command::
	
	docker build -t <Repository Name> https://bitbucket.org/sulab/omics_pipe/downloads/Dockerfile_AWS_prebuiltAMI_public

This will store the dockercluster image in the Repository Name of your choice.

.. _Get-Docker: http://docs.docker.io/introduction/get-docker/

There is also an `AWS_custombuild Dockerfile`_, which can be used to build an Amazon Machine Image from scratch

.. _AWS_custombuild Dockerfile: https://bitbucket.org/sulab/omics_pipe/downloads/Dockerfile_AWS_custombuild

Add storage > 1TB to the cluster using LVM (for advanced users)
==========================================================
1. Within StarCluster create x new volumes by running::

      nvolumes=2 #number of volumes
      vsize=1000 #in gb
      instance=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
      akey=<AWS KEY>
      skey=<AWS SECRET KEY>
      region=us-west-1
      zone=us-west-1a

      for x in $(seq 1 $nvolumes)
      do
        ec2-create-volume \
	    --aws-access-key $akey \
	    --aws-secret-key $skey \
	    --size $vsize \
	    --region $region \
	    --availability-zone $zone
      done > /tmp/vols.txt 

2. Attach the volumes to the head node::
   
      i=0
      for vol in $(awk '{print $2}' /tmp/vols.txt)
      do
	    i=$(( i + 1 ))
	    ec2-attach-volume $vol \
	    -O $akey \
	    -W $skey \
	    -i $instance \
	    --region $region \
	    -d /dev/sdh${i}
      done > /tmp/attach.txt

3. Mark the EBS volumes as physical volumes::

      for i in $(find /dev/xvdh*)
      do
	   pvcreate $i
      done
      
4. Create a volume group::

      vgcreate vg /dev/xvdh*
   
5. Create a logical volume::

      lvcreate -l100%VG -n lv vg
      
6. Create the file system::

      mkfs -t xfs /dev/vg/lv
      
8. Mount the file system::

      mount /dev/vg/lv /data/data_large
      
9. Create mount point and mount the device::

      mkdir /data/data_large
      mount /dev/md0 /data/data_large
   
10. Add new mountpoint to /etc/exports::

      for x in $(qconf -sh | tail -n +2)
      do
	    echo '/data/data_large' ${x}'(async,no_root_squash,no_subtree_check,rw)' >> /etc/exports
      done
      
11. Reload /etc/exports::

      exportfs -a
   
12. Mount the new folder on all nodes::

      for x in $(qconf -sh | tail -n +2)
      do
	    ssh $x 'mkdir /data/data_large'
	    ssh $x 'mount -t nfs master:/data/data_large /data/data_large'
      done
      
      
**How to increase volume size?**

1. Create and attach EBS volumes as described in steps 1. & 2. and then create the additional physical volumes::

      for i in $(cat /tmp/attach.txt  | cut -f 4 | sed 's/[^0-9]*//g')
      do
	     pvcreate /dev/xvdh${i}
      done
      
2. Add new volumes to the volume group::

      for i in $(cat /tmp/attach.txt  | cut -f 4 | sed 's/[^0-9]*//g')
      do
	     vgextend vg /dev/xvdh${i}
      done
      
      lvextend -l100%VG /dev/mapper/vg-lv     
      
3.  Grow the file system to the new size::

      xfs_growfs /data/data_large
         

Add storage > 1TB to the cluster using RAID 0 (for advanced users)
==========================================================
1. Within StarCluster create x new volumes by running::

      nvolumes=2 #number of volumes
      vsize=1000 #in gb
      instance=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
      akey=<AWS KEY>
      skey=<AWS SECRET KEY>
      region=us-west-1
      zone=us-west-1a

      for x in $(seq 1 $nvolumes)
      do
        ec2-create-volume \
	    --aws-access-key $akey \
	    --aws-secret-key $skey \
	    --size $vsize \
	    --region $region \
	    --availability-zone $zone
      done > /tmp/vols.txt 

2. Attach the volumes to the head node::
   
      i=0
      for vol in $(awk '{print $2}' /tmp/vols.txt)
      do
	    i=$(( i + 1 ))
	    ec2-attach-volume $vol \
	    -O $akey \
	    -W $skey \
	    -i $instance \
	    --region $region \
	    -d /dev/sdh${i}
      done
   
3. Create a raid 0 volume::
   
      mdadm --create -l 0 -n $nvolumes /dev/md0 /dev/xvdh*
   
4. Create a file system::

      mkfs -t ext4 /dev/md0
   
5. Create mount point and mount the device::

      mkdir /data/data_large
      mount /dev/md0 /data/data_large
   
6. Add new mountpoint to /etc/exports::

      for x in $(qconf -sh | tail -n +2)
      do
	    echo '/data/data_large' ${x}'(async,no_root_squash,no_subtree_check,rw)' >> /etc/exports
      done
      
7. Reload /etc/exports::

      exportfs -a
   
8. Mount the new folder on all nodes::

      for x in $(qconf -sh | tail -n +2)
      do
	    ssh $x 'mkdir /data/data_large'
	    ssh $x 'mount -t nfs master:/data/data_large /data/data_large'
      done


Backing up your data to S3
==========================================================
1. Run::
      
      s3cmd --configure

and follow the instructions

2. Create a S3 bucket::

      s3cmd mb s3://backup
      
3. Copy data to the bucket::

      s3cmd put -r /data/results s3://backup
   
More info on s3cmd here: https://github.com/s3tools/s3cmd