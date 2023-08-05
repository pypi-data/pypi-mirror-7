Changes
*******

Release 0.7.1 (released 3-Feb-2014)
===================================

Bugs fixed
----------

* Fix inequality test: missing __ne__ method.

Internals
---------

* Optimized "and" and "or" operator for constant signals.


Release 0.7.0 (released 27-Jan-2014)
====================================

Features added
--------------

* Add buf_step to method stream.
* Add return self to in place working method clone_into.

Incompatible changes
--------------------

* Change step_start, step_num with step_left, step_right in method correlation.
* Change correlation unittest from a graphic one to procedural only.


Release 0.6.0 (released 16-Dec-2013)
===================================

Features added
--------------

* Add method clone_into.
* Add method concatenate: add operator.
* Add method stream.
* Add method elapse returning the signal elapse time.
* Add example to demonstrate phase recovery from a noisy signal (lockin).
* Add examples, module reference, bts format, change log to doc pages.
* Add unittest for stream.

Incompatible changes
--------------------

* Change start level with active argument in noise method.

Bugs fixed
----------

* Fix method append: make it return the signal with the append result.
* Fix shift in correlation method.
* Fix time shift computation in correlaton method: was delayed by 1 step size.

Internals
---------

* Change method append: check arguments with assert.
* Refactor method split.


Release 0.5.0 (released 9-Dec-2013)
===================================

Features added
--------------

* Embed y limits setting into plot method.
* Add method square for signal generation of a periodc square wave.
* Add a more fine control in correlation function computation.
* Add signal append method.
* Add method start, return signal start time.
* Add method end, return signal end time.
* Add method len, return signal change times sequence length.

Incompatible changes
--------------------

* Change start times computation in bin2pwn, serial_tx to minimize
  time elapse from start to first change.

Bugs fixed
----------

* Fix 0.4.0 release changelog: missing changes.

Internals
---------

* Change noise from method to function.
* Change examples for changed noise method.


Release 0.4.0 (released 2-Dec-2013)
===================================

Features added
--------------

* Add signal split method.
* Add two signals join method.
* Add unittest for split and join.
* Add float times capability to BTS signals.

Incompatible changes
--------------------

* Uniformate pwm2bin arguments to bin2pwm methods.
* Add tscale=1. argument in bin2pwm.
* Change to tscale=1. argument in serial_tx.

Bugs fixed
----------

* Fix slevel setup, signal start and end in bin2pwm.

Internals
---------

* Rewrite jitter method.


Release 0.3.0 (released 11-Nov-2013)
====================================

Features added
--------------

* Add async serial transmitter (bits.serial_tx method) from chars to BTS
  serial line signal.
* Add async serial receiver (bitis.serial_rx method) from BTS serial line
  to chars.
* Add async serial transmitter example: serial_tx.py.
* Add unittest for async serial tx and rx.
* Modified plot method: only 0,1 ticks on y axis.


Release 0.2.0 (released 4-Nov-2013)
===================================

Features added
--------------

* Add PWM coder and decoder between a BTS signal (PWM) and a binary code.
* New correlation example.


Release 0.1.0 (released 29-Oct-2013)
====================================

* First release.
