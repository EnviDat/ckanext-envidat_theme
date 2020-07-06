import json
import time
import datetime
import urllib
import hashlib


import ckan.lib.helpers as h
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
                    url += token_tag + '=' + token + '&' + username_tag + '=' + user_mail
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
            markup_text += ['<b><a href="' + token + '" target="_blank" >' + tag + '</a></b>']
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
    creators = _get_from_json_dict_list(package_data_dict.get('author', ""), ['name', 'given_name'])
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
        citation += '<a href="https://doi.org/' + doi.strip() + '">doi:' + doi.strip() + '</a>.'

    return citation


def _get_from_json_dict (text, field):
    try:
        json_dict = json.loads(text)
        value = json_dict.get(field, "")
    except:
        return ""
    return _safe_str(value).strip()

def _get_from_json_dict_list (text, fields, sep='; '):
    try:
        json_list = json.loads(text)
        if type(json_list) is not list:
            json_list = [ json_list ]
        value_list = []
        for item in json_list:
            item_values = []
            for field in fields:
                value = _safe_str(item.get(field, "")).strip()
                if value:
                    item_values += [ value ]
            if item_values:
                value_list += [ ', '.join(item_values)]
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


def envidat_theme_sizeof_fmt(num_text, resource_size=None):
    if num_text:
        try:
            num = float(num_text)
        except:
            return (str(num_text) + " bytes")
        for unit in ['bytes','KB','MB','GB','TB','PB','EB','ZB']:
            if abs(num) < 1024.0:
                return "%3.2f %s" % (num, unit)
            num /= 1024.0
        return "%.1f %s" % (num, 'YB')
    else:
        try:
            resource_size_obj = json.loads(resource_size)
            return resource_size_obj.get('size_value' , '0') + ' ' + resource_size_obj.get('size_unit' , 'KB').upper() 
        except:
            return (str(num_text) + " bytes")

def envidat_get_related_datasets(related_datasets):
    related_datasets_html = h.render_markdown(related_datasets)

    edited_html = []
    for line in related_datasets_html.split('\n'):
        edited_line = line
        if (line.startswith('<li>') and line.endswith('</li>')) or\
           (line.startswith('<p>') and line.endswith('</p>')):
            line_contents = line[3:-4].strip().lower()
            html_tags = ['<p>','</p>']
            if line.startswith('<li>'):
                html_tags = ['<li>','</li>']
                line_contents = line_contents[1:-1].strip()

            envidat_id = None
            envidat_citation = None

            package_list = []
            try:
                package_list = toolkit.get_action('package_list')(
                                context={'ignore_auth': False},
                                data_dict={})
            except:
                logger.error('envidat_get_related_datasets: could not retrieve package list from API')

            if line_contents in package_list:
                envidat_id = line_contents
            elif line_contents.startswith('<a href="https://www.envidat.ch'):
                url = line_contents.split('"')[1]
                url_split = url.rsplit('/', 1)
                envidat_id = url_split[1].replace('%3a', ':')

            if envidat_id:
                try:
                    envidat_dataset = toolkit.get_action('package_show')(
                                            context={'ignore_auth': False},
                                            data_dict={'id':envidat_id})
                    envidat_citation = envidat_theme_get_citation(envidat_dataset)
                except:
                    logger.error('envidat_get_related_datasets: could not retrieve package details from API')


                if envidat_citation:
                    edited_line = html_tags[0] + envidat_citation + html_tags[1] 

        edited_html += [edited_line]
    return '\n'.join(edited_html)


def envidat_get_related_citations(related_publications):
    related_publications_html = h.render_markdown(related_publications)

    edited_html = []
    for line in related_publications_html.split('\n'):
        edited_line = line
        if (line.startswith('<li>') and line.endswith('</li>')) or\
           (line.startswith('<p>') and line.endswith('</p>')):
            line_contents = line[3:-4].strip().lower()
            html_tags = ['<p>','</p>']
            if line.startswith('<li>'):
                html_tags = ['<li>','</li>']
                line_contents = line_contents[1:-1].strip()
            dora_citation = None
            if line_contents.startswith('wsl:') or line_contents.startswith('psi:') or \
               line_contents.startswith('eawag:')or line_contents.startswith('empa:') :
                dora_citation = _get_dora_id_citation(line_contents, html_tags)
            elif line_contents.startswith('<a href="https://www.dora.lib4ri.ch'):
                url = line_contents.split('"')[1]
                url_split = url.rsplit('/', 1)
                dora_id = url_split[1].replace('%3a', ':')
                dora_citation = _get_dora_id_citation(dora_id, html_tags)
            if dora_citation:
                edited_line= dora_citation

        edited_html += [edited_line]
    return '\n'.join(edited_html)


def envidat_get_dora_citation(dora_id_list):
    dora_html = "<ul>"
    if dora_id_list:
        for dora_id in dora_id_list.split(' '):
            if dora_id:
                dora_html += _get_dora_id_citation(dora_id)
        return dora_html + "</ul>"
    else:
        return ""

def _get_dora_id_citation(dora_id, html_tags = ['<li>','</li>']):
    dora_url = "https://www.dora.lib4ri.ch/wsl/islandora/search/json_cit_pids/"
    citation_url = dora_url + dora_id
    try:
        response = urllib.urlopen(citation_url) 
        data = json.loads(response.read())
        citation_html = data[dora_id]["citation"]["ACS"]
        dora_html = html_tags[0] +  _markup_links(citation_html) + html_tags[1]
    except:
        logger.warn(u"Couldn't retrieve DORA citation for '{0}'".format(dora_id))
        dora_html = ''
    return dora_html

def envidat_get_funding(funding):
    if funding:
        data = json.loads(funding)
        return data
    return None

def _markup_links(text):
    markup_text = []
    for token in text.split(' '):
        if token.find('http://')==0 or token.find('https://')==0:
            start = token.find('//') + len('//')
            tag = token[start:]
            markup_text += ['<a href="' + token + '" target="_blank">' + tag + '</a>']
        else:
            markup_text += [token]
    return ' '.join(markup_text)

