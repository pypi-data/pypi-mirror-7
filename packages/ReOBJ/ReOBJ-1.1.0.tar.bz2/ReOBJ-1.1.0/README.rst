.. _LongDescription:

******************
ReOBJ: Description
******************

.. rubric:: ReOBJ:
.. rubric:: R(estricted) E(xtended) Objects. Simple, reasonable fast, restricted/extended python objects.

.. contents::
   :depth: 3


HTML Documentation
==================

HTML documentation of the project is hosted at: `ReOBJ-HTML documentation <http://reobj.readthedocs.org/>`_

Or `Package Documentation <http://pythonhosted.org//ReOBJ/>`_


Main Info
=========

**ReOBJ** contains different restricted/extended python objects.

- **ReDICTs**: Simple, reasonable fast, restricted/extended python dictionary objects.

- **ReLISTs**: Simple, reasonable fast, restricted/extended list objects.

- **ReTUPLEs**: Simple, reasonable fast, restricted/extended tuple objects.

- **ReMATRIXs**: Simple, reasonable fast, restricted/extended list-of-tuples objects.


**All `ReBASE classes - subclasses`**:

   .. warning:: for all `ReBASE classes` disabled methods

      - any class.copy()

         - e.g.: xy = myrlist.copy()

      - any class.clear()

         - e.g.: myrlist.clear()

      - any __setattr__()
      - any __delattr__()
      - any __add__()

   - can be dumped with json: but will lose any extra data like: `key_order (list)` or/and any `extra_data dict`
   - can be pickled

   - additional methods:

      - set_extra_data(), update_extra_data(), replace_extra_data(): Sets/updates key/value to the additional dictionary: `extra_data`

      - copy_recursively(): recursively copy: Supports recursively intermediate ReDICT, ReLIST, ReTUPLE, dicts, lists and tuples (and their subclasses: depending on there implementation though)

         - this will also copy any ReDICT / ReLIST / ReTUPLE / ReMATRIX `extra_data dict` and any `key_order (list)` and any `extra_key_order (list)`

      - copy_recursively_to_python_native_types(): recursively copy: changing all `ReOBJ` to native python types.

         - `RdictIO, RdictFO, RdictFO2: to python `OrderedDict obj` keeping their order (see also argument: use_extra_key_order)

         - all other ReDICT: objects will be replaced by normal python `dict objs`
         - all `ReLIST obj` will be replaced by normal python `list objs`
         - all `ReTUPLE obj` will be replaced by normal python `tuple objs`
         - all `ReMATRIX obj` will be replaced by normal python `list of tuple objs`

            .. warning::  ReMATRIX tuple items (rows) are not recursively copied so there should be no dict, list ect.. just basic types

         Supports recursively intermediate ReDICT, ReLIST, ReTUPLE, dicts, lists and tuples (and their subclasses: depending on there implementation though)

         .. note:: any ReOBJ set: `extra_data` will be lost

      - topickle(): returns a new pickled dumps byte string from the obj

      - tojson(): returns a new json dumps string from the obj

      - tojson_keeporder(): returns a new json dumps string from the obj keeping the order of any `RdictIO, RdictFO, RdictFO2`

         - this uses first the: copy_recursively_to_python_native_types()

.. warning:: comparisons do not take into consideration any `key_order (list)` or `extra_data dict`


ReDICT
------

Overview Differences
++++++++++++++++++++

- `Edict` is similar to a normal python dict but has some additional (extended) features
- `Rdict` and `RdictIO`: **can add** new items after creation/initialization
- `RdictF` and `RdictFO`, `RdictFO2`: F(ix) **can not add** new items after creation/initialization

- `Rdict` and `RdictF`: **do not have** any `key_order (list)` nor any `extra_key_order (list)`
- `RdictIO` and `RdictFO`, `RdictFO2`: O(rder) **do have** a `key_order (list)` plus an `extra_key_order (list)`

   - `RdictIO`: I(nsertion) O(rder): keeps track of the order new keys where added
   - `RdictFO`, `RdictFO2`: F(ix) O(rder): keeps track of the order of the keys when it was created/initialized

   - all three have the `extra_key_order (list)`:
      - this is a list which can be optionally set with a user defined key order (can also include just a subset of keys)

   - all three can be converted to OrderedDict: keeping their `key_order` or optionally the `extra_key_order`

      - example usage to print an ordered json using the method: tojson_keeporder()

      .. code-block:: python

         example_rdictordered = RdictFO([
            ('key1', 'value1'),
            ('key2', 'value2'),
            ('key3', RdictIO([
               ('inner_key1', 'innervalue1'),
               ('inner_key2', 'innervalue2'),
            ], False)),
         ], False)

         json_dumps = example_rdictordered.tojson_keeporder(indent=3)
         print(json_dumps)

      Output will be:

      .. code-block:: json

         {
            "key1": "value1",
            "key2": "value2",
            "key3": {
               "inner_key1": "innervalue1",
               "inner_key2": "innervalue2"
            }
         }


   - `RdictFO` vs. `RdictFO2`: RdictFO can change the values. RdictFO2 can after creation not change the values


ReLIST
------

- `Elist` is similar to a normal python list but has some additional (extended) features
- `Rlist`: **can add** new items after creation/initialization
- `RlistF`: F(ix) **can not add** new items after creation/initialization


ReTUPLE
-------

- `Etuple` is similar to a normal python tuple but has some additional (extended) features


ReMATRIX
--------

- `Lmatrix` is a List-Of-Tuples with some additional (extended) features
- `LmatrixF`: F(ix) **can not add** new items (tuple-rows) after creation/initialization


Code Examples
=============

for code examples see the files in 'development source` folders: Examples, Tests, SpeedCheck


Projects using ReOBJ
====================

`projects` which make use of: **ReOBJ**


|
|

`ReOBJ` is distributed under the terms of the BSD 3-clause license.
Consult LICENSE.rst or http://opensource.org/licenses/BSD-3-Clause.

(c) 2014, `peter1000` https://github.com/peter1000
All rights reserved.

|
|
