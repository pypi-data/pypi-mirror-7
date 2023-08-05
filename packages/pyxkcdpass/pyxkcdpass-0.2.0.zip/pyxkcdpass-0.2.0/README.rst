===============================
PyXKCDPass
===============================

.. image:: https://badge.fury.io/py/pyxkcdpass.png
    :target: http://badge.fury.io/py/pyxkcdpass
    
.. image:: https://travis-ci.org/ikkebr/pyxkcdpass.png?branch=master
        :target: https://travis-ci.org/ikkebr/pyxkcdpass

.. image:: https://pypip.in/d/pyxkcdpass/badge.png
        :target: https://pypi.python.org/pypi/pyxkcdpass
        
.. image:: https://coveralls.io/repos/ikkebr/pyxkcdpass/badge.png?1234
        :target: https://coveralls.io/r/ikkebr/pyxkcdpass


        
.. image:: http://imgs.xkcd.com/comics/password_strength.png
        :target: www.xkcd.com/936/
        
        
This script provides a simple way to generate secure and human readable passwords, based on XKCD #936

* Free software: BSD license
* Documentation: http://pyxkcdpass.rtfd.org.

Install
--------

Open your terminal and type:

   ** pip install pyxkcdpass
   
or 
   
   ** easy_install pyxkcdpass

Usage
--------

Just call pyxckdpass and supply it with a dictionary:

  ** pyxkcdpass -d /usr/share/dict/words
  
or provide a dictionary and a password length

  ** pyxkcdpass -d /usr/share/dict/words -l 10
