==============================
python-ldap_paged_search 0.4.1
==============================

Summary
=======

ldap_paged_search is a python library to easily perform LDAP queries with more
than 1000 results, or to break down queries into smaller result sets to reduce
server loads.

Many LDAP servers, such as active directory, will not return more than 1000
results unless paged requests are used.  The existing python ldap library does
support pageing, but requires some not very intuitive coding to perform it.
This library is simply a wrapper to make paged searches easy.

Its interface is also slightly easier to perform queries than the LDAP library
it wraps.

Requirements
============

* Tested on python 2.8
* Default python library includes ldap library

Installation
============

Via pip or easy_install
-----------------------

.. code:: bash

    $ sudo pip install ldap_paged_search   # If you prefer PIP

    $ sudo easy_install ldap_paged_search  # If you prefer easy_install

Manual installation
-------------------

.. code:: bash

    $ git clone https://github.com/neoCrimeLabs/python-ldap_paged_search.git
    $ cd python-ldap_paged_search
    $ sudo python setup.py install

Usage
=====

Initial setup
-------------

.. code:: python

    from ldap_paged_search import LdapPagedSearch

    # Required values
    url             = 'ldap://your.ldap.server'
    username        = 'username'      # for anything but active directory
    username        = 'domain\\user'  # for active directory
    password        = 'yourPassword'

    baseDN          = 'dc=company,dc=com'
    searchFilter    = '(&(objectCategory=user))'

    # Optional values
    maxPages        = 0     # 0 = everything
    maxPages        = 10    # Return first 10 pages only

    attributes      = ['*']                         # Return all fields
    attributes      = ['FieldName', 'AnotherField'] # Return specific fields only
                            

    pageSize        = 1000  # How many records per page
                            # Usual max is 1000; check your LDAP server docs

Defining a callback method
--------------------------

.. code:: python

    # Using a callback method to process results uses less memory on large queries
    # Not using a callback search() will return all results as a single list

    def myCallback(dn,record):
        print dn, record

Query using 'with'
------------------

.. code:: python

    # maxPages, pageSize, attributes, and callback are all OPTIONAL

    with LdapPagedSearch(url, username, password, maxPages=2, pageSize=2 ) as l:
        results = l.search(baseDN, searchFilter, attributes = attributes, callback = myCallback)


Alternative query method
------------------------

.. code:: python

    # maxPages, pageSize, attributes, and callback are all OPTIONAL

    l = LdapPagedSearch(url, username, password, maxPages=2, pageSize=2 )
    results = l.search(baseDN, searchFilter, attributes = attributes, callback = myCallback)
    

Results format
--------------

.. code:: python

    # If you don't set a callback, your results will be returned as follows

    [
        ('DistinctName1',
            {  'FieldName':    ['value1', 'value2'],
               'AnotherField': ['value'], }),
        ('DistinctName2',
            {  'FieldName':    ['value1', 'value2'],
               'AnotherField': ['value'], }),
        ...
    ]

Conditions of Use
=================

I wrote this library for my own use, but realized others may find it useful as
there were many forum topics describing this problem.

Unfortunately I cannot guarentee any active support, but will do my best as time
permits.  That said, I'll happily accept push requests with suitable changes
that address the general audience of this library.

Put simply, use this at your own risk.  If it works, great!  If not, I may not
be able to help you.  If you fix anything, however, please push it back and I'll
likely accept it.  :-)

Also, if you use this library in your package, tool, or comercial software, let
me know, and I'll list it here!
