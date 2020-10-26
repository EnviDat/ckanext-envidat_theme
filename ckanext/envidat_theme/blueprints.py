import ckan.model as model
import ckan.plugins.toolkit as toolkit
import collections

from logging import getLogger

from flask import Blueprint, make_response

from xmltodict import unparse

from ckanext.package_converter.logic import export_as_record
from ckanext.package_converter.model.record import XMLRecord

log = getLogger(__name__)


def get_blueprints(name, module):
    # Create Blueprint for plugin
    blueprint = Blueprint(name, module)

    blueprint.add_url_rule(
        u"/catalog/export/<file_format>.<extension>",
        u"catalog_export",
        catalog_export
    )

    return blueprint


def catalog_export(file_format, extension='xml'):
    """Return the given dataset as a converted file.
    """
    converted_package = None

    context = {
        'model': model,
        'session': model.Session,
        'user': toolkit.g.user
    }

    if file_format == 'dcat-ap-ch':
        content_type = 'application/xml'

        headers = {u'Content-Disposition': 'attachment; filename=' + file_format + '.' + extension,
                   u'Content-Type': content_type}

        package_list = toolkit.get_action('package_list')(context, {})
        converted_packages = []

        try:
            for package_name in package_list:
                converted_record = export_as_record(package_name, file_format, type='package')
                record = XMLRecord.from_record(converted_record)
                dataset_dict = record.get_xml_dict().get('rdf:RDF', {}).get('dcat:Dataset')
                if dataset_dict:
                    converted_packages += [{'dcat:Dataset': dataset_dict}]
        except Exception as e:
            log.error('Cannot convert to format {0}, Exception: {1}'.format(file_format,e))
            toolkit.abort(404, 'Cannot convert, format not found')

        catalog_dict = collections.OrderedDict()

        # header
        catalog_dict['@xmlns:dct'] = "http://purl.org/dc/terms/"
        catalog_dict['@xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        catalog_dict['@xmlns:dcat'] = "http://www.w3.org/ns/dcat#"
        catalog_dict['@xmlns:foaf'] = "http://xmlns.com/foaf/0.1/"
        catalog_dict['@xmlns:xsd'] = "http://www.w3.org/2001/XMLSchema#"
        catalog_dict['@xmlns:rdfs'] = "http://www.w3.org/2000/01/rdf-schema#"
        catalog_dict['@xmlns:rdf'] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        catalog_dict['@xmlns:vcard'] = "http://www.w3.org/2006/vcard/ns#"
        catalog_dict['@xmlns:odrs'] = "http://schema.theodi.org/odrs#"
        catalog_dict['@xmlns:schema'] = "http://schema.org/"

        catalog_dict['dcat:Catalog'] = {'dcat:dataset': converted_packages}

        dcat_catalog_dict = collections.OrderedDict()
        dcat_catalog_dict['rdf:RDF'] = catalog_dict

        catalog_converted = unparse(dcat_catalog_dict, short_empty_elements=True, pretty=True)

        return make_response(catalog_converted, 200, headers)
    else:
        toolkit.abort(404, 'Format not found')

