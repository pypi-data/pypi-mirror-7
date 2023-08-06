==================
Ubuntu AMI Locator
==================

.. image:: https://badge.fury.io/py/ubuntufinder.png
    :target: http://badge.fury.io/py/ubuntufinder

.. image:: https://travis-ci.org/krallin/ubuntufinder.png?branch=master
        :target: https://travis-ci.org/krallin/ubuntufinder

.. image:: https://pypip.in/d/ubuntufinder/badge.png
        :target: https://crate.io/packages/ubuntufinder?version=latest


An utility package to locate the latest Ubuntu AMIs.

* Quickstart: http://ubuntufinder.readthedocs.org/en/latest/usage.html
* Documentation (CLI & library usage): http://ubuntufinder.readthedocs.org.
* Free software: BSD license

::

    $ pip install --upgrade ubuntufinder
    $ ubuntufinder -r precise -a amd64 -i ebs -v paravirtual us-east-1
    ami-fa7dba92
