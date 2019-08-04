# coding: utf8

from ckan.logic import side_effect_free

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
        return auth_user_obj.as_dict()
    else:
        return {}
