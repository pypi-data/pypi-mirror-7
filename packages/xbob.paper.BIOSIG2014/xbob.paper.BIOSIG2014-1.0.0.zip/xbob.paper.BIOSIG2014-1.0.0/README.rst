==========================================
Spoofing Attack to Finger vein Recognition
==========================================

This package provides the source code to run the experiments published in the paper `On the Vulnerability of Finger Vein Recognition to Spoofing <http://publications.idiap.ch/index.php/publications/show/2910>`_.
It relies on the FingerveinRecLib_ to execute the fingervein recognition experiments, and some satellite packages from Bob_ to compute the evaluation. See the video for more details: <http://www.idiap.ch/technology-transfer/demonstrations/spoofing-finger-vein-recognition>

.. note::
  Currently, this package only works in Unix-like environments and under MacOS.
  Due to limitations of the Bob_ library, MS Windows operating systems are not supported.
  We are working on a port of Bob_ for MS Windows, but it might take a while.
  In the meanwhile you could use our VirtualBox_ images that can be downloaded `here <http://www.idiap.ch/software/bob/images>`_.


Installation
============
The installation of this package relies on the `BuildOut <http://www.buildout.org>`_ system. By default, the command line sequence::

  $ ./python bootstrap.py
  $ ./bin/buildout

should download and install all requirements, including the FingerveinRecLib_, the database interface `xbob.db.vera <http://pypi.python.org/pypi/xbob.db.vera>`_, the Spoofing evaluation framework `antispoofing.evaluation <http://pypi.python.org/pypi/antispoofing.evaluation>`_ and all their required packages.
There are a few exceptions, which are not automatically downloaded:

Bob
---
The face recognition experiments rely on the open source signal-processing and machine learning toolbox Bob_.
To install Bob_, please visit http://www.idiap.ch/software/bob and follow the installation instructions.
Please verify that you have at least version 1.2.0 of Bob installed.
If you have installed Bob in a non-standard directory, please open the buildout.cfg file from the base directory and set the ``prefixes`` directory accordingly.

.. note::
  The experiments that we report in the Paper_ were generated with Bob_ version 1.2.1 and FingerveinRecLib_ version 1.0.0.
  If you use different versions of either of these packages, the results might differ slightly.
  For example, we are aware that, due to some initialization differences, the results using Bob 1.2.0 and 1.2.1 are not identical, but similar.


Image Databases
---------------
The experiments are run on external image databases.
We do not provide the images from the databases themselves.
Hence, please contact the database owners to obtain a copy of the images.
The two databases used in our experiments can be downloaded here:

- VERA Fingervein [``vera``]: http://www.idiap.ch/dataset/vera-fingervein
- VERA SpoofingFingervein [``vera``]: http://www.idiap.ch/dataset/vera-spoofingfingervein

.. note::
  For the experiments you have to create a unique directory (example: vera) and two subdirectories (vera/Fingervein) and (vera/SpoofingFingervein) that contain the databases.
  After downloading the databases, you will need to tell our software, where it can find them by changing the **configuration files**.
  In particular, please update the ``--imagedir`` to indicate the directory of the images in **xbob.db.vera**.


Please let all other configuration parameters unchanged as this might influence the face recognition experiments and, hence, the reproducibility of the results.

Getting help
------------
In case anything goes wrong, please feel free to open a new ticket in our GitLab_ page, or send an email to pedro.tome@idiap.ch.


Recreating the results of the Paper_
====================================

After successfully setting up the databases, you are now able to run the fingervein recognition and spoofing attack experiments as explained in the Paper_.

The experiment configuration
----------------------------
The fingervein recognition experiment are run using the **xbob.fingervein** package, but for convenience there exists a wrapper script that set up the right parametrization for the call to the FingerveinRecLib_.
The configuration files that are used by the FingerveinRecLib_, which contain all the parameters of the experiments, can be found in the **xbob.fingervein/xbob/fingervein/configurations** directory. 

Running the experiments
-----------------------
This script can be found in ``bin/biosig2014_fingervein_NOMandSpoofingAttack.py``.
It requires some command line options, which you can list using ``./bin/biosig2014_fingervein_NOMandSpoofingAttack.py --help``.
Usually, the command line options have a long version (starting with ``--``) and a shortcut (starting with a single ``-``), here we use only the long versions:

