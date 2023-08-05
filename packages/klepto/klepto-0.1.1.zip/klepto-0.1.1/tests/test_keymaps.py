#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2014 California Institute of Technology.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/pathos/browser/klepto/LICENSE

from klepto.keymaps import *

args = (1,2); kwds = {"a":3, "b":4}

encode = keymap(typed=False, flat=True, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == (1, 2, 'a', 3, 'b', 4)
encode = keymap(typed=False, flat=False, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == (args, kwds)
encode = keymap(typed=True, flat=True, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == (1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4))
encode = keymap(typed=True, flat=False, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == (args, kwds, (type(1), type(2)), (type(3), type(4)))

encode = hashmap(typed=False, flat=True, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == hash((1, 2, 'a', 3, 'b', 4))
#encode = hashmap(typed=False, flat=False, sentinel=NOSENTINEL)
#assert encode(*args, **kwds) == TypeError("unhashable type: 'dict'")
encode = hashmap(typed=True, flat=True, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == hash((1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4)))
#encode = hashmap(typed=True, flat=False, sentinel=NOSENTINEL)
#assert encode(*args, **kwds) == TypeError("unhashable type: 'dict'")

encode = stringmap(typed=False, flat=True, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == "(1, 2, 'a', 3, 'b', 4)"
encode = stringmap(typed=False, flat=False, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == str((args, kwds))
encode = stringmap(typed=True, flat=True, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == str( (1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4)) )
encode = stringmap(typed=True, flat=False, sentinel=NOSENTINEL)
assert encode(*args, **kwds) == str( (args, kwds, (type(1), type(2)), (type(3), type(4))) )

from dill import dumps
encode = picklemap(typed=False, flat=True, serializer='dill')
assert encode(*args, **kwds) == dumps((1, 2, 'a', 3, 'b', 4))
encode = picklemap(typed=False, flat=False, serializer='dill')
assert encode(*args, **kwds) == dumps((args, kwds))
encode = picklemap(typed=True, flat=True, serializer='dill')
assert encode(*args, **kwds) == dumps( (1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4)) )
encode = picklemap(typed=True, flat=False, serializer='dill')
assert encode(*args, **kwds) == dumps( (args, kwds, (type(1), type(2)), (type(3), type(4))) )

