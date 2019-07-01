from ckantoolkit import _

import ckan.lib.navl.dictization_functions as df
StopOnError = df.StopOnError


def envidat_shortname_validator(key, data, errors, context):

    value = data.get(key)
    if not value or len(value) > 80:
        errors[key].append(_('text should be maximum 80 characters long'))
        raise StopOnError

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


def envidat_minimum_tag_count(key, data, errors, context):
    """
      count tags and raise an error if there are less than 5
    """
    min_tags = 5
    # tags to count
    num = 0
    tag = data.get(('tags', num, 'name'), "")
    while tag:
        num += 1
        tag = data.get(('tags', num, 'name'), "")

    if num < min_tags:
        errors[key].append(_('at least ' + str(min_tags) + ' tags'))
        raise StopOnError


# upper or same value if it is not a string
def _safe_upper(value):
    try:
        return(value.upper())
    except:
        return value

