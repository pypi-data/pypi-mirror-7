Bimodal Gender Recognition
==========================

This package contains scripts to reproduce the experiments of the following article on bimodal (face and speech) gender recognition:

This article published at (Not Yet Published)::

   @inproceedings{BimodalGenderRec2014,
     author = {Laurent El Shafey, Elie Khoury, S{\'e}bastien Marcel},
     title = {Audio-visual Gender Recognition in Uncontrolled Environment Using Variability Modeling Techniques},
     year = {2014}
   }

If you use this package and/or its results, we would appreciate that you cite the previous publication as well as:

Bob as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
      author = {A. Anjos and L. El Shafey and R. Wallace and M. G\"unther and C. McCool and S. Marcel},
      title = {Bob: a free signal processing and machine learning toolbox for researchers},
      year = {2012},
      month = {oct},
      booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
      publisher = {ACM Press},
      url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
    }


Installation
------------

To download the package, please go to http://pypi.python.org/pypi/xbob.gender.bimodal, click on the **download** button and extract the .zip file to a folder of your choice.


Bob
...

You will need a copy of Bob in version 1.2.2 to run the algorithms.
Please download `Bob <http://www.idiap.ch/software/bob>`_ from its webpage.

After downloading and extracting this package, you should go to the console and write::

   $ python bootstrap.py
   $ bin/buildout

This will download all required dependencies and install them locally.


Databases
.........

Experiments are conducted on several databases.
They should be downloaded and extracted manually to be able to reproduce the plots.

- FERET [http://www.itl.nist.gov/iad/humanid/feret/feret_master.html] (eye center annotations are shipped with this package in the directory `feret_annotations <feret_annotations>`_)
- MOBIO  [http://www.idiap.ch/dataset/mobio]
- Labeled Faces in the Wild (LFW) [http://vis-www.cs.umass.edu/lfw] (images aligned with funneling [http://vis-www.cs.umass.edu/lfw/lfw-funneled.tgz] and annotations [http://www.idiap.ch/resource/biometric/data/LFW-Annotations.tar.gz])
- NIST Speaker Recognition Evaluation 2012 [http://www.nist.gov/itl/iad/mig/sre12.cfm] (Additional data distributed by `LDC <https://www.ldc.upenn.edu/>`_ are required for training and development purposes [see https://pypi.python.org/pypi/xbob.db.nist_sre12 to preprocess the data])

Once you have installed the databases, you should set the path to raw data into some configuration files.
For instance, for running experiments on the FERET database, you should set the variables 'image_directory' and 'annotation_directory' in the file `feret.py <xbob/gender/bimodal/configurations/databases/feret.py>`_ to your directory that contains the images (resp. annotations) of this database.

.. note:: For the FERET database, the original images should be converted into '.png' format. For reproducibility purposes, we recommend you to use ImageMagick through the 'convert' binary utility.


Running experiments
-------------------

If you have set up everything mentioned above, you are ready to run the gender recognition experiments.

This process is split into two different steps::

   1. Generation of raw scores from raw data (image/audio files [and possibly annotations]) of the databases

   2. Generation of plots from these raw scores

In practice, the first step has high computational requirements, which depend on the database considered.



FERET Experiments
-----------------

Generation of raw scores
........................

After downloading the database and setting up the configuration file feret.py_
(image and annotation directories),
you should run the following set of scripts. 
All the loops are independent and can be split as different processes (Don't forget to set the MYDIR variable within each terminal)::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ for k in 16 24 32 48 64 80 ; do 
       # Raw pixels
       ./bin/faceverify.py -d gferet -p face-crop-${k} -f dct -t gmm --user-directory ${MYDIR}/feret/results --temp-directory ${MYDIR}/feret -b crop${k}x${k}_raw --skip-extraction --skip-extractor-training --skip-extraction --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation
       # SVM classifiers
       ./bin/svm_linear.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_raw/preprocessed/ --output-directory ${MYDIR}/feret/crop${k}x${k}_raw/svm/
     done

   $ for k in 16 24 32 48 64 80 ; do 
       # HOG features
       ./bin/faceverify.py -d gferet -p face-crop-${k} -f hog-${k} -t gmm --user-directory ${MYDIR}/feret/results --temp-directory ${MYDIR}/feret -b crop${k}x${k}_hog --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation
       # SVM classifiers
       ./bin/svm_linear.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_hog/features/ --output-directory ${MYDIR}/feret/crop${k}x${k}_hog/svm/
     done


   $ for k in 16 24 32 48 64 80 ; do 
       # LBP features
       ./bin/faceverify.py -d gferet -p face-crop-${k} -f lbphs -t gmm --user-directory ${MYDIR}/feret/results --temp-directory ${MYDIR}/feret -b crop${k}x${k}_lbp --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation
       # SVM classifiers
       ./bin/svm_linear.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_lbp/features/ --output-directory ${MYDIR}/feret/crop${k}x${k}_lbp/svm/
     done


   $ for k in 16 24 32 48 64 80 ; do 
       # DCT
       ./bin/faceverify.py -d gferet -p face-crop-${k} -f dct -t gmm --user-directory ${MYDIR}/feret/results --temp-directory ${MYDIR}/feret -b crop${k}x${k}_dct --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation

       # GMM
       ./bin/gmm_training.py -d gferet-female --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/features --temp-directory ${MYDIR}/feret/crop${k}x${k}_dct/ --user-directory ${MYDIR}/feret/crop${k}x${k}_dct/ -b gmm_female
       ./bin/gmm_training.py -d gferet-male --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/features --temp-directory ${MYDIR}/feret/crop${k}x${k}_dct/ --user-directory ${MYDIR}/feret/crop${k}x${k}_dct/ -b gmm_male
       ./bin/gmm_scoring.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/features/ --gmm-male-filename ${MYDIR}/feret/crop${k}x${k}_dct/gmm_male/Projector.hdf5 --gmm-female-filename ${MYDIR}/feret/crop${k}x${k}_dct/gmm_female/Projector.hdf5 --output-directory ${MYDIR}/feret/crop${k}x${k}_dct/gmm/scores

       ./bin/gmm_training.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/features --temp-directory ${MYDIR}/feret/crop${k}x${k}_dct/ --user-directory ${MYDIR}/feret/crop${k}x${k}_dct/

       # ISV
       ./bin/isv_training.py -d gferet --gmm-directory ${MYDIR}/feret/crop${k}x${k}_dct/gmm --temp-directory ${MYDIR}/feret/crop${k}x${k}_dct/ --user-directory ${MYDIR}/feret/crop${k}x${k}_dct/ -b isv
       ./bin/isv_scoring.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/features/ --gmm-directory ${MYDIR}/feret/crop${k}x${k}_dct/gmm/ --isv-directory ${MYDIR}/feret/crop${k}x${k}_dct/isv/

       # IVector
       ./bin/ivector.py -d gferet -b ivec -t myivector200 --gmm-directory ${MYDIR}/feret/crop${k}x${k}_dct/gmm/ --temp-directory ${MYDIR}/feret/crop${k}x${k}_dct/ --user-directory ${MYDIR}/feret/crop${k}x${k}_dct/
       ./bin/svm_linear.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/ivec/wccn_projected_ivector/ --output-directory ${MYDIR}/feret/crop${k}x${k}_dct/ivec/svm/
       ./bin/cosine_distance.py -d gferet --features-directory ${MYDIR}/feret/crop${k}x${k}_dct/ivec/wccn_projected_ivector/  -T ${MYDIR}/feret/crop${k}x${k}_dct/ivec/ -b cosine -U ${MYDIR}/feret/crop${k}x${k}_dct/ivec/
     done


Plotting
........

Once all the scores have been generated, the plot and the table on FERET reported on the article can be obtained by using::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_feret.py -r ${MYDIR}
   $ xdg-open feret.pdf

.. note:: The Table 1 will be displayed in the output stream of the terminal once the script completed.


LFW Experiments
---------------

Generation of raw scores
........................

After downloading the database and setting up the configuration files 
`lfw_fold0.py <file:xbob/gender/bimodal/configurations/databases/lfw_fold0.py>`_,
`lfw_fold1.py <file:xbob/gender/bimodal/configurations/databases/lfw_fold1.py>`_,
`lfw_fold2.py <file:xbob/gender/bimodal/configurations/databases/lfw_fold2.py>`_,
`lfw_fold3.py <file:xbob/gender/bimodal/configurations/databases/lfw_fold3.py>`_ and
`lfw_fold4.py <file:xbob/gender/bimodal/configurations/databases/lfw_fold4.py>`_
(image and annotation directories),
you should run the following set of scripts. 
All the loops are independent and can be split as different processes (Don't forget to set the MYDIR variable within each terminal)::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ for f in lfw-fold0 lfw-fold1 lfw-fold2 lfw-fold3 lfw-fold4 ; do
       # Raw pixels
       ./bin/faceverify.py -d g${f} -p face-crop-80 -f dct -t gmm --user-directory ${MYDIR}/${f}/results --temp-directory ${MYDIR}/${f} -b crop80x80_raw --skip-extraction --skip-extractor-training --skip-extraction --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;
       # SVM classifiers
       ./bin/svm_linear.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_raw/preprocessed/ --output-directory ${MYDIR}/${f}/crop80x80_raw/svm/
     done

   $ for f in lfw-fold0 lfw-fold1 lfw-fold2 lfw-fold3 lfw-fold4 ; do
       # HOG
      ./bin/faceverify.py -d g${f} -p face-crop-80 -f hog-80 -t gmm --user-directory ${MYDIR}/${f}/results --temp-directory ${MYDIR}/${f} -b crop80x80_hog --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;
      # SVM classifiers
      ./bin/svm_linear.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_hog/features/ --output-directory ${MYDIR}/${f}/crop80x80_hog/svm/
     done

   $ for f in lfw-fold0 lfw-fold1 lfw-fold2 lfw-fold3 lfw-fold4 ; do
       # LBP
       ./bin/faceverify.py -d g${f} -p face-crop-80 -f lbphs -t gmm --user-directory ${MYDIR}/${f}/results --temp-directory ${MYDIR}/${f} -b crop80x80_lbp --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;
       # SVM classifiers
       ./bin/svm_linear.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_lbp/features/ --output-directory ${MYDIR}/${f}/crop80x80_lbp/svm/
     done


   $ for f in lfw-fold0 lfw-fold1 lfw-fold2 lfw-fold3 lfw-fold4 ; do
       # DCT
       ./bin/faceverify.py -d g${f} -p face-crop-80 -f dct -t gmm --user-directory ${MYDIR}/${f}/results --temp-directory ${MYDIR}/${f} -b crop80x80_dct --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;

       # GMM
       ./bin/gmm_training.py -d g${f}-female --features-directory ${MYDIR}/${f}/crop80x80_dct/features --temp-directory ${MYDIR}/${f}/crop80x80_dct/ --user-directory ${MYDIR}/${f}/crop80x80_dct/ -b gmm_female
       ./bin/gmm_training.py -d g${f}-male --features-directory ${MYDIR}/${f}/crop80x80_dct/features --temp-directory ${MYDIR}/${f}/crop80x80_dct/ --user-directory ${MYDIR}/${f}/crop80x80_dct/ -b gmm_male
       ./bin/gmm_scoring.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_dct/features/ --gmm-male-filename ${MYDIR}/${f}/crop80x80_dct/gmm_male/Projector.hdf5 --gmm-female-filename ${MYDIR}/${f}/crop80x80_dct/gmm_female/Projector.hdf5 --output-directory ${MYDIR}/${f}/crop80x80_dct/gmm/scores


       ./bin/gmm_training.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_dct/features --temp-directory ${MYDIR}/${f}/crop80x80_dct/ --user-directory ${MYDIR}/${f}/crop80x80_dct/

       # ISV
       ./bin/isv_training.py -d g${f} --gmm-directory ${MYDIR}/${f}/crop80x80_dct/gmm --temp-directory ${MYDIR}/${f}/crop80x80_dct/ --user-directory ${MYDIR}/${f}/crop80x80_dct/ -b isv
       ./bin/isv_scoring.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_dct/features/ --gmm-directory ${MYDIR}/${f}/crop80x80_dct/gmm/ --isv-directory ${MYDIR}/${f}/crop80x80_dct/isv/

       # IVector
       ./bin/ivector.py -d g${f} -b ivec -t myivector --gmm-directory ${MYDIR}/${f}/crop80x80_dct/gmm/ --temp-directory ${MYDIR}/${f}/crop80x80_dct/ --user-directory ${MYDIR}/${f}/crop80x80_dct/
       ./bin/svm_linear.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_dct/ivec/wccn_projected_ivector/ --output-directory ${MYDIR}/${f}/crop80x80_dct/ivec/svm/
       ./bin/cosine_distance.py -d g${f} --features-directory ${MYDIR}/${f}/crop80x80_dct/ivec/wccn_projected_ivector/  -T ${MYDIR}/${f}/crop80x80_dct/ivec/ -b cosine -U ${MYDIR}/${f}/crop80x80_dct/ivec/
     done


Plotting
........

Once all the scores have been generated, the plot and the table on LFW reported on the article can be obtained by using::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_lfw.py -r ${MYDIR}
     ...
   $ xdg-open lfw.pdf

.. note:: The Table 2 will be displayed in the output stream of the terminal once the script completed.


MOBIO Experiments
-----------------

Generation of raw scores
........................

After downloading the database and setting up the configuration files
`mobio_image <file:xbob/gender/bimodal/configurations/databases/mobio.py>`_
(image and annotation directories) and
`mobio_speech <file:xbob/gender/bimodal/configurations/audio/mobio/all.py>`_
(audio data),
you should run the following set of scripts. 
All the loops are independent and can be split as different processes (Don't forget to set the MYDIR variable within each terminal).

Face experiments::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # Raw pixels
   $ ./bin/faceverify.py -d gmobio -p face-crop-80 -f dct -t gmm --user-directory ${MYDIR}/mobio/results --temp-directory ${MYDIR}/mobio -b crop80x80_raw --skip-extraction --skip-extractor-training --skip-extraction --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;
   $ # SVM classifiers
   $ ./bin/svm_linear.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_raw/preprocessed/ --output-directory ${MYDIR}/mobio/crop80x80_raw/svm/

   $ # HOG
   $ ./bin/faceverify.py -d gmobio -p face-crop-80 -f hog-80 -t gmm --user-directory ${MYDIR}/mobio/results --temp-directory ${MYDIR}/mobio -b crop80x80_hog --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;
   $ # SVM classifiers
   $ ./bin/svm_linear.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_hog/features/ --output-directory ${MYDIR}/mobio/crop80x80_hog/svm/

   $ # LBP
   $ ./bin/faceverify.py -d gmobio -p face-crop-80 -f lbphs -t gmm --user-directory ${MYDIR}/mobio/results --temp-directory ${MYDIR}/mobio -b crop80x80_lbp --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;
   $ # SVM classifiers
   $ ./bin/svm_linear.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_lbp/features/ --output-directory ${MYDIR}/mobio/crop80x80_lbp/svm/

   $ # DCT
   $ ./bin/faceverify.py -d gmobio -p face-crop-80 -f dct -t gmm --user-directory ${MYDIR}/mobio/results --temp-directory ${MYDIR}/mobio -b crop80x80_dct --skip-extractor-training --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation ;

   $ # GMM
   $ ./bin/gmm_training.py -d gmobio-female --features-directory ${MYDIR}/mobio/crop80x80_dct/features --temp-directory ${MYDIR}/mobio/crop80x80_dct/ --user-directory ${MYDIR}/mobio/crop80x80_dct/ -b gmm_female
   $ ./bin/gmm_training.py -d gmobio-male --features-directory ${MYDIR}/mobio/crop80x80_dct/features --temp-directory ${MYDIR}/mobio/crop80x80_dct/ --user-directory ${MYDIR}/mobio/crop80x80_dct/ -b gmm_male
   $ ./bin/gmm_scoring.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_dct/features/ --gmm-male-filename ${MYDIR}/mobio/crop80x80_dct/gmm_male/Projector.hdf5 --gmm-female-filename ${MYDIR}/mobio/crop80x80_dct/gmm_female/Projector.hdf5 --output-directory ${MYDIR}/mobio/crop80x80_dct/gmm/scores

   $ ./bin/gmm_training.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_dct/features --temp-directory ${MYDIR}/mobio/crop80x80_dct/ --user-directory ${MYDIR}/mobio/crop80x80_dct/

   $ # ISV
   $ ./bin/isv_training.py -d gmobio --gmm-directory ${MYDIR}/mobio/crop80x80_dct/gmm --temp-directory ${MYDIR}/mobio/crop80x80_dct/ --user-directory ${MYDIR}/mobio/crop80x80_dct/ -b isv
   $ ./bin/isv_scoring.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_dct/features/ --gmm-directory ${MYDIR}/mobio/crop80x80_dct/gmm/ --isv-directory ${MYDIR}/mobio/crop80x80_dct/isv/

   $ # IVector
   $ ./bin/ivector.py -d gmobio -b ivec -t myivector --gmm-directory ${MYDIR}/mobio/crop80x80_dct/gmm/ --temp-directory ${MYDIR}/mobio/crop80x80_dct/ --user-directory ${MYDIR}/mobio/crop80x80_dct/
   $ ./bin/svm_linear.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_dct/ivec/wccn_projected_ivector/ --output-directory ${MYDIR}/mobio/crop80x80_dct/ivec/svm/
   $ ./bin/cosine_distance.py -d gmobio --features-directory ${MYDIR}/mobio/crop80x80_dct/ivec/wccn_projected_ivector/  -T ${MYDIR}/mobio/crop80x80_dct/ivec/ -b cosine -U ${MYDIR}/mobio/crop80x80_dct/ivec/ --groups 'dev' 'eval'

Speech experiments::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # MFCC
   $ ./bin/mfcc_vad_energy.py -d xbob/gender/bimodal/configurations/audio/mobio/all.py -b mfcc60 -T ${MYDIR}/mobio/

   $ # GMM
   $ ./bin/gmm_training.py -d gmobio-female --features-directory ${MYDIR}/mobio/mfcc60/features --temp-directory ${MYDIR}/mobio/mfcc60/ --user-directory ${MYDIR}/mobio/mfcc60/ -b gmm_female
   $ ./bin/gmm_training.py -d gmobio-male --features-directory ${MYDIR}/mobio/mfcc60/features --temp-directory ${MYDIR}/mobio/mfcc60/ --user-directory ${MYDIR}/mobio/mfcc60/ -b gmm_male
   $ ./bin/gmm_scoring.py -d gmobio --features-directory ${MYDIR}/mobio/mfcc60/features/ --gmm-male-filename ${MYDIR}/mobio/mfcc60/gmm_male/Projector.hdf5 --gmm-female-filename ${MYDIR}/mobio/mfcc60/gmm_female/Projector.hdf5 --output-directory ${MYDIR}/mobio/mfcc60/gmm/scores

   $ ./bin/gmm_training.py -d gmobio --features-directory ${MYDIR}/mobio/mfcc60/features --temp-directory ${MYDIR}/mobio/mfcc60/ --user-directory ${MYDIR}/mobio/mfcc60/

   $ # ISV
   $ ./bin/isv_training.py -d gmobio --gmm-directory ${MYDIR}/mobio/mfcc60/gmm --temp-directory ${MYDIR}/mobio/mfcc60/ --user-directory ${MYDIR}/mobio/mfcc60/ -b isv
   $ ./bin/isv_scoring.py -d gmobio --features-directory ${MYDIR}/mobio/mfcc60/features/ --gmm-directory ${MYDIR}/mobio/mfcc60/gmm/ --isv-directory ${MYDIR}/mobio/mfcc60/isv/

   $ # IVector
   $ ./bin/ivector.py -d gmobio -b ivec -t myivector --gmm-directory ${MYDIR}/mobio/mfcc60/gmm/ --temp-directory ${MYDIR}/mobio/mfcc60/ --user-directory ${MYDIR}/mobio/mfcc60/
   $ ./bin/svm_linear.py -d gmobio --features-directory ${MYDIR}/mobio/mfcc60/ivec/wccn_projected_ivector/ --output-directory ${MYDIR}/mobio/mfcc60/ivec/svm/
   $ ./bin/cosine_distance.py -d gmobio --features-directory ${MYDIR}/mobio/mfcc60/ivec/wccn_projected_ivector/  -T ${MYDIR}/mobio/mfcc60/ivec/ -b cosine -U ${MYDIR}/mobio/mfcc60/ivec/ --groups 'dev' 'eval'

Once all the previous scores have been generated, bimodal fusion is achieved with the following script::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/fusion_mobio.py -r ${MYDIR}


Plotting
........

Once all the scores have been generated, the plots on MOBIO reported on the article can be obtained by using::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_mobio.py -r ${MYDIR}
     ...
   $ xdg-open mobio.pdf

.. note:: The Table 4 will be displayed in the output stream of the terminal once the script completed.


NIST SRE Experiments
--------------------

Generation of raw scores
........................

After downloading and preprocessing the database (see https://pypi.python.org/pypi/xbob.db.nist_sre12), 
you should set up the configuration file
`all.py <file:xbob/gender/bimodal/configurations/audio/nistsre/all.py>`_.
Then, you should be able to run the following set of scripts::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # MFCC
   $ ./bin/mfcc_vad_energy.py -d xbob/gender/bimodal/configurations/audio/nistsre/all.py -b mfcc60 -T ${MYDIR}/nistsre/

   $ # GMM
   $ ./bin/gmm_training.py -d gnistsre-female --features-directory ${MYDIR}/nistsre/mfcc60/features --temp-directory ${MYDIR}/nistsre/mfcc60/ --user-directory ${MYDIR}/nistsre/mfcc60/ -b gmm_female
   $ ./bin/gmm_training.py -d gnistsre-male --features-directory ${MYDIR}/nistsre/mfcc60/features --temp-directory ${MYDIR}/nistsre/mfcc60/ --user-directory ${MYDIR}/nistsre/mfcc60/ -b gmm_male
   $ ./bin/gmm_scoring.py -d gnistsre --features-directory ${MYDIR}/nistsre/mfcc60/features/ --gmm-male-filename ${MYDIR}/nistsre/mfcc60/gmm_male/Projector.hdf5 --gmm-female-filename ${MYDIR}/nistsre/mfcc60/gmm_female/Projector.hdf5 --output-directory ${MYDIR}/nistsre/mfcc60/gmm/scores

   $ ./bin/gmm_training.py -d gnistsre --features-directory ${MYDIR}/nistsre/mfcc60/features --temp-directory ${MYDIR}/nistsre/mfcc60/ --user-directory ${MYDIR}/nistsre/mfcc60/

   $ # ISV
   $ ./bin/isv_training.py -d gnistsre --gmm-directory ${MYDIR}/nistsre/mfcc60/gmm --temp-directory ${MYDIR}/nistsre/mfcc60/ --user-directory ${MYDIR}/nistsre/mfcc60/ -b isv
   $ ./bin/isv_scoring.py -d gnistsre --features-directory ${MYDIR}/nistsre/mfcc60/features/ --gmm-directory ${MYDIR}/nistsre/mfcc60/gmm/ --isv-directory ${MYDIR}/nistsre/mfcc60/isv/

   $ # IVector
   $ ./bin/ivector.py -d gnistsre -b ivec -t myivector --gmm-directory ${MYDIR}/nistsre/mfcc60/gmm/ --temp-directory ${MYDIR}/nistsre/mfcc60/ --user-directory ${MYDIR}/nistsre/mfcc60/
   $ ./bin/svm_linear.py -d gnistsre --features-directory ${MYDIR}/nistsre/mfcc60/ivec/wccn_projected_ivector/ --output-directory ${MYDIR}/nistsre/mfcc60/ivec/svm/
   $ ./bin/cosine_distance.py -d gnistsre --features-directory ${MYDIR}/nistsre/mfcc60/ivec/wccn_projected_ivector/  -T ${MYDIR}/nistsre/mfcc60/ivec/ -b cosine -U ${MYDIR}/nistsre/mfcc60/ivec/ --groups 'dev' 'eval'


.. note:: To train the GMM, we used a parallelized implementation, where we initialized k-means with a subset of the data as follows::

   $ ./bin/para_gmm_training.py -d gnistsre --temp-directory ${MYDIR}/nistsre/mfcc60/ --user-directory ${MYDIR}/nistsre/mfcc60/ --nopre --noe -b gmm -g xbob/gender/bimodal/configurations/grid/para_gmm.py -l 5000


Plotting
........

Once all the scores have been generated, the plot on NIST-SRE reported on the article can be obtained by using::

   $ MYDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_nistsre.py -r ${MYDIR}
     ...
   $ xdg-open nistsre.pdf


Problems
--------

In case of problems, please contact any of the authors of the paper.

If you are facing technical issues to be able to run the scripts 
of this package, you can send a message on the `Bob's mailing list
<https://groups.google.com/forum/#!forum/bob-devel>`_.

Please follow `these guidelines 
<http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/TicketReportingDev.html>`_
when (or even better before) reporting any bug.

