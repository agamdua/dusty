import os
import yaml

from dusty.compiler.spec_assembler import get_specs_path

def _num_to_alpha(num):
    if num >= 26:
        raise ValueError('Only supports up to 26')
    return chr(num + 97)

def _write(spec_type, name, spec_doc):
    spec_type_path = os.path.join(get_specs_path(), '{}s'.format(spec_type))
    try:
        os.makedirs(spec_type_path)
    except OSError:
        pass
    with open(os.path.join(spec_type_path, '{}.yml'.format(name)), 'w') as f:
        f.write(yaml.dump(spec_doc, default_flow_style=False))

def basic_specs_fixture():
    _write('bundle', 'bundle-a', {'description': 'Bundle A', 'apps': ['app-a']})
    _write('bundle', 'bundle-b', {'description': 'Bundle B', 'apps': ['app-b']})
    _write('app', 'app-a', {'repo': 'github.com/app/a',
                            'image': 'app/a',
                            'scripts': {'example': {'description': 'A script description',
                                                    'command': 'ls /'}}})
    _write('app', 'app-b', {'repo': 'github.com/app/b', 'image': 'app/b'})
    _write('lib', 'lib-a', {'repo': 'github.com/lib/a', 'image': 'lib/a'})
    _write('service', 'service-a', {'image': 'service/a'})

def busybox_single_app_bundle_fixture(num_bundles=1):
    for bundle in range(num_bundles):
        name = 'busybox-{}'.format(_num_to_alpha(bundle))
        _write('bundle', name, {'description': 'Busybox bundle', 'apps': [name]})
        _write('app', name, {'repo': 'github.com/fake/repo', 'image': 'busybox'})
