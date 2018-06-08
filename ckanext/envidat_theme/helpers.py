import json
import time
import datetime

import hashlib

import ckan.plugins.toolkit as toolkit

from ckanext.hierarchy import helpers
import ckan.plugins as p

from ckan.common import c

import logging
logger = logging.getLogger(__name__)

def _envidat_theme_get_hash(text):
     #logger.debug('Hashing ' + str(text))
     #https://www.pythoncentral.io/hashing-strings-with-python/
     # SHA256
     hash_sha256 = hashlib.sha256(text)
     hex_dig_sha256 = hash_sha256.hexdigest()
     # MD5
     hash_md5 = hashlib.md5(hex_dig_sha256)
     hex_dig_md5 = hash_md5.hexdigest()
     return(hex_dig_md5)

def envidat_theme_get_access_url(resource, user_id=''):
    token_tag = "envidat_token"
    username_tag = "envidat_user"

    url = resource.get('url','no_url')

    resource_id = resource.get('id','')
    resource_dict = {}

    if resource_id:
        try:
            resource_dict = toolkit.get_action('resource_show')(
                                context={'ignore_auth': True},
                                data_dict={'id':resource_id})
        except:
            return (url)

        if resource_dict and (resource_dict.get('url_type', 'upload')!='upload'):
            restricted_dict = {}
            try:
                restricted_dict = json.loads(resource_dict.get("restricted", "{}"))
            except:
                restricted_dict = {}
            shared_secret = restricted_dict.get("shared_secret","")
            if shared_secret:
                if not user_id:
                     user_id = str(c.user)
                if user_id:
                    user_dict = toolkit.get_action('user_show')(context={'ignore_auth': True},
                                                                data_dict={'id': user_id})
                    user_mail = user_dict.get('email', "none@none")
                    timestamp_str = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
                    token = _envidat_theme_get_hash( str(shared_secret) + user_mail + timestamp_str)

                    if (url.find('?')<0):
                        url += '?'
                    else:
                        url += '&'
                    url += token_tag + '=' + token + '&' + username_tag + '=' + user_id
    return url

# Copied from hierarchy, maybe this code should go there!!
def envidat_theme_get_children_packages(organization, count=2):

    def _children_name_list(children):
        name_list = []
        for child in children:
            name = child.get('name', "")
            name_list += [name] + _children_name_list(child.get('children', []))
        return name_list

    packages = organization.get('packages', [])
    children_organizations = _children_name_list(helpers.group_tree_section(organization['id'], include_parents=False, include_siblings=False).get('children',[]))
    for children in children_organizations:
        packages += p.toolkit.get_action('organization_show')({},{'id':children, 'include_datasets':True}).get('packages', [])
    return packages[:count]

def envidat_theme_get_markup(text):
    markup_text = []

    for token in text.split(' '):
        if token.find('@')>=0:
            markup_text += ['<b><a href="mailto:' + token + '" target="_top">' + token + '</a></b>']
        elif token.find('http://')==0 or token.find('https://')==0:
            start = token.find('//') + len('//')
            end = token.find('/', start)
            tag = token[start:end]
            markup_text += ['<b><a href="' + token + '">' + tag + '</a></b>']
        else:
            markup_text += [token]
    return ' '.join(markup_text)

def envidat_theme_set_default(values, default_value):
    ## Only set default value if current value is empty string or None
    ## or a list containing only '' or None.
    if isinstance(values, basestring) or values is None:
        if values not in ['', None]:
            return values
        islist = False
    elif isinstance(values, list):
        if not all([x in ['', None] for x in values]):
            return values
        islist = True
    else:
        return values

    # special default value resulting in "Full Name <email>"
    #if default_value == "context_fullname_email":
    #    val = u'{} <{}>'.format(toolkit.c.userobj.fullname,
    #                           toolkit.c.userobj.email)

    ## insert elif clauses for other defaults

    #else:
    #    val = default_value

    val = default_value

    # deal with list/string - duality
    if islist:
        values[0] = val
    else:
        values = val

    return values

def envidat_theme_get_citation(package_data_dict):
    '''
    Combines multiple datacite metadata into a
    citation string. Pattern:
    creators (publication_year): title; subtitle. publisher; doi:identifier.
    '''

    # skip if custom citation is included
    citation_found = package_data_dict.get('notes', "").find("__Citation:__")
    if (citation_found>=0):
        return False

    # otherwise generate from metadata
    citation = u''

    # creators
    creators = _get_from_json_dict_list(package_data_dict.get('author', ""), 'name')
    if creators:
        citation += creators

    # publication_year
    publication_year = _get_from_json_dict(package_data_dict.get('publication', ""), 'publication_year')
    if (publication_year):
        citation += ' ('+ publication_year + ')'

    # separator
    if citation:
        citation +='. '

    # title
    title = package_data_dict.get('title', "")
    if title:
        citation += title.strip() + '. '

    # publisher
    publisher = _get_from_json_dict(package_data_dict.get('publication', ""), 'publisher')
    if (publisher):
        citation += publisher + '. '

    # doi:identifier.
    doi = package_data_dict.get('doi', "")
    if doi:
        citation += 'doi:' + doi.strip() + '.'

    return citation


def _get_from_json_dict (text, field):
    try:
        json_dict = json.loads(text)
        value = json_dict.get(field, "")
    except:
        return ""
    return _safe_str(value).strip()

def _get_from_json_dict_list (text, field, sep='; '):
    try:
        json_list = json.loads(text)
        if type(json_list) is not list:
            json_list = [ json_list ]
        value_list = []
        for item in json_list:
            value = _safe_str(item.get(field, "")).strip()
            if value:
                value_list += [ value ]
    except:
        return ""
    return (sep.join(value_list))


def _safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj)

def envidat_theme_get_datamanager_choices(organization_dict):
    '''
    Gets the admins of the organization as choices
    '''
    choices = []
    for user in organization_dict.get('users',[]):
        username = user.get('name', '')
        fullname = user.get('display_name', user.get('fullname', username))
        capacity = user.get('capacity', '')
        if fullname and (capacity=='admin'):
            choices += [ { "value": username, "label": fullname}]
    return choices

def envidat_theme_get_datamanager_user(username, organization_dict):
    '''
    Gets the user information of the data manager
    '''
    datamanager_user = {}
    for user in organization_dict.get('users',[]):
        if  (user.get('name', '') == username)  and (user.get('capacity', '') == 'admin'):
            datamanager_user = user
    return datamanager_user

