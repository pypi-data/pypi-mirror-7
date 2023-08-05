'''
Created on 26 May 2013

@author: lukasz.forynski

@brief: Implementation of the multi-key dictionary.

https://github.com/formiaczek/python_data_structures
___________________________________

 Copyright (c) 2013 Lukasz Forynski <lukasz.forynski@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sub-license, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
'''

class multi_key_dict(object):
    """ Purpose of this type is to provie a multi-key dictionary.
    This kind of dictionary has a similar interface to the standard dictionary, and indeed if used 
    with single key key elements - it's behaviour is the same as for a standard dict().

    However it also allows for creation elements using multiple keys (using tuples/lists).
    Such elements can be accessed using either of those keys (e.g read/updated/deleted).
    Dictionary provides also extended interface for iterating over items and keys by the key type.
    This can be useful e.g.: when creating dictionaries with (index,name) allowing to iterate over
    items using either: names or indexes. It can be useful for many many other similar use-cases,
    and there is no limit to the number of keys used to map to the value.

    There are also methods to find other keys mapping to the same value as the specified keys etc.
    Refer to examples and test code to see it in action.

    simple example:
        k = multi_key_dict()
        k[100] = 'hundred'  # add item to the dictionary (as for normal dictionary)

        # but also:
        # below creates entry with two possible key types: int and str, 
        # mapping all keys to the assigned value
        k[1000, 'kilo', 'k'] = 'kilo (x1000)'
        print k[1000]   # will print 'kilo (x1000)'
        print k['k']  # will also print 'kilo (x1000)'
        
        # the same way objects can be updated, and if an object is updated using one key, the new value will
        # be accessible using any other key, e.g. for example above:
        k['kilo'] = 'kilo'
        print k[1000] # will print 'kilo' as value was updated
    """
    
    def __init__(self, mapping_or_iterable=None, **kwargs):
        """ Initializes dictionary from an optional positional argument and a possibly empty set of keyword arguments."""
        if mapping_or_iterable is not None:
            if type(mapping_or_iterable) is dict:
                mapping_or_iterable = mapping_or_iterable.items()
            for kv in mapping_or_iterable:
                if len(kv) != 2:
                    raise Exception('Iterable should contain tuples with exactly two values but specified: {0}.'.format(kv))
                self[kv[0]] = kv[1]
        for keys, value in kwargs.iteritems():
            self[keys] = value

    def __getitem__(self, key):
        """ Return the value at index specified as key."""
        if self.has_key(key):
            return self.items_dict[self.__dict__[str(type(key))][key]]
        else:
            raise KeyError(key)

    def __setitem__(self, keys, value):
        """ Set the value at index (or list of indexes) specified as keys.
            Note, that if multiple key list is specified, either: 
              - none of keys should map to an existing item already (item creation), or 
              - all of keys should map to exactly the same item (as previously created)
                  (item update)
            If this is not the case - KeyError is raised. """
        if(type(keys) in [tuple, list]):
            num_of_keys_we_have = reduce(lambda x, y: x+y, map(lambda x : self.has_key(x), keys))
            if num_of_keys_we_have:
                all_select_same_item = True
                direct_key = None
                for key in keys:
                    key_type = str(type(key))
                    try:
                        if not direct_key:
                            direct_key = self.__dict__[key_type][key]
                        else:
                            new = self.__dict__[key_type][key]
                            if new != direct_key:
                                all_select_same_item = False
                                break
                    except Exception, err:
                        all_select_same_item = False
                        break;

                if not all_select_same_item:
                    raise KeyError(', '.join(str(key) for key in keys))

            first_key = keys[0] # combination if keys is allowed, simply use the first one
        else:
            first_key = keys

        key_type = str(type(first_key)) # find the intermediate dictionary..
        if self.has_key(first_key):
            self.items_dict[self.__dict__[key_type][first_key]] = value # .. and update the object if it exists..
        else:
            if(type(keys) not in [tuple, list]):
                key = keys
                keys = [keys]
            self.__add_item(value, keys) # .. or create it - if it doesn't

    def __delitem__(self, key):
        """ Called to implement deletion of self[key]."""
        key_type = str(type(key))
        if (self.has_key(key) and
            self.items_dict and
            self.items_dict.has_key(self.__dict__[key_type][key])):
            intermediate_key = self.__dict__[key_type][key]

            # remove the item in main dictionary 
            del self.items_dict[intermediate_key]

            # remove all references (also pointed by other types of keys)
            # for the item that this key pointed to.
            for name, reference_dict in self.__dict__.iteritems():
                if(type(name) == str and name.find('<type') == 0):
                    ref_key = None
                    for temp_key, value in reference_dict.iteritems():
                        if value == intermediate_key:
                            ref_key = temp_key
                            break
                    if ref_key:
                        del reference_dict[ref_key]
        else:
            raise KeyError(key)

    def has_key(self, key):
        """ Returns True if this object contains an item referenced by the key."""
        key_type = str(type(key))
        if self.__dict__.has_key(key_type):
            if self.__dict__[key_type].has_key(key):
                return True
        return False

    def get_other_keys(self, key, including_current=False):
        """ Returns list of other keys that are mapped to the same value as specified key. 
            @param key - key for which other keys should be returned.
            @param including_current if set to True - key will also appear on this list."""
        other_keys = []
        if self.has_key(key):
            other_keys.extend(self.__dict__[str(type(key))][key])
            if not including_current:
                other_keys.remove(key)
        return other_keys

    def iteritems(self, key_type=None, return_all_keys=False):
        """ Returns an iterator over the dictionary's (key, value) pairs.
            @param key_type if specified, iterator will be returning only (key,value) pairs for this type of key.
                   Otherwise (if not specified) ((keys,...), value) 
                   i.e. (tuple of keys, values) pairs for all items in this dictionary will be generated.
            @param return_all_keys if set to True - tuple of keys is retuned instead of a key of this type."""
        if key_type is not None:
            key = str(key_type)
            if self.__dict__.has_key(key):
                for key, keys in self.__dict__[key].iteritems():
                    if return_all_keys:
                        yield keys, self.items_dict[keys]
                    else:
                        yield key, self.items_dict[keys]
        else:
            for keys, value in self.items_dict.iteritems():
                yield keys, value

    def iterkeys(self, key_type=None, return_all_keys=False):
        """ Returns an iterator over the dictionary's keys.
            @param key_type if specified, iterator for a dictionary of this type will be used. 
                   Otherwise (if not specified) tuples containing all (multiple) keys
                   for this dictionary will be generated.
            @param return_all_keys if set to True - tuple of keys is retuned instead of a key of this type."""
        if(key_type is not None):
            the_key = str(key_type)
            if self.__dict__.has_key(the_key):
                for key in self.__dict__[the_key].iterkeys():
                    if return_all_keys:
                        yield self.__dict__[the_key][key]
                    else:
                        yield key            
        else:
            for keys in self.items_dict.keys():
                yield keys

    def itervalues(self, key_type=None):
        """ Returns an iterator over the dictionary's values.
            @param key_type if specified, iterator will be returning only values pointed by keys of this type.
                   Otherwise (if not specified) all values in this dictinary will be generated."""
        if(key_type is not None):
            intermediate_key = str(key_type)
            if self.__dict__.has_key(intermediate_key):
                for direct_key in self.__dict__[intermediate_key].itervalues():
                    yield self.items_dict[direct_key]
        else:
            for value in self.items_dict.itervalues():
                yield value

    def items(self, key_type=None, return_all_keys=False):
        """ Return a copy of the dictionary's list of (key, value) pairs.
            @param key_type if specified, (key, value) pairs for keys of this type will be returned.
                 Otherwise list of pairs: ((keys), value) for all items will be returned.
            @param return_all_keys if set to True - tuple of keys is retuned instead of a key of this type."""
        all_items = []
        if key_type is not None:
            keys_used_so_far = set()
            direct_key = str(key_type)
            if self.__dict__.has_key(direct_key):
                for key, keys in self.__dict__[direct_key].iteritems():
                    if not keys in keys_used_so_far:
                        keys_used_so_far.add(keys)
                        if return_all_keys:
                            all_items.append((keys, self.items_dict[keys]))
                        else:
                            all_items.append((key, self.items_dict[keys]))
        else:
            for keys, value in self.items_dict.iteritems():
                all_items.append((keys, value))
        return all_items

    def keys(self, key_type=None):
        """ Returns a copy of the dictionary's keys.
            @param key_type if specified, only keys for this type will be returned.
                 Otherwise list of tuples containing all (multiple) keys will be returned."""
        if key_type is not None:
            intermediate_key = str(key_type)
            if self.__dict__.has_key(intermediate_key):
                return self.__dict__[intermediate_key].keys()
        else:
            # keys will contain lists of keys
            all_keys = []
            for keys in self.items_dict.keys():
                all_keys.append(keys)
            return all_keys

    def values(self, key_type=None):
        """ Returns a copy of the dictionary's values.
            @param key_type if specified, only values pointed by keys of this type will be returned.
                 Otherwise list of all values contained in this dictionary will be returned."""
        if(key_type is not None):
            all_items = []
            keys_used = set()
            direct_key = str(key_type)
            if self.__dict__.has_key(direct_key):
                for intermediate_key in self.__dict__[direct_key].itervalues():
                    if not intermediate_key in keys_used:
                        all_items.append(self.items_dict[intermediate_key])
                        keys_used.add(intermediate_key)
            return all_items
        else:
            return self.items_dict.values()

    def __len__(self):
        """ Returns number of objects in dictionary."""
        length = 0
        if self.__dict__.has_key('items_dict'):
            length = len(self.items_dict)
        return length

    def __add_item(self, item, keys=None):        
        """ Internal method to add an item to the multi-key dictionary"""
        if(not keys or not len(keys)):
            raise Exception('Error in %s.__add_item(%s, keys=tuple/list of items): need to specify a tuple/list containing at least one key!'
                            % (self.__class__.__name__, str(item)))
        direct_key = tuple(keys) # put all keys in a tuple, and use it as a key
        for key in keys:
            key_type = str(type(key))

            # store direct key as a value in an intermediate dictionary
            if(not self.__dict__.has_key(key_type)):
                self.__setattr__(key_type, dict())
            self.__dict__[key_type][key] = direct_key
         
            # store the value in the actual dictionary
            if(not self.__dict__.has_key('items_dict')):
                self.items_dict = dict()            
            self.items_dict[direct_key] = item

    def get(self, key, default=None):
        """ Return the value at index specified as key."""
        if self.has_key(key):
            return self.items_dict[self.__dict__[str(type(key))][key]]
        else:
            return default

    def __str__(self):
        items = []
        str_repr = lambda x: '\'%s\'' % x if type(x) == str else str(x)
        if hasattr(self, 'items_dict'):
            for (keys, value) in self.items():
                keys_str = [str_repr(k) for k in keys]
                items.append('(%s): %s' % (', '.join(keys_str),
                                           str_repr(value)))
        dict_str = '{%s}' % ( ', '.join(items))
        return dict_str

