idx2numpy
=========

idx2numpy package provides a tool for converting files from IDX format to
numpy.ndarray. You can meet files in IDX format, e.g. when you're going
to read the [MNIST database of handwritten digits]
(http://yann.lecun.com/exdb/mnist/) provided by Yann LeCun.

The description of IDX format also can be found on this page.

[![Build Status](https://travis-ci.org/ivanyu/idx2numpy.svg?branch=master)](https://travis-ci.org/ivanyu/idx2numpy)

Installation
============

The easiest way to install is by using pip to pull it from PyPI:

    pip install idx2numpy

You can also clone the Git repository from Github and install 
the package manually:

    git clone https://github.com/ivanyu/idx2numpy.git
    python setup.py install

Usage
=====

    import idx2numpy
    ndarr = idx2numpy.convert_from_file('myfile.idx')
    
    f = open('myfile.idx', 'rb)
    ndarr = idx2numpy.convert_from_file(f)
    
    s = f.read()
    ndarr = idx2numpy.convert_from_string(s)

Authors and Contributors
========================
The project is started and maintained by Ivan Yurchenko
(ivan0yurchenko@gmail.com).
The Contributors are:
 * [andres-s](https://github.com/andres-s)

License
=======
MIT license (see *LICENSE* file)


Also
====

Please, send me a feedback about the library, such as bugs, use cases etc.
