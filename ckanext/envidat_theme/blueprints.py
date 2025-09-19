import ckan.plugins.toolkit as toolkit

from logging import getLogger

from flask import Blueprint, make_response, request

import urllib
import requests

import base64


log = getLogger(__name__)


def get_blueprints(name, module):
    # Create Blueprint for plugin
    blueprint = Blueprint(name, module)

    blueprint.add_url_rule(
        u"/query",
        u"query",
        query_solr
    )

    return blueprint


def query_solr():
    """Redirect the query to Solr
    """
    try:
        # get the config object
        config = toolkit.config
        solr_url = config.get('solr_url')
        solr_user = config.get('solr_user')
        solr_password = config.get('solr_password')

        # base64
        if request.args.get('stream'):
            query = base64.b64decode(request.args.get('stream')).decode("utf-8")
            request_url = solr_url + "/select?" + query
        else:
            query = urllib.parse.urlencode(request.args)
            request_url = solr_url + "/select?" + query

        # set a header
        headers = {u'Content-Type': 'application/json'}

        # set authorization
        if solr_user is not None and solr_password is not None:
            http_auth = solr_user + ':' + solr_password
            http_auth = base64.b64encode(bytes(http_auth, "utf-8")).decode()
            headers['Authorization'] = 'Basic {0}'.format(http_auth)

        r = requests.get(request_url, headers=headers)
        return make_response(r.content, r.status_code, headers)
    except Exception as e:
        log.error('Cannot query to Solr {0}, Exception: {1}'.format(query, e))
        return make_response({'error': 'Exception occurred', 'message': str(e)}, 500, headers)
