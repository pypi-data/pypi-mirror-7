The verschemes package provides easy and customizable version identifier
management in Python.  It supports defining custom version schemes in a
subclass of the `Version` class.  Instances of `Version` and its subclasses are
concrete versions guaranteed to follow the rules of the class from which they
were instantiated.

The `source <https://github.com/gnuworldman/verschemes/tree/master>`_,
`documentation <http://gnuworldman.github.io/verschemes/>`_,
and `issues <https://github.com/gnuworldman/verschemes/issues>`_
are hosted on `GitHub <https://github.com/>`_.

This is an open-source project by and for the community.  Contributions,
suggestions, and questions are `welcome <https://twitter.com/BraveGnuWorld>`_
(Twitter: @bravegnuworld).

.. image:: https://travis-ci.org/gnuworldman/verschemes.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/gnuworldman/verschemes

.. image:: https://img.shields.io/coveralls/gnuworldman/verschemes.svg
   :alt: Coverage Status
   :target: https://coveralls.io/r/gnuworldman/verschemes?branch=master

NOTE
^^^^

Version 1.1 introduces a backwards-incompatible change: Version instances are
now immutable. See the `Release Notes
<http://gnuworldman.github.io/verschemes/notes.html#version-1-1>`_ for details.

Overview
========

Concept
-------

Most versioned components have their own method of identifying their versions.
This method is often termed "versioning" or called a "version scheme".  The
method is simply a set of rules that dictate what is a valid version identifier
and is usually separated (often by delimiters, such as a dot) in a number of
segments to signify hierarchy among the versions.  The hierarchy determines
ordering along with the values of the segments within the hierarchy.

Implementation
--------------

In the `verschemes` library, a version scheme is a set of rules pertaining to
the identification of versions for a given scope or purpose.  Each version
contains a number of segments often separated by delimiters.  Each segment is
allowed to have multiple fields to identify portions of the segment, though
many segments have just one field.

Many version schemes are just integers separated by dots.  The base
`Version <http://gnuworldman.github.io/verschemes/api.html#verschemes.Version>`_
class works fine for generic version numbers that fit
this scheme, but the real power of this library is in defining version schemes
(`Version` subclasses) with segments that specifically describe the scheme and
automatically implement validation and normalized rendering of a version
identifier or a sequence of version segment values.  The
`SEGMENT_DEFINITIONS <http://gnuworldman.github.io/verschemes/api.html#verschemes.Version.SEGMENT_DEFINITIONS>`_
attribute of a `Version` subclass can be used to define the specific parameters
of the version scheme that is represented by that class.

The library also contains some implementations of specific version schemes
including
`Python <https://docs.python.org/3/faq/general.html#how-does-the-python-version-numbering-scheme-work>`_,
`PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#local-version-identifiers>`_,
`PostgreSQL <http://www.postgresql.org/support/versioning/>`_, and
`X.org <http://www.x.org/wiki/Development/Documentation/VersionNumberScheme/>`_
versioning.  More are sure to be added, and submissions of version shemes for
popular, public projects/systems are welcome.  These implementations also serve
as examples for those wishing to subclass `Version` for their own (or
another's) version scheme.

Examples
========

Importing
---------

>>> from verschemes import Version
>>> from verschemes.python import PythonVersion, PythonMinorVersion
>>> from verschemes.pep440 import Pep440Version

Instantiation from a string
---------------------------

>>> Version("3.1.4")
verschemes.Version(3, 1, 4)
>>> Pep440Version("3.1.4")
verschemes.pep440.Pep440Version(None, 3, 1, 4, None, None, None, None, None, None)

Instantiation from segment values
---------------------------------

>>> Version(3, 1, 4)
verschemes.Version(3, 1, 4)
>>> PythonVersion(3, 1, 4, ["b", 5])
verschemes.python.PythonVersion(3, 1, 4, Segment(releaselevel='b', serial=5))
>>> Pep440Version(None, 3, 1, 4)
verschemes.pep440.Pep440Version(None, 3, 1, 4, None, None, None, None, None, None)

Instantiation from named segment values
---------------------------------------

>>> PythonVersion(major=3, minor=1, micro=4)
verschemes.python.PythonVersion(3, 1, 4, None)
>>> Pep440Version(release1=3, release2=1, release3=4)
verschemes.pep440.Pep440Version(None, 3, 1, 4, None, None, None, None, None, None)
>>> Pep440Version(epoch=2, release1=3, release2=1, release3=4, post_release=7)
verschemes.pep440.Pep440Version(2, 3, 1, 4, None, None, None, None, 7, None)

Rendering
---------

>>> version = Version(3, 1, 4)
>>> str(version)
'3.1.4'
>>> version.render()
'3.1.4'
>>> version = Pep440Version("3.1.4b5", epoch=2)
>>> str(version)
'2!3.1.4b5'
>>> version.render(min_release_segments=4)
'2!3.1.4.0b5'

Comparison
----------

>>> Version("3.1.4") == Version(3, 1, 4)
True
>>> Version("3.1.10") > Version("3.1.4")
True
>>> PythonVersion(3, 1, 4, ["b", 5]).minor_version == PythonMinorVersion(3, 1)
True

Normalization
-------------

>>> str(Version("3.01.0004"))
'3.1.4'
>>> str(Pep440Version("3.1.4-dev5"))
'3.1.4.dev5'
>>> str(Pep440Version("3.1.4post6"))
'3.1.4.post6'
>>> str(Pep440Version("3.1.4.RC7"))
'3.1.4c7'

.. _properties_examples:

Properties
----------

>>> version = PythonVersion(3, 1, 4, ["b", 5])
>>> version.major
3
>>> version.minor
1
>>> version.micro
4
>>> version.suffix.releaselevel
'b'
>>> version.suffix.serial
5
>>> version.is_release
True
>>> version.is_nondevelopment
False
>>> Pep440Version("3.1.4").is_release
True
>>> Pep440Version("3.1.4a2").is_release
False

Replacement
-----------

>>> version = Version(3, 1, 4)
>>> new_version = version.replace(_0=2)
>>> str(new_version)
'2.1.4'
>>> version = PythonVersion(3, 1, 4)
>>> new_version = version.replace(major=2)
>>> str(new_version)
'2.1.4'
