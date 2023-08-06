*geeneus-0.1.8 released 18th August 2014*

geeneus
=========

Overview
----------
**geeneus** is a very simple Python API for accessing biological data in a stable, scriptable and easy manner. In its current version it provides access to protein record information, primarily from the NCBI servers but with the ability to fall back on EBI's UniProt servers (and default there where NCBI cannot provide the records needed). In future versions we hope to add similar functionality to access genetic information using the scalable backend frame work and design principles currently being employed to deal with protein data.

As a short usability summary, the general idea is that the a manager object (e.g. a ProteinMananager object) is created, which acts as a queryable database object. This object has a series of requests which can be made based on a proteins accession number (e.g. GI, UniProt, RefSeq) such as getting the protein name, sequence, mutations, isoforms etc. Regardless of which database the system eventually queries (NCBI or UniProt) the behaviour is identical. This manager object, in turn, deals with 100% of the complexity. The end user need not worry about parsing XML data, caching or networking problems.

For detailed documentation surrounding methods, design principles and relevant reading, `go here <http://alexholehouse.github.io/Geeneus/>`_

-------------

Installation
-------------

By far the easiest way to install geeneus is to use `pip` to directly install. Running::

    sudo pip install geeneus

Will install geeneus with the requests and biopython dependencies.

Geeneus can also be installed from source using `pip` which may be relevant if you wish to install a development version from github instead of waiting for a release though PyPi. Development versions are included in the github repo as self-standing tarballs.

------------

Usage - quickstart
--------------------

Once installed, general usage is as follows::

    #!/usr/bin/env python

    from geeneus import Proteome
    manager = Proteome.ProteinManager("your.emailaddress@email.com")
    manager.get_protein_name("accession number")

For more information regarding the possible functions try::

    help(geeneus)
    help(geeneus.Proteome)

Meeting NCBI's usage guideliness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An important consideration when working with eUtils wrappers is that you don't exceed `NCBI's usage guidelines
<http://www.ncbi.nlm.nih.gov/books/NBK25497/>`_. Geeneus has been written in such a way that every query to the database can only occur 0.4 seconds after the previous one, irrespective of anything else.

This means that even if you had something like this::

    for id in listOfIDs:
        print manager.get_protein_name[id]

You will not exceed the usage guidelines. However, NCBI has other guidelines which you should be aware of (notably no more than 100 successive queries during *peak* hours in the USA). It is up to you, the user, to ensure you meet these requirements.

This is also why the `manager` object requires an email address on initialization.   

------------

More information
----------------
For information on this project, including underlying design principles just `click here
<http://alexholehouse.github.io/Geeneus/>`_. The github repository is  `available here
<https://github.com/alexholehouse/Geeneus>`_.

------------


Requirements
--------------
geeneus requires `biopython <http://biopython.org/DIST/docs/install/Installation.html>`_ and 'requests <http://docs.python-requests.org/en/latest/>`_. Initially we're assuming biopython 1.6, although earlier versions haven't been tested. To put it another way, we've tested on 1.6 and all's well. Earlier versions may also work, but you're on your own.

------------

About
----------
This code was developed by `Alex Holehouse
<http://holehouse.org/>`_ at `Washington University in Saint Louis
<http://www.wustl.edu/>`_ as part of the `Naegle lab
<http://naegle.wustl.edu/>`_. It is licensed under the the GNU General Public License (GPL-2.0). For more information see LICENCE.
