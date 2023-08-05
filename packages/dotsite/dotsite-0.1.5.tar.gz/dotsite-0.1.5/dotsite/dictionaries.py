"""Some methods to help with the handling of dictionaries"""


from collections import defaultdict


def get_caselessly(dictionary, sought):
    """Find the sought key in the given dictionary regardless of case

    >>> things = {'Fred' : 9}
    >>> print get_caselessly(things, 'fred')
    9
    """
    try:
        return dictionary[sought]
    except KeyError:
        caseless_keys = dict([(k.lower(), k) for k in dictionary.keys()])
        real_key = caseless_keys[sought.lower()]  # allow any KeyError here
        return dictionary[real_key]


def swap_dictionary(dictionary):
    """Swap keys for values in the given dictionary"""
    if not dictionary:
        return {}
    result = {}
    for k, v in dictionary.iteritems():
        result[v] = k
    return result


def append_value(dictionary, key, item):
    """Append those items to the values for that key"""
    items = dictionary.get(key, [])
    items.append(item)
    dictionary[key] = items


def extend_values(dictionary, key, items):
    """Extend the values for that key with the items"""
    values = dictionary.get(key, [])
    try:
        values.extend(items)
    except TypeError:
        raise TypeError('Expected a list, got: %r' % items)
    dictionary[key] = values


def group_list(items):
    """Items in the list are grouped into a dictionary

    Items should be a list of (key, value) pairs

    >>> grouped = group_list([(1,0), (2,0), (1,1)])
    >>> grouped[1] == [0,1]
    True
    """
    groups = defaultdict(list)
    for key, value in items:
        groups[key].append(value)
    return groups


def group_list_by(items, key_from_item):
    """Items in the list are grouped into a dictionary

    key_from_item is a method to get the key from the item

    >>> items = [(1,9), (2,8), (1,7)]
    >>> key_from_item = lambda x: 'a' if x[0] == 1 else 'b'
    >>> grouped = group_list_by(items, key_from_item)
    >>> grouped['a'] == [(1, 9), (1, 7)]
    True
    """
    groups = defaultdict(list)
    for item in items:
        key = key_from_item(item)
        groups[key].append(item)
    return groups
