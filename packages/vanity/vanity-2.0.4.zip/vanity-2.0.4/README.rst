Vanity
======

Get package download statistics from PyPI.

Usage
-----

Enter a package name::

    $ vanity django
    Django-1.1.3.tar.gz    2010-12-23        4,938
    Django-1.1.4.tar.gz    2011-02-09       10,259
      Django-1.2.tar.gz    2010-05-17       24,011
    Django-1.2.1.tar.gz    2010-05-24       71,479
    Django-1.2.2.tar.gz    2010-09-09        4,388
    Django-1.2.3.tar.gz    2010-09-11       82,629
    Django-1.2.4.tar.gz    2010-12-23       66,223
    Django-1.2.5.tar.gz    2011-02-09       82,325
    Django-1.2.6.tar.gz    2011-09-10        2,559
    Django-1.2.7.tar.gz    2011-09-11       31,833
      Django-1.3.tar.gz    2011-03-23      363,202
    Django-1.3.1.tar.gz    2011-09-10      585,745
    Django-1.3.2.tar.gz    2012-07-30        7,649
    Django-1.3.3.tar.gz    2012-08-01       31,375
    Django-1.3.4.tar.gz    2013-03-05        1,974
    Django-1.3.5.tar.gz    2012-12-10       16,880
    Django-1.3.6.tar.gz    2013-02-19        2,292
    Django-1.3.7.tar.gz    2013-02-20       14,756
      Django-1.4.tar.gz    2012-03-23      437,635
    Django-1.4.1.tar.gz    2012-07-30      328,418
    Django-1.4.2.tar.gz    2012-10-17      326,088
    Django-1.4.3.tar.gz    2012-12-10      280,915
    Django-1.4.4.tar.gz    2013-02-19       12,453
    Django-1.4.5.tar.gz    2013-02-20      117,366
      Django-1.5.tar.gz    2013-02-26      124,429
    Django-1.5.1.tar.gz    2013-03-28      150,413
    ----------------------------------------------
    Django has been downloaded 3,182,234 times!

Or enter a package name with version specification:: 

    $ vanity pillow==2.0.0
                    Pillow-2.0.0.zip    2013-03-15       61,022
        Pillow-2.0.0.win32-py3.3.exe    2013-03-15          593
        Pillow-2.0.0.win32-py3.2.exe    2013-03-15          379
        Pillow-2.0.0.win32-py2.7.exe    2013-03-15          703
        Pillow-2.0.0.win32-py2.6.exe    2013-03-15          308
    Pillow-2.0.0.win-amd64-py3.3.exe    2013-03-15          487
    Pillow-2.0.0.win-amd64-py3.2.exe    2013-03-15          328
    Pillow-2.0.0.win-amd64-py2.7.exe    2013-03-15          500
    Pillow-2.0.0.win-amd64-py2.6.exe    2013-03-15          311
        Pillow-2.0.0-py3.3-win32.egg    2013-03-15          421
    Pillow-2.0.0-py3.3-win-amd64.egg    2013-03-15          431
        Pillow-2.0.0-py3.2-win32.egg    2013-03-15          353
    Pillow-2.0.0-py3.2-win-amd64.egg    2013-03-15          357
        Pillow-2.0.0-py2.7-win32.egg    2013-03-15        1,160
    Pillow-2.0.0-py2.7-win-amd64.egg    2013-03-15          620
        Pillow-2.0.0-py2.6-win32.egg    2013-03-15          730
    Pillow-2.0.0-py2.6-win-amd64.egg    2013-03-15          395
    -----------------------------------------------------------
    Pillow 2.0.0 has been downloaded 69,098 times!

Or enter more than one package name::

    $ bin/vanity --quiet setuptools distribute 
    setuptools has been downloaded 9,181,047 times!
    distribute has been downloaded 7,487,115 times!
    setuptools, distribute has been downloaded 16,668,162 times!

Installation
------------

Install via::

    $ pip install vanity

Or::

    $ easy_install vanity

Or download the compressed archive, extract it, and inside it run:: 

    $ python setup.py install