def test_multi_key_dict():
    contains_all = lambda cont, in_items: not (False in [c in cont for c in in_items])

    m = multi_key_dict()
    assert( len(m) == 0 ), 'expected len(m) == 0'
    all_keys = list()

    m['aa', 12, 32, 'mmm'] = 123  # create a value with multiple keys..
    assert( len(m) == 1 ), 'expected len(m) == 1'
    all_keys.append(('aa', 'mmm', 32, 12)) # store it for later

    # try retrieving other keys mapped to the same value using one of them
    res = m.get_other_keys('aa')
    assert(contains_all(res, ['mmm', 32, 12])), 'get_other_keys(\'aa\'): %s other than expected: %s ' % (m, ['mmm', 32, 12])
    
    # try retrieving other keys mapped to the same value using one of them: also include this key
    res = m.get_other_keys(32, True)
    assert(contains_all(res, ['aa', 'mmm', 32, 12])), 'get_other_keys(32): %s other than expected: %s ' % (res, ['aa', 'mmm', 32, 12])

    assert( m.has_key('aa') == True ), 'expected m.has_key(\'aa\') == True'
    assert( m.has_key('aab') == False ), 'expected m.has_key(\'aab\') == False'

    assert( m.has_key(12) == True ), 'expected m.has_key(12) == True'
    assert( m.has_key(13) == False ), 'expected m.has_key(13) == False'
    assert( m.has_key(32) == True ), 'expected m.has_key(32) == True'

    m['something else'] = 'abcd'
    assert( len(m) == 2 ), 'expected len(m) == 2'
    all_keys.append(('something else',)) # store for later

    m[23] = 0
    assert( len(m) == 3 ), 'expected len(m) == 3'
    all_keys.append((23,)) # store for later

    # check if it's possible to read this value back using either of keys
    assert( m['aa'] == 123 ), 'expected m[\'aa\'] == 123'
    assert( m[12] == 123 ), 'expected m[12] == 123'
    assert( m[32] == 123 ), 'expected m[32] == 123'
    assert( m['mmm'] == 123 ), 'expected m[\'mmm\'] == 123'

    # now update value and again - confirm it back - using different keys..
    m['aa'] = 45
    assert( m['aa'] == 45 ), 'expected m[\'aa\'] == 45'
    assert( m[12] == 45 ), 'expected m[12] == 45'
    assert( m[32] == 45 ), 'expected m[32] == 45'
    assert( m['mmm'] == 45 ), 'expected m[\'mmm\'] == 45'

    m[12] = '4'
    assert( m['aa'] == '4' ), 'expected m[\'aa\'] == \'4\''
    assert( m[12] == '4' ), 'expected m[12] == \'4\''

    # test __str__
    m_str_exp = '{(23): 0, (\'aa\', \'mmm\', 32, 12): \'4\', (\'something else\'): \'abcd\'}'
    m_str = str(m)
    assert (len(m_str) > 0), 'str(m) should not be empty!'    
    assert (m_str[0] == '{'), 'str(m) should start with \'{\', but does with \'%c\'' % m_str[0]
    assert (m_str[-1] == '}'), 'str(m) should end with \'}\', but does with \'%c\'' % m_str[-1]

    # check if all key-values are there as expected. THey might be sorted differently
    def get_values_from_str(dict_str):
        sorted_keys_and_value = []
        for k in dict_str.split(', ('):
            keys, val = k.strip('{}() ').replace(')', '').split(':')
            keys = sorted([k.strip() for k in keys.split(',')])
            sorted_keys_and_value.append((keys, val))
        return sorted_keys_and_value
    exp = get_values_from_str(m_str_exp)
    act = get_values_from_str(m_str)
    assert (contains_all(act, exp)), 'str(m) values: \'{0}\' are not {1} '.format(act, exp)

    # try accessing / creating new (keys)-> value mapping whilst one of these
    # keys already maps to a value in this dictionarys
    try:
        m['aa', 'bb'] = 'something new'
        assert(False), 'Should not allow adding multiple-keys when one of keys (\'aa\') already exists!'
    except KeyError, err:
        pass

    # now check if we can get all possible keys (formed in a list of tuples
    # each tuple containing all keys)
    res = sorted([sorted(k) for k in m.keys()])
    all_keys = sorted([sorted(k) for k in all_keys])
    assert(contains_all(res, all_keys)), 'unexpected values from m.keys(), got:\n%s\n expected:\n%s)' %(res, all_keys) 

    # check default iteritems (which will unpack tupe with key(s) and value)
    all_keys = [sorted(k) for k in all_keys]
    num_of_elements = 0
    for keys, value in m.iteritems():
        num_of_elements += 1
        assert(sorted(keys) in all_keys), 'm.iteritems(): unexpected keys: %s' % (keys)
        assert(m[keys[0]] == value), 'm.iteritems(): unexpected value: %s (keys: %s)' % (value, keys)
    assert(num_of_elements > 0), 'm.iteritems() returned generator that did not produce anything'

    # test default iterkeys()
    num_of_elements = 0
    for keys in m.iterkeys():
        num_of_elements += 1
        assert(sorted(keys) in all_keys), 'm.iterkeys(): unexpected keys: %s' % (keys)
    assert(num_of_elements > 0), 'm.iterkeys() returned generator that did not produce anything'

    # test iterkeys(int, True): useful to get all info from the dictionary
    # dictionary is iterated over the type specified, but all keys are returned.
    num_of_elements = 0
    for keys in m.iterkeys(int, True):
        num_of_elements += 1
        assert(sorted(keys) in all_keys), 'm.iterkeys(int, True): unexpected keys: %s' % (keys)
    assert(num_of_elements > 0), 'm.iterkeys(int, True) returned generator that did not produce anything'

    # test values for different types of keys()
    values_for_int_keys = sorted([0, '4'])
    assert (sorted(m.values(int)) == values_for_int_keys), 'm.values(int) are %s, but expected: %s.' % (sorted(m.values(int)), 
                                                                                                          values_for_int_keys)
    values_for_str_keys = sorted(['4', 'abcd'])
    assert (sorted(m.values(str)) == values_for_str_keys), 'm.values(str) are %s, but expected: %s.' % (sorted(m.values(str)), 
                                                                                                          values_for_str_keys)
    current_values = sorted([0, '4', 'abcd']) # default (should give all values)
    assert (sorted(m.values()) == current_values), 'm.values() are %s, but expected: %s.' % (sorted(m.values()),
                                                                                                    current_values)

    #test itervalues() (default) - should return all values. (Itervalues for other types are tested below)
    vals = []
    for value in m.itervalues():
        vals.append(value)
    assert (current_values == sorted(vals)), 'itervalues(): expected %s, but collected %s' % (current_values, sorted(vals))

    #test items(int)
    items_for_int = sorted([(32, '4'), (23, 0)])
    assert (items_for_int == sorted(m.items(int))), 'items(int): expected %s, but collected %s' % (items_for_int, 
                                                                                                     sorted(m.items(int)))

    # test items(str)
    items_for_str = sorted([('aa', '4'), ('something else', 'abcd')])
    assert (items_for_str == sorted(m.items(str))), 'items(str): expected %s, but collected %s' % (items_for_str, 
                                                                                                     sorted(m.items(str)))
    # test items() (default - all items)
    all_items = [((('aa', 12, 32, 'mmm'), '4')), (('something else',), 'abcd'), ((23,), 0)]
    all_items = sorted([sorted(k) for k in [sorted(kk) for kk in all_items]])
    res = sorted([sorted(k) for k in m.items()])
    assert (all_items == res), 'items() (all items): expected %s,\n\t\t\t\tbut collected %s' % (all_items, res)

    # now test deletion..
    curr_len = len(m)
    del m[12]
    assert( len(m) == curr_len - 1 ), 'expected len(m) == %d' % (curr_len - 1)

    # try again 
    try:
        del m['aa']
        assert(False), 'cant remove again: item m[\'aa\'] should not exist!'
    except KeyError, err:
        pass

    # try to access non-existing 
    try:
        k =  m['aa']
        assert(False), 'removed item m[\'aa\'] should exist!'
    except KeyError, err:
        pass

    # try to access non-existing with a different key 
    try:
        k =  m[12]
        assert(False), 'removed item m[12] should exist!'
    except KeyError, err:
        pass

    # prepare for other tests (also testing creation of new items)
    tst_range = range(10, 40) + range(50, 70)
    for i in tst_range:
        m[i] = i # will create a dictionary, where keys are same as items

    # test iteritems()
    for key, value in m.iteritems(int):
        assert(key == value), 'iteritems(int): expected %d, but received %d' % (key, value)

    # test iterkeys()
    num_of_elements = 0
    curr_index_in_range = 0
    for key in m.iterkeys(int):
        expected = tst_range[curr_index_in_range]
        assert (key == expected), 'iterkeys(int): expected %d, but received %d' % (expected, key)
        curr_index_in_range += 1
        num_of_elements += 1
    assert(num_of_elements > 0), 'm.iteritems(int) returned generator that did not produce anything'

    #test itervalues(int)
    curr_index_in_range = 0
    num_of_elements = 0
    for value in m.itervalues(int):
        expected = tst_range[curr_index_in_range]
        assert (value == expected), 'itervalues(int): expected %d, but received %d' % (expected, value)
        curr_index_in_range += 1
        num_of_elements += 1
    assert(num_of_elements > 0), 'm.itervalues(int) returned generator that did not produce anything'

    # test values(int)
    assert (m.values(int) == tst_range), 'm.values(int) is not as expected.'

    # test keys()
    assert (m.keys(int) == tst_range), 'm.keys(int) is not as expected.'

    # test setitem with multiple keys
    m['xy', 999, 'abcd'] = 'teststr'
    try:
        m['xy', 998] = 'otherstr'
        assert(False), 'creating / updating m[\'xy\', 998] should fail!'
    except KeyError, err:
        pass

    # test setitem with multiple keys
    m['cd'] = 'somethingelse'
    try:
        m['cd', 999] = 'otherstr'
        assert(False), 'creating / updating m[\'cd\', 999] should fail!'
    except KeyError, err:
        pass

    m['xy', 999] = 'otherstr'
    assert (m['xy']  == 'otherstr'), 'm[\'xy\'] is not as expected.'
    assert (m[999]   == 'otherstr'), 'm[999] is not as expected.'
    assert (m['abcd'] == 'otherstr'), 'm[\'abcd\'] is not as expected.'

    m['abcd', 'xy']   =  'another'
    assert (m['xy']  == 'another'), 'm[\'xy\'] is not == \'another\'.'
    assert (m[999]   == 'another'), 'm[999] is not == \'another\''
    assert (m['abcd'] == 'another'), 'm[\'abcd\'] is not  == \'another\'.'

    # test get functionality of basic dictionaries
    m['CanIGet'] = 'yes'
    assert (m.get('CanIGet') == 'yes')
    assert (m.get('ICantGet') == None)
    assert (m.get('ICantGet', "Ok") == "Ok")

    k = multi_key_dict()
    k['1:12', 1] = 'key_has_:'
    k.items() # should not cause any problems to have : in key
    assert (k[1] == 'key_has_:'), 'k[1] is not equal to \'abc:def:ghi\''

    import datetime
    n = datetime.datetime.now()
    l = multi_key_dict()
    l[n] = 'now' # use datetime obj as a key

    #test keys..
    r = l.keys()[0]
    assert(r == (n,)), 'Expected {0} (tuple with all key types) as a 1st key, but got: {1}'.format((n,), r)

    r = l.keys(datetime.datetime)[0]
    assert(r == n), 'Expected {0} as a key, but got: {1}'.format(n, r)
    assert(l.values() == ['now']), 'Expected values: {0}, but got: {1}'.format(l.values(), 'now')

    # test items..
    exp_items = [((n,), 'now')]
    r = l.items()
    assert(r == exp_items), 'Expected for items(): tuple of keys: {0}, but got: {1}'.format(r, exp_items) 
    assert(exp_items[0][1] == 'now'), 'Expected for items(): value: {0}, but got: {1}'.format('now', 
                                                                                              exp_items[0][1])

    x = multi_key_dict({('k', 'kilo'):1000, ('M', 'MEGA', 1000000):1000000}, milli=0.01)
    assert (x['k'] == 1000), 'x[\'k\'] is not equal to 1000'
    x['kilo'] = 'kilo'
    assert (x['kilo'] == 'kilo'), 'x[\'kilo\'] is not equal to \'kilo\''

    y = multi_key_dict([(('two', 'duo'), 2), (('one', 'uno'), 1), ('three', 3)])

    assert (y['two'] == 2), 'y[\'two\'] is not equal to 2'
    y['one'] = 'one'
    assert (y['one'] == 'one'), 'y[\'one\'] is not equal to \'one\''

    try:
        y = multi_key_dict([(('two', 'duo'), 2), ('one', 'uno', 1), ('three', 3)])
        assert(False), 'creating dictionary using iterable with tuples of size > 2 should fail!'
    except:
        pass

    print 'All test passed OK!'

if __name__ == '__main__':
    try:
        test_multi_key_dict()
    except KeyboardInterrupt:
        print '\n(interrupted by user)'

