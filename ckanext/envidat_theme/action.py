# coding: utf8

from ckan.logic import side_effect_free
from ckan.logic.action.get import user_show
import ckan.plugins.toolkit as toolkit
from ckanext.passwordless import util

from logging import getLogger

log = getLogger(__name__)


@side_effect_free
def context_user_show(context, data_dict):
    user = envidat_get_user_from_context(context)
    if user:
        return {'user': user}
    else:
        return {}


def envidat_get_user_from_context(context):
    auth_user_obj = context.get('auth_user_obj', None)
    if auth_user_obj:
        auth_user_obj_dict = auth_user_obj.as_dict()
        user_data = user_show(context, {'id': auth_user_obj_dict['id']})
        auth_user_obj_dict["email_hash"] = user_data["email_hash"]

        # renew the master key
        apikey = util.renew_master_token(auth_user_obj_dict['name'])
        auth_user_obj_dict["apikey"] = apikey

        return auth_user_obj_dict
    else:
        return {}
