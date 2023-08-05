#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2014 California Institute of Technology.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/pathos/browser/klepto/LICENSE

import sys
from functools import partial
def foo(x,y,z,a=1,b=2):
    return x+y+z+a+b

from klepto import validate
p = partial(foo, 0,1)
try:
    res1 = p(1,2,3,4,b=5)
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p,1,2,3,4,b=5)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() takes at most 5 arguments (7 given)"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:20] == str(re_2)[:20]
else:
    pass # python 3.3 gives "foo() got multiple values for argument 'b'"

try:
    res1 = p()
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() takes at least 3 arguments (2 given)"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:21] == str(re_2)[:21]
else:
    pass # python 3.3 gives "foo() missing 1 required positional argument 'z'"

try:
    res1 = p(1,2,3,4,r=5)
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p,1,2,3,4,r=5)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() takes at most 5 arguments (7 given)"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:20] == str(re_2)[:20]
else:
    pass # python 3.3 gives "foo() got unexpected keyword argument 'r'"

p = partial(foo, 0,x=4)
try:
    res1 = p(1,2,3,4,r=5)
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p,1,2,3,4,r=5)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() got multiple values for keyword argument 'x'"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:25] == str(re_2)[:25]
else:
    pass # python 3.3 gives "foo() got unexpected keyword argument 'r'"

p = partial(foo, 0,1,2,3,4,5,6,7)
try:
    res1 = p()
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() takes at most 5 arguments (8 given)"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:20] == str(re_2)[:20]
else:
    pass # python 3.3 gives "foo() takes from 3 to 5 positional arguments but 8 were given"

p = partial(foo, 0,z=1,b=2)
try:
    res1 = p()
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() takes at least 3 arguments (3 given)"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:21] == str(re_2)[:21]
else:
    pass # python 3.3 gives "foo() missing 1 required positional argument: 'y'"

p = partial(foo, 0,r=4)
try:
    res1 = p(1)
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p,1)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() got an unexpected keyword argument 'r'"))
else: # all versions slightly different
    assert str(res2)[:24] == str(re_2)[:24]

p = partial(foo, 0,a=2)
try:
    res1 = p(1)
    res2 = Exception()
except:
    res1,res2 = sys.exc_info()[:2]
try:
    re_1 = validate(p,1)
    re_2 = Exception()
except:
    re_1,re_2 = sys.exc_info()[:2]
#print(res2)
#print(re_2)
assert res1 == re_1
if hex(sys.hexversion).startswith('0x207'):
    assert str(res2) == str(TypeError("foo() takes at least 3 arguments (3 given)"))
elif hex(sys.hexversion) < '0x30300f0': # all versions slightly different
    assert str(res2)[:21] == str(re_2)[:21]
else:
    pass # python 3.3 gives "foo() missing 1 required positional argument: 'z'"

assert validate(p,1,2) == None #XXX: better return ((1,2),{}) ?
'''
>>> p(1,2)
7
'''


