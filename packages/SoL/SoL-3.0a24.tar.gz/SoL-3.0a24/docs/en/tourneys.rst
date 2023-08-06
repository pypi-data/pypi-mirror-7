.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:16:58 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _tourneys management:

Tourneys management
-------------------

.. index::
   pair: Management; Clubs

The *tourney* is clearly the primary element of the whole system, everything has been designed
to allow an easy and fast management of these events.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu at the top contains the
following items:

.. figure:: tourneys.png
   :figclass: float-right

   Tourneys management

:guilabel:`Details`
  Opens the :ref:`management <tourney management>` window of the selected tourney.

:guilabel:`Competitors`
  Opens the :ref:`competitors fixup` window that allows the correction of the competitors of
  old tourneys.

:guilabel:`Replay again`
  Allows *duplicating* an existing tourney, expecially handy on teams events: it basically
  clones a tourney on the current date, with all its competitors; just be sure to update the
  description, eventually adjusting the date of the event!

:guilabel:`Download`
  Downloads an archive of the selected tourney's data.


.. _tourney insert and edit:

Insert and edit
~~~~~~~~~~~~~~~

.. index::
   pair: Insert and edit; Tourney

Each tourney has a :guilabel:`date` and a :guilabel:`description` of the event and there cannot
be two dictinct tourneys in the same date associated to a single championship.

The :guilabel:`location` is optional.

The :guilabel:`duration` and :guilabel:`prealarm` refer to the length of a single turn, and are
expressed in *minutes*. They will be used by the :ref:`clock` window.

A tourney may use a particular :guilabel:`rating`: in such a case, the first turn is generated
accordingly with the rate of each player instead of using a random order.

.. _couplings:

The :guilabel:`pairing method` determines how the couplings are done at each new turn:

``Ranking order``
  the ``serial`` algorithm will try to couple a player with one of the players that follows him
  in the current ranking order, for example the first with the second, the third with the
  fourth, and so on;

``Dazed ranking order``
  to delay as much as possible most exciting matches, the ``dazed`` method is more elaborated:
  it takes the players with same points as the pivot, and tries to couple the first with the
  one in the middle of that series, the second with the middle+1 one, and so on.

The :guilabel:`phantom score` is the score assigned to a player in the matches against the
*phantom player*, when there are an odd number of competitors. By convention these matches
assign a score of 25 to the player but there may be cases where a different score is more
appropriate, for example when the number of competitors is very low and winning 25—0 would be
an unfair advantage.

The :guilabel:`responsible` is usually the user that inserted that particular tournament: the
information related to the tournament are changeable only by him (and also by the
*administrator* of the system).

.. toctree::
   :maxdepth: 2

   tourney
   competitors
