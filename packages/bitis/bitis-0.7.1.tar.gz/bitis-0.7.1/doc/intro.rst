==============================================
Bitis, binary timed signals processing library
==============================================

Introduction
============

**Bitis** is a python module that implements a full set of operators over
binary signals represented with BTS format. The `BTS format <./btsformat.html>`_
is a computer
memory representation of a binary signal that can have a very compact
memory footprint when the signal has a low rate of change with respect
to its sampling period.

For example, let see a typical case, a time reference signal having about
one pulse per second and one microsecond of time resolution. The BTS
format allows to completely discard the one million samples per second
between each two pulses and allows to keep in memory only the signal change
times: for each second, the time of the pulse front edge and the time of the
trailing edge.

At present, no effort is made for speed optimization and the employed
algorithms are essentially procedural. The only goal is "make it work in
some way" and understand what can be a decent set of objects/methods/functions.

BITIS is released under the GNU General Public License.

At present, version 0.7.1, BITIS is in alpha status. Any debugging aid is
welcome.

For any question, suggestion, contribution contact the author Fabrizio Pollastri <f.pollastri_a_t_inrim.it>.


Requirements
============

To run the code, **Python 2.6 or later** must
already be installed.  The latest release is recommended.  Python is
available from http://www.python.org/.

When the Signal plotting method is used also `Matplotlib`_ is required.


Installation
============

1. Open a shell.

2. Get root privileges and install the package. Command::

    pip install bitis


.. _Matplotlib: http://matplotlib.org
