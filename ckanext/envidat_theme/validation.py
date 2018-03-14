def envidat_string_uppercase(key, data, errors, context):
    """
      if the value is a string, make it uppercase, otherwise leave the value as it is.
      make all tags uppercase if possible.
    """
    # Plain value to uppercase
    tags = data[key]
    if isinstance(tags, basestring):
        data[key] = tags.upper()

    # tags to uppercase
    num = 0
    tag = data.get(('tags', num, 'name'), "")
    while tag:
        data[('tags', num, 'name')] = _safe_upper(tag)
        num += 1
        tag = data.get(('tags', num, 'name'), "")

# upper or same value if it is not a string
def _safe_upper(value):
    try:
        return(value.upper())
    except:
        return value

