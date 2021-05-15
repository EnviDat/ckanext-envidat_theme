# -*- coding: utf-8 -*-
#  ckan -c /etc/ckan/default/ckan_cloud.ini envidattheme migrate-local

import click
import os

from pathlib import Path

import ckan.plugins as p
from ckanapi import LocalCKAN
from ckan.logic import NotFound
import hashlib

from ckanext.cloudstorage.storage import (CloudStorage, ResourceCloudStorage, _md5sum)


@click.group()
def envidattheme():
    """EnviDat Theme management commands.
    """
    pass


@envidattheme.command('migrate-local')
@click.argument('path', required=False)
def migrate_local(path):
    """Migrate back uploaded resources from cloud
       to local storage.
    """
    msg, ok = _migrate_local(path)
    click.secho(msg, fg='green' if ok else 'red')


def get_commands():
    return [envidattheme]


def _migrate_local(path):
    # get the config object
    config = p.toolkit.config
    lc = LocalCKAN()

    # get the path
    if path:
        local_path = path
    else:
        local_path = config.get('ckan.storage_path')

    # get the storage access
    cs = CloudStorage()

    RESOURCE_DIR_TAG = "resources/"
    obj_dir = {o.name.split('/')[1]: o for o in cs.container.list_objects() if o.name.startswith(RESOURCE_DIR_TAG)}

    print("Found {0} resources:".format(len(obj_dir)))
    count_existing = 0
    count_downloaded = 0
    for resource_id, cloud_object in obj_dir.items():
        print("\n - {0} : {1}".format(resource_id, cloud_object.name))
        try:
            resource = lc.action.resource_show(id=resource_id)
            count_existing +=1
            print(u'\t * Resource FOUND')
            # check if it exists locally
            resource_path = os.path.join(local_path, RESOURCE_DIR_TAG, resource_id[0:3], resource_id[3:6], resource_id[6:])
            do_migrate = False
            if not os.path.exists(resource_path):
                do_migrate = True
                directory = os.path.dirname(resource_path)
                print(u'\t * Resource does NOT exist locally, prepare directory {0}'.format(directory))
                Path(directory).mkdir(parents=True, exist_ok=True)
            else:
                local_size = os.path.getsize(resource_path)
                cloud_size = int(cloud_object.size)
                if local_size != cloud_size:
                    do_migrate = True
                    print(u'\t * Resource local size {0} differs from cloud {1}'.format(local_size, cloud_size))
                else:
                    print(u'\t * Resource local size {0} equals cloud'.format(local_size))
                    # compare checksum/md5 (as in cloud migrate)
                    print("\t * Cloud hash: {0}".format(cloud_object.hash))
                    hash_file = hashlib.md5(open(resource_path, 'rb').read()).hexdigest()
                    print("\t * File hash {0}: {1}".format(resource_path, hash_file))
                    # basic hash
                    if hash_file == cloud_object.hash:
                        print("\t - Matching hash, skipping upload...")
                    else:
                        # multipart hash
                        multi_hash_file = _md5sum(resource_path)
                        print("\t - File multi hash {0}: {1}".format(resource_path, multi_hash_file))
                        if multi_hash_file == cloud_object.hash:
                            print("\t - File found, matching hash, skipping download...")
                        else:
                            print("\t * File found, different multi hash {0}".format(cloud_object.hash))
                            do_migrate = True
            if do_migrate:
                print("\t => Resource found locally but OUTDATED, downloading")
                Path(resource_path).touch()
                cloud_object.download(destination_path=resource_path, overwrite_existing=True)
                count_downloaded += 1
                print("\t\t ...DONE ({0})".format(count_downloaded))

        except NotFound:
            print(u'\t - Resource not found, skipping...')
            pass

    return 'Done! found {0} cloud resources, migrated {1} to path "{2}"'.format(count_existing,
                                                                                count_downloaded,
                                                                                local_path, ), True
