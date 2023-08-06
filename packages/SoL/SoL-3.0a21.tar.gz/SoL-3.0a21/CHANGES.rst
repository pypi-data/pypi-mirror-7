Changes
-------

3.0a21 (2014-06-13)
~~~~~~~~~~~~~~~~~~~

* Change the logic used to determine the current rate of a player, considering only
  the referenced rating and, when inherit is active, those at an higher level, not
  at the same level


3.0a20 (2014-06-12)
~~~~~~~~~~~~~~~~~~~

* Fix generation of first turn when number of turns when the number of players is odd

* Fix reordering of first turn combinations when the number of players is odd


3.0a19 (2014-06-10)
~~~~~~~~~~~~~~~~~~~

* Fix the formula used to compute matches outcome, using the whole range of values
  from 0 to 1 instead of just 0, 0.5 and 1

* Parametrize the lower and higher range of the interval used to interpolate players
  rates when the tourney's competitors are (almost) all unrated


3.0a18 (2014-05-24)
~~~~~~~~~~~~~~~~~~~

* New printout with the results of all played turns

* Fix database upgrade logic


3.0a17 (2014-05-16)
~~~~~~~~~~~~~~~~~~~

* Fix tourneys export, forgot to include the new phantomscore field


3.0a16 (2014-05-16)
~~~~~~~~~~~~~~~~~~~

* Show also the player's club after his name in the ranking printout

* Allow customization of the score assigned to players in phantom matches

* Do not delete historical rates when recomputing from scratch non-inheriting
  ratings


3.0a15 (2014-04-25)
~~~~~~~~~~~~~~~~~~~

* Add an inherit flag to ratings, so the lookup behaviour for player's rate lookup
  is a user choice

* Align the two versions of the user manual

* Minor tweaks to the lit interface


3.0a14 (2014-04-06)
~~~~~~~~~~~~~~~~~~~

* Fix glitch in player's rate lookup


3.0a13 (2014-04-05)
~~~~~~~~~~~~~~~~~~~

* Fix PDF printouts font usage, using DejaVuSans also for the page decorations

* ``soladmin create-config`` now asks for the admin password, instead of
  generating it randomly


3.0a12 (2014-04-04)
~~~~~~~~~~~~~~~~~~~

* Fix glitch in the configuration template


3.0a11 (2014-04-04)
~~~~~~~~~~~~~~~~~~~

* Fix overlaps in score cards printout

* ``soladmin load-historical-rating`` is now able to use arbitrary formulas
  to compute rate, deviation and volatility


3.0a10 (2014-03-31)
~~~~~~~~~~~~~~~~~~~

* Do not translate log messages

* More detailed log of applied changes

* Do not clobber existing information from an uploaded archive, as SoL 2 did

* Impose a lower limit of 800 to the player's rates computed by Glicko2


3.0a9 (2014-03-28)
~~~~~~~~~~~~~~~~~~

* Explicitly require Pillow, since ReportLab 3.0 does not


3.0a8 (2014-03-22)
~~~~~~~~~~~~~~~~~~

* Tested on Python 3.4

* Require nssjson instead of simplejson

* Minor tweaks to the player window, changing default fields visibility and
  slightly taller to show 23 records at a time


3.0a7 (2014-03-17)
~~~~~~~~~~~~~~~~~~

* Automatic check of the release date in CHANGES.rst

* Fix compatibility with Python 3.4 using Chameleon 2.15

* Fix another glitch when the guest user is not defined in the configuration


3.0a6 (2014-03-08)
~~~~~~~~~~~~~~~~~~

* Add a link to this section (on PyPI) to the login panel


3.0a5 (2014-03-06)
~~~~~~~~~~~~~~~~~~

* New command to update an existing configuration file


3.0a4 (2014-03-06)
~~~~~~~~~~~~~~~~~~

* Fix minor deploy issue with metapensiero.extjs.desktop


3.0a3 (2014-03-06)
~~~~~~~~~~~~~~~~~~

* Tweak the deployment infrastructure

* Change package description to improve the chance it gets found

* Some work on the user manuals


3.0a2 (2014-03-04)
~~~~~~~~~~~~~~~~~~

* Fix various deploy related issues


3.0a1 (2014-03-03)
~~~~~~~~~~~~~~~~~~

* Let's try the release process!


Version 3
~~~~~~~~~

* Ported to Python 3.3 and to ExtJS 4.2

* Built on `metapensiero.extjs.desktop`__ and `metapensiero.sqlalchemy.proxy`__

  __ https://pypi.python.org/pypi/metapensiero.extjs.desktop
  __ https://pypi.python.org/pypi/metapensiero.sqlalchemy.proxy

* Version control moved from darcs__ to git__ (darcs is beautiful, but git is more powerful and
  many more people use it)

  __ http://darcs.net/
  __ http://git-scm.com/

* It tooks almost one year and more than 760 changesets (still counting!)...


Highlights
++++++++++

* Glicko2__ ratings, with graphical charts

  __ http://en.wikipedia.org/wiki/Glicko_rating_system

* Old `championships` are gone, old `seasons` has been renamed to `championships`

  People got confused by the overlapping functionality, old championships were an attempt to
  compute national-wide rankings: the new Glicko2-based ratings are much better at that

* Augmented players information to fit international tourneys requirements, clubs may be marked
  as `federations`

* Easier interfaces to insert and modify

* Easier way to upload players portraits and clubs logos

* Hopefully easier installation

* Better infrastructure to accomodate database migrations

* Simpler way to detect potential duplicated players

* Most entities carry a ``GUID`` that make it possible to reliably match them when imported
  from a different SoL instance

* Players merges are tracked and distribuited to other SoL instances


Dark ages
~~~~~~~~~

``Scarry`` was a `Delphi 5`__ application I wrote years ago, with the equivalent goal. It
started as a "quick and dirty" solution to the problem, and Delphi was quite good at that. It
has served us with good enough reliability for years, but since programming in that environment
really bored me to death, there's no way I could be convinced to enhance it further.

``SoL`` is a complete reimplementation, restarting from scratch: it uses exclusively `free
software`__ components, so that I won't be embaraced to public the whole source code.

__ http://en.wikipedia.org/wiki/Borland_Delphi
__ http://en.wikipedia.org/wiki/Free_software
