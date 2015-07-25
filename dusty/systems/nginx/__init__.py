import os
import logging
import subprocess
import tempfile

from ... import constants
from ...config import get_config_value
from ..rsync import sync_local_path_to_vm
from ...platform import running_osx

def _write_nginx_config(nginx_config, path):
    """Writes the config file from the Dusty Nginx compiler
    to the Nginx includes directory, which should be included
    in the main nginx.conf."""
    with open(path, 'w') as f:
        f.write(nginx_config)

def update_nginx_from_config(nginx_config):
    """Write the given config to disk as a Dusty sub-config
    in the Nginx includes directory. Then, either start nginx
    or tell it to reload its config to pick up what we've
    just written."""
    logging.info('Updating nginx with new Dusty config')
    if running_osx():
        temp_path = tempfile.mkstemp()[1]
        _write_nginx_config(nginx_config, temp_path)
        sync_local_path_to_vm(temp_path, os.path.join(constants.NGINX_CONFIG_DIR_IN_VM, 'dustyNginx.conf'))
    else:
        if not os.path.isdir(constants.NGINX_CONFIG_LOCAL_PATH):
            os.makedirs(constants.NGINX_CONFIG_LOCAL_PATH)
        _write_nginx_config(nginx_config, os.path.join(constants.NGINX_CONFIG_LOCAL_PATH, 'dustyNginx.conf'))