- ``--database``: Specify the name of the databases to run experiments on. (default: ``vera``).
- ``--preprocessing``: Specify the image preprocessing to run; the preprocessors will automatically assigned to the according experiment. Possible values are ``fingervein-preprocessor_lq`` and ``fingervein-preprocessor_lq_heq``. By default, experiments on both preprocessors are executed.
- ``--features``: Specify the features to run the experimetns. By default, the feature selected is the maximum curvature.
- ``--tool``: Specify the matcher to run the experimetns. By default, the miura-match-miuramax is selected.
- ``--protocols``: Specify a list of protocols that you want to run. Possible values are ``NOM50`` and ``SpoofingAttack50``. By default, all protocols are used.
- ``--dry-run``: Use this option to print the calls to the FingerveinRecLib_ without executing them.
- ``--temp-directory``: Specify a directory where temporary files will be stored (default: ``temp``). This directory can be deleted after all experiments ran successfully.
- ``--result-directory``: Specify a directory where final result files will be stored (default: ``results``). This directory is required to evaluate the experiments.

Additionally, you can pass options directly to the FingerveinRecLib_, but you should do that with care.
Simply use ``--`` to separate options to the ``bin/biosig2014_fingervein_NOMandSpoofingAttack.py`` from options to the FingerveinRecLib_.
For example, the ``--force`` option might be of interest.
See ``./bin/fingerveinverify.py --help`` for a complete list of options.

It is advisable to use the ``--dry-run`` option before actually running the experiments, just to see that everything is correct.
Also, the Info (2) verbosity level prints useful information, e.g., by adding the ``--verbose --verbose`` (or shortly ``-vv``) on the command line.
A commonly used command line sequence to execute the face recognition algorithm on both databases could be:

1. Run the experiments on the VERA database::

    $ ./bin/biosig2014_fingervein_NOMandSpoofingAttack.py -vv --databases vera

.. note::
  All output directories of the scripts will be automatically generated if they do not exist yet.

.. warning::
  The execution of the script may take a long time and require large amounts of memory.
  Nevertheless, the scripts are set up such that they re-use all parts of the experiments as far as this is possible.



Evaluating the experiments
--------------------------
After all experiments have finished successfully, the resulting score files can be evaluated.
For this, the ``bin/biosig2014_evaluate.py`` script can be used to create a pdf file with the SFAR curves that are provided in the paper. See ``./bin/plot_on_demand.py --help`` for a complete list of options. To replicate the results of the paper:

- ``--dev-file``: Specify the file of the scores file (4-column) containing the scores for the verification system, Normal Operation Mode (NOM) scenario.
- ``--spoofing-file``: The file of the scores file (4-column) containing the scores for the verification system, Spoofing Attack scenario.
- ``--output-file``: (Optional) Specify the name of the output pdf file. 
- ``--demandedplot``: Specify the option to plotting the score distribution for licit and spoof scenario and threshold line and probability of success line.

Again, the most usual way to compute the resulting tables could be:

1. Evaluate experiments on VERA::

    $ bin/biosig2014_evaluate.py -vvv 


Cite our paper
--------------

If you use the results in any of your contributions, please cite the following paper::

  @inproceedings{Tome_IEEEBIOSIG2014,
         author = {Tome, Pedro and Vanoni, Matthias and Marcel, S{\'{e}}bastien},
       keywords = {Biometrics, Finger vein, Spoofing Attacks},
          month = sep,
          title = {On the Vulnerability of Finger Vein Recognition to Spoofing},
      booktitle = {IEEE International Conference of the Biometrics Special Interest Group (BIOSIG)},
         series = {},
         volume = {},
           year = {2014},
          pages = {},
       location = {Darmstadt, Germay},
            url = {http://publications.idiap.ch/index.php/publications/show/2910}
  }



.. _paper: http://publications.idiap.ch/index.php/publications/show/2910
.. _idiap: http://www.idiap.ch
.. _bob: http://www.idiap.ch/software/bob
.. _fingerveinreclib: http://pypi.python.org/pypi/fingerveinreclib
.. _bioidiap at github: http://www.github.com/bioidiap
.. _gitlab: http://gitlab.idiap.ch/pedro.tome/xbob.paper.biosig2014
.. _virtualbox: http://www.virtualbox.org

