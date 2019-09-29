import ckan.plugins as plugins
from ckan.lib.plugins import DefaultTranslation

import ckan.plugins.toolkit as toolkit

from ckanext.envidat_theme import helpers, validation, logic, action

class Envidat_ThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'envidat_theme')

    # ITemplateHelpers
    def get_helpers(self):
        return {'envidat_theme_get_children_packages': helpers.envidat_theme_get_children_packages,
                 'envidat_theme_get_citation': helpers.envidat_theme_get_citation,
                 'envidat_theme_get_datamanager_choices': helpers.envidat_theme_get_datamanager_choices,
                 'envidat_theme_get_datamanager_user': helpers.envidat_theme_get_datamanager_user,
                 'envidat_theme_set_default': helpers.envidat_theme_set_default,
                 'envidat_theme_get_markup': helpers.envidat_theme_get_markup,
                 'envidat_theme_get_access_url': helpers.envidat_theme_get_access_url,
                 'envidat_theme_sizeof_fmt': helpers.envidat_theme_sizeof_fmt,
                 'envidat_get_dora_citation': helpers.envidat_get_dora_citation,
                 'envidat_get_funding': helpers.envidat_get_funding }


    # IValidators
    def get_validators(self):
        return { 'envidat_string_uppercase': validation.envidat_string_uppercase,
                 'envidat_shortname_validator': validation.envidat_shortname_validator,
                 'envidat_minimum_tag_count': validation.envidat_minimum_tag_count }

    # IActions
    def get_actions(self):
        return {'envidat_context_user_show': action.context_user_show }

    # IAuthFunctions
    # The portal admin can always update
    # Editors can edit their own datasets
    # Organization admins can edit all datasets in their organization
    def get_auth_functions(self):
        return {'package_update': logic.envidat_theme_package_update}

