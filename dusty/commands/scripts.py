import textwrap

from prettytable import PrettyTable

from ..log import log_to_client
from ..compiler.spec_assembler import get_specs
from ..compiler.compose import container_code_path
from . import utils
from ..systems.docker import get_dusty_container_name
from ..command_file import dusty_command_file_name
from .. import constants
from ..payload import daemon_command

@daemon_command
def script_info_for_app(app_name):
    app_specs = get_specs()['apps'].get(app_name)
    if not app_specs:
        raise KeyError('No app found named {} in specs'.format(app_name))
    if not app_specs['scripts']:
        log_to_client('No scripts registered for app {}'.format(app_name))
        return

    table = PrettyTable(['Script', 'Description'])
    for script_spec in app_specs['scripts']:
        table.add_row([script_spec['name'],
                       '\n'.join(textwrap.wrap(script_spec['description'], 80))])
    log_to_client(table.get_string(sortby='Script'))

def execute_script(app_name, script_name, script_arguments=[]):
    app_specs = get_specs()['apps'].get(app_name)
    if not app_specs:
        raise KeyError('No app found named {} in specs'.format(app_name))
    found_spec = False
    for script_dict in app_specs['scripts']:
        if script_dict['name'] == script_name:
            found_spec = True
            break
    if not found_spec:
        raise KeyError('No script found named {} in specs for app {}'.format(script_name, app_name))

    command_file = '{}/{}'.format(constants.CONTAINER_COMMAND_FILES_DIR, dusty_command_file_name(app_specs.name, script_name=script_name))
    container_name = get_dusty_container_name(app_name)
    exec_options = utils.exec_docker_options()
    utils.exec_docker('exec', exec_options, container_name, 'sh', command_file, *script_arguments)
