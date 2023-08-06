spliterator
===========

Split line streams into managable chunks

Usage
=====

Take things.txt as follows.

..  code:: text

    Thing Name Thing 1
    Thing Color Red
    Thing Hair Big
    Thing Motto I am Number 1!
    Thing Name Thing 2
    Thing Color Red
    Thing Hair Big
    Thing Motto Seconds Please!

And lets iterate through each line while adding in start and end events around each individual thing.

..  code:: python

    >>> import spliterator
    >>> for event, line in spliterator.chunk(open('things.txt'), 'Thing Name'):
    ...   print(event, line)
    ... 
    START None
    LINE Thing Name Thing 1
    LINE Thing Color Red
    LINE Thing Hair Big
    LINE Thing Motto I am Number 1!
    END None
    START None
    LINE Thing Name Thing 2
    LINE Thing Color Red
    LINE Thing Hair Big
    LINE Thing Motto Seconds Please!
    END None
    
Now we can process specific things properly based on the event variable.
