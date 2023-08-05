txt2contincd
==========================
.. image:: https://secure.travis-ci.org/lambdalisue/txt2contincd.png?branch=master
    :target: http://travis-ci.org/lambdalisue/txt2contincd
    :alt: Build status

.. image:: https://coveralls.io/repos/lambdalisue/txt2contincd/badge.png?branch=master
    :target: https://coveralls.io/r/lambdalisue/txt2contincd/
    :alt: Coverage

.. image:: https://pypip.in/d/txt2contincd/badge.png
    :target: https://pypi.python.org/pypi/txt2contincd/
    :alt: Downloads

.. image:: https://pypip.in/v/txt2contincd/badge.png
    :target: https://pypi.python.org/pypi/txt2contincd/
    :alt: Latest version

.. image:: https://pypip.in/wheel/txt2contincd/badge.png
    :target: https://pypi.python.org/pypi/txt2contincd/
    :alt: Wheel Status

.. image:: https://pypip.in/egg/txt2contincd/badge.png
    :target: https://pypi.python.org/pypi/txt2contincd/
    :alt: Egg Status

.. image:: https://pypip.in/license/txt2contincd/badge.png
    :target: https://pypi.python.org/pypi/txt2contincd/
    :alt: License

txt2contincd convert raw text data files into a
`CONTIN-CD <http://s-provencher.com/pages/contin-cd.shtml>`_ input file.
It use `maidenhair <https://github.com/lambdalisue/maidenhair>`_ for reading raw
text files so any kind of raw text file can be used if there is a maidenhair
plugins.

Installation
------------
Use pip_ like::

    $ pip install txt2contincd

.. _pip:  https://pypi.python.org/pypi/pip

Quick Usage
-------------
Assume that you have measured the far-UV CD spectrum with the following condition::

    The number of residues (amino acids):   260 aa
    The molecular weight of the protein:    29.07 kDa
    The concentration of the protein:       0.303 mg/mL
    The length of the light pathway:        0.1 cm

Then run *txt2contincd* with

    % txt2contincd -n 260 -m 29.07 -c 0.303 -L 0.1 <raw CD spectrum>

It will produce ``contin-cd.in`` file.

Usage
------

::

    usage: txt2contincd [-h] [-v] [-p PARSER] [-l LOADER] [-u USING] [-a] [-s]
                        [-o OUTPUT] [-n NUMBER] [-m MOLECULAR_WEIGHT]
                        [-c CONCENTRATION]
                        [--molar-concentration MOLAR_CONCENTRATION] [-L LENGTH]
                        pathname

    positional arguments:
    pathname              An unix grob style filename pattern for the data files

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

    Reading options:
    -p PARSER, --parser PARSER
                            A maidenhair parser name which will be used to parse
                            the raw text data.
    -l LOADER, --loader LOADER
                            A maidenhair loader name which will be used to load
                            the raw text data.
    -u USING, --using USING
                            A colon (:) separated column indexes. It is used for
                            limiting the reading columns.
    -a, --average         Calculate the average value of the specified data.
    -s, --no-strict       Do not strict the wavelength range into 190-240 .
    -o OUTPUT, --output OUTPUT
                            A output filename. The default is "contin-cd.in".

    Experimental properties:
    -n NUMBER, --number NUMBER
                            The number of residues (amino acids) in the sample.
    -m MOLECULAR_WEIGHT, --molecular-weight MOLECULAR_WEIGHT
                            A molecular weight of the sample in kDa (=kg/mol).
    -c CONCENTRATION, --concentration CONCENTRATION
                            A concentration of the sample in g/L. See --molar-
                            concentration as an alternative.
    --molar-concentration MOLAR_CONCENTRATION
                            A molar concentration of the sample in mol/L. It is
                            used as an alternative option of --concentration.
    -L LENGTH, --length LENGTH
                            A light pathway length (cuvette length) in centimeter

Preference
-----------
You can create configure file as ``~/.config/txt2contincd/txt2contincd.cfg`` (Linux),
``~/.txt2contincd.cfg`` (Mac), or ``%APPDATA%\txt2contincd\txt2contincd.cfg`` (Windows).

The default preference is equal to the configure file as below::

    [default]
    parser = 'parsers.PlainParser'
    loader = 'loaders.PlainLoader'
    using = None
    average = False
    strict = True
    output = 'contin-cd.in'

    [experiment]
    number = None
    molecular_weight = None
    concentration = None
    molar_concentration = None
    length = None

I don't use Microsoft Windows so the location of the configure file in Windows
might be wrong.
Let me know if there are any mistakes.
