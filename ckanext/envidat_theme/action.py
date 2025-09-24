# coding: utf8

from ckan.logic import side_effect_free
# from ckan.logic.action.get import user_show
import ckan.plugins.toolkit as toolkit
# from ckanext.passwordless import util
import json
from xml.etree import ElementTree
import requests


from logging import getLogger

log = getLogger(__name__)


# @side_effect_free
# def context_user_show(context, data_dict):
#     user = envidat_get_user_from_context(context)
#     if user:
#         return {'user': user}
#     else:
#         return {}


@side_effect_free
def envidat_get_author_data(context, data_dict):
    user_data = get_author_data(context, data_dict)
    return user_data


# def envidat_get_user_from_context(context):
#     auth_user_obj = context.get('auth_user_obj', None)
#     if auth_user_obj:
#         auth_user_obj_dict = auth_user_obj.as_dict()
#         user_data = user_show(context, {'id': auth_user_obj_dict['id']})
#         auth_user_obj_dict["email_hash"] = user_data["email_hash"]
#
#         # renew the master key
#         apikey = util.renew_master_token(auth_user_obj_dict['name'])
#         auth_user_obj_dict["apikey"] = apikey
#
#         return auth_user_obj_dict
#     else:
#         return {}


def get_author_data(context, data_dict):

    context['ignore_auth'] = True

    email = data_dict.get('email', '').strip().lower()

    if email:
        try:
            search_results = toolkit.get_action(
                'package_search')(
                context,
                {'q': 'author:\"' + email + '\"',
                 'sort': 'metadata_modified desc'}
            )
        except Exception as e:
            log.error("exception {0}".format(e))
            return {}

        author_data = {}
        if search_results.get('count', 0) > 0:
            author_data_list = []
            for dataset in search_results.get('results', []):
                author_data_list += [a for a in json.loads(dataset.get('author'))
                                     if a.get('email', '').strip().lower() == email]


            # copy dictionary field by field including empty fields
            author_data = {}

            if author_data_list:
                for k, v in author_data_list[0].items():
                    if v and len(v) > 0:
                        author_data[k] = "{0}".format(v).strip()
                    else:
                        author_data[k] = ""

            # fill up empty fields from older datasets
            for author in author_data_list:
                for k, v in author.items():
                    if not author_data.get(k) or (len(author_data.get(k, "")) < 1):
                        # TODO skip affiliation
                        author_data[k] = "{0}".format(v).strip()

        # TODO check if the orcid is empty request from ORCID API
        # https://www.envidat.ch/orcid/search/?q=email:*@wsl.ch
        if not author_data.get('identifier'):
            author_data['identifier'] = get_orcid_id(email)

        return author_data

    return {}




def get_orcid_id(email):
    try:

        api_call = 'https://www.envidat.ch/orcid/search/?q=email:{0}'.format(email)

        req = requests.get(api_call)

        root = ElementTree.fromstring(req.content)

        path = root.find(".//{http://www.orcid.org/ns/common}path")
        orcid_id = path.text

        return orcid_id

    except AttributeError:
        return ''

    except Exception as e:
        log.error('Failed to get orcid_id: {0}'.format(e))
        return ''
