==========
c (urcalc)
==========

*c* is a simple calculator in terminal using Urwid_, created solely for big
buttons to click with mouse button, not meant to be having complex arithmetic
operations, just basic ``+-*/``.

.. _Urwid: http://urwid.org/
.. figure:: https://bytebucket.org/livibetter/c/raw/tip/c.png

This project's name is "c," however, in order to register on PyPI_, it uses
"urcalc" as the PyPI package name. ``c`` is also the command to invoke the
calculator.


.. contents:: **Contents**
   :local:


Installation
============

You can install via ``pip``:

.. code:: sh

  $ pip install c
  $ c


Dependencies
------------

* Python 3
* Urwid_


Controls
========

Beside ``LMB`` (Left Mouse Button) to press button on screen, there are also
keyboard controls as listed below:

+------------------------+--------------------------+
| key                    | action                   |
+========================+==========================+
| ``Enter`` or ``Space`` | press focused button     |
+------------------------+--------------------------+
| arrow keys             | navigate through buttons |
+------------------------+--------------------------+
| ``0`` to ``9``         | enter the digit          |
+------------------------+--------------------------+
| ``Backspace``          | remove lowest digit      |
+------------------------+--------------------------+
| ``N``                  | change sign              |
+------------------------+--------------------------+
| ``.``                  | begin fractional part    |
+------------------------+--------------------------+
| ``=``                  | get answer               |
+------------------------+--------------------------+
| ``C``, ``Escape``      | clear                    |
+------------------------+--------------------------+
| ``Q``                  | quit                     |
+------------------------+--------------------------+


Links
=====

* Bitbucket_
* PyPI_

.. _Bitbucket: https://bitbucket.org/livibetter/c
.. _PyPI: https://pypi.python.org/pypi/urcalc


Copyright
=========

This project is licensed under the MIT License, see COPYING_.

.. _COPYING: https://bitbucket.org/livibetter/c/src/tip/COPYING
