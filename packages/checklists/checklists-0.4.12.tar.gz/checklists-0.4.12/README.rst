Checklists
==========
Checklists is a reusable, Django app containing a full featured model and
an admin site for building web applications for managing and publishing
checklists of birds. It provides the following set of features:

  * A comprehensive model for capturing detailed information about visits made
    to a site from recording whether a specific protocol was used to count the
    birds to a breakdown of each species counted by age, sex, plumage, etc.

  * Aggregate records from other online databases, such as eBird, using feeds
    of checklists downloaded by the scrapers from the checklists_scrapers
    project.

  * A full admin application for managing the database.

  * A strong focus on data quality with the ability to selectively exclude
    specific checklists, observations or even species. Incoming checklists
    from feeds can also be filtered, for example, to selectively exclude
    checklists from specific regions or locations.

  * Autocompletion for names of locations, species, etc. for fast data entry.

  * An API to the model for easily extracting records for publication.

  * Suites of reference data, including a complete checklist for all the
    species in the world, and tools for quickly populating a new database.

  * Fully internationalized so versions supporting different languages can
    easily be created.

The project is designed to support any type of application that uses lists of
observations, from news services for publishing reports on what species have
been seen to on-line databases for observers to add their own observations.
The current focus is for managing checklists of birds however the model should
be sufficiently flexible that it can be used to record information on any type
of animal or plant.


Demo
####
The project directory has all the file required to run a django site to
demonstrate the admin site (preferably within a virtual environment):

.. code-block:: sh

    $ git clone git://github.com/StuartMacKay/checklists/
    $ cd checklists/project
    $ pip install -r requirements/demo.txt
    $ python manage.py syncdb --settings=settings.demo
    $ python manage.py migrate checklists --settings=settings.demo
    $ python manage.py migrate django_extensions --settings=settings.demo
    $ python manage.py runscript initdb --script-args pt --settings=settings.demo

An almost empty database is not very interesting, however it is easy to
populate with checklists from `eBird <http://ebird.org/>´_:

.. code-block:: sh

    $ mkdir downloads
    $ scrapy crawl ebird -a region=PT-11 -s DOWNLOAD_DIR=downloads
    $ python manage.py load_checklists  --settings=settings.demo
    $ python manage.py runserver --settings=settings.demo

eBird uses `ISO 3166-2 <https://en.wikipedia.org/wiki/ISO_3166-2>`_ codes
to identify a region. PT-11 is the code for Lisbon, Portugal. For the purposes
of getting started stick with this code for now since the list of species
loaded into the database is only for Portugal. If you choose another region
then it's likely that a checklist will contain a species not in the database
and it will fail to load.


Related projects
################
Checklists is part of a groups of apps intended to be building blocks for
creating applications:

`checklists_scrapers <http://github.com/StuartMacKay/checklists_scrapers>`_ is
a suite of web scrapers for downloading checklists from on-line databases such
as eBird (using the public API) or Birdlife International's WorldBirds network.
The downloaded checklists can then be imported into the database using the
load_checklists management command.

`checklists_api <http://github.com/StuartMacKay/checklists_api>`_ contains
extensions to the model API that are not yet sufficiently stable to be included
in the main checklists API.


Links
#####

* Documentation: http://checklists.readthedocs.org/
* Repository: https://github.com/StuartMacKay/checklists
* Package: https://pypi.python.org/pypi/checklists/
* Buildbot: http://travis-ci.org/#!/StuartMacKay/checklists

.. image:: https://secure.travis-ci.org/StuartMacKay/checklists.png?branch=master
    :target: http://travis-ci.org/StuartMacKay/checklists/


Licence
#######
Checklists is available under the modified BSD licence.