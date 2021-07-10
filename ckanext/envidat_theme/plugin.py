import ckan.plugins as plugins
from ckan.lib.plugins import DefaultTranslation

import ckan.plugins.toolkit as toolkit

from ckanext.envidat_theme import helpers, validation, logic, action, commands
import ckanext.envidat_theme.blueprints as blueprints

from ckan.lib.webassets_tools import add_public_path
import os


class Envidat_ThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IClick)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public', 'envidat_theme')

        asset_path = os.path.join(
            os.path.dirname(__file__), 'public'
        )
        add_public_path(asset_path, '/')

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
                'envidat_get_related_datasets': helpers.envidat_get_related_datasets,
                'envidat_get_related_citations': helpers.envidat_get_related_citations,
                'envidat_get_funding': helpers.envidat_get_funding}

    # IValidators
    def get_validators(self):
        return {'envidat_string_uppercase': validation.envidat_string_uppercase,
                'envidat_shortname_validator': validation.envidat_shortname_validator,
                'envidat_minimum_tag_count': validation.envidat_minimum_tag_count,
                'envidat_reorder': validation.envidat_reorder,
                'envidat_copy_type_general': validation.envidat_copy_type_general,
                'envidat_minimum_description_length': validation.envidat_minimum_description_length}

    # IActions
    def get_actions(self):
        return {'envidat_context_user_show': action.context_user_show,
                'envidat_get_author_data': action.envidat_get_author_data}

    # IAuthFunctions
    # The portal admin can always update
    # Editors can edit their own datasets
    # Organization admins can edit all datasets in their organization
    def get_auth_functions(self):
        return {'package_update': logic.envidat_theme_package_update,
                'package_delete': logic.envidat_theme_package_delete}

    # IBlueprint
    def get_blueprint(self):
        return blueprints.get_blueprints(self.name, self.__module__)

    # IClick
    def get_commands(self):
        return commands.get_commands()
