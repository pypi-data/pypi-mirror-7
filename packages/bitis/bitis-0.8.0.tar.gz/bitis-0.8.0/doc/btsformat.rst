==========
BTS format
==========

Definition
----------

The scope of this memo is to describe the BTS, Binary Timed Signal. A format
for compact storage of binary signals in computer memory.
Binary signals are signal that can have only two levels/states, zero or one.

The *BTS* format is composed by 3 elements.

1. The change times.
2. The start level.
3. The time scale.

**Change times**

This sequence stores all the times where the signal changes its level from
0 to 1 or viceversa. The first and the last sequence items have a different
meaning: they are respectively the start time and the end time of the signal.
The signal start and end are the boundaries of the signal domain. Outside
this interval, the signal is to be itended as not defined.
The change times sequence may be empty: in this case the signal must
be threated as empty or null. The sequence may have 2 items: in this case
the signal has a constant level along all its domain and there are no level
changes. The sequence may have 3 or more items: in this case the signal has
1 or more level changes. A sequence with only one item is not allowed.
The sequence must be sorted in ascending order.

**Start level**

If the change times sequence has 3 or more items, the start level value
specifies the signal level from the signal start time to the first change time.
If the change times sequence has 2 items, the signal has a constant level
that is equal to the start level value.

**Time scale**

An arbitrary unit of time can be chosen to express the values of change times.
The time scale value is the ratio: 1 second / arbitrary time unit.


Python implementation
---------------------

**BITIS** implements the *BTS* format with the *Signal* class. Each BTS
signal is an instance of this class. The three elements of the BTS format
are the three attributes (*times, slevel, tscale*) of the *Signal* class.
The sequence *times* is realized as list of integers or floats.
