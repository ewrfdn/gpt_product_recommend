def pick_value(value_dict, keys, default=None, filter_none=False):
    if default is None:
        default = {}
    res = {}
    for key in keys:
        val = value_dict.get(key)
        if val is None or val == '':
            val = default.get(key)
        if filter_none:
            if val is not None:
                res[key] = val
        else:
            res[key] = val
    return res
