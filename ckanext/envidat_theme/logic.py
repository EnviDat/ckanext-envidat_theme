import ckan.logic.auth as logic_auth
import ckan.authz as authz
from ckan.logic.auth.update import package_update
from ckan.logic import get_action
from ckan.common import _

import ckan.model as model

from logging import getLogger

log = getLogger(__name__)


# Editors can edit only their own datasets
# Organization admins can edit all datasets in their organization
def envidat_theme_package_update(context, data_dict):
    # if CKAN returns false, don't do any further checks
    ckan_default_auth = package_update(context, data_dict)

    if not ckan_default_auth.get('success', True):
        return ckan_default_auth

    # retireve user and package data
    user = context.get('user')
    package = logic_auth.get_package_object(context, data_dict)

    # if there is an owner org then we must have update_dataset
    # permission for that organization
    package_organization = package.owner_org
    package_creator = package.creator_user_id
    # log.debug("package organization is " + str(package_organization))
    # log.debug("package creator is " + str(package_creator))

    if package_organization:
        creator_id, user_role = _get_user_role_organization(user, package_organization)
        # log.debug("user " + str(user) + " role is " + str(user_role) + " and creator_id is " + str(creator_id))
        if user_role == 'admin':
            # log.debug("true - admin")
            return {'success': True}
        elif creator_id == package_creator:
            # log.debug("true - creator")
            return {'success': True}

    # Check collaborators
    userobj = model.User.get(user)

    if userobj:
        context = {'ignore_auth': True, 'user': user}
        data_dict = {'id': package.id}
        collaborators = get_action('package_collaborator_list')(context, data_dict)

        for collaborator in collaborators:
            if (collaborator.get('user_id') == userobj.id) and (collaborator.get('capacity') == 'editor'):
                return {'success': True}

    # log.debug("false - cannot update")
    return {'success': False,
            'msg': _('User %s not authorized to edit this dataset') %
                   (str(user))}


def _get_user_role_organization(user_id, org_id):
    organization_dict = get_action('organization_show')({'ignore_auth': True}, {'id': org_id})
    for user_data in organization_dict.get('users'):
        if (user_id == user_data.get('name')) or (user_id == user_data.get('id')):
            return user_data.get('id'), user_data.get('capacity')
    return '', ''
