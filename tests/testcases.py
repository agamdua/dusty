import os
import sys
import shutil
import tempfile
import logging
import getpass

from unittest import TestCase
from nose.tools import nottest
from mock import patch

from dusty import constants
from dusty.config import write_default_config, save_config_value, get_config, save_config
from dusty.compiler.spec_assembler import get_specs_repo
from dusty.commands.repos import override_repo
from dusty.cli import main as client_entrypoint
from dusty.systems.docker import _exec_in_container, _get_docker_client, _get_container_for_app_or_service
from .fixtures import basic_specs_fixture

class TestCaptureHandler(logging.Handler):
    def __init__(self, lst):
        super(TestCaptureHandler, self).__init__()
        self.lst = lst

    def emit(self, record):
        self.lst.append(self.format(record))

class DustyTestCase(TestCase):
    def setUp(self):
        self.temp_config_path = tempfile.mkstemp()[1]
        self.temp_specs_path = tempfile.mkdtemp()
        self.temp_repos_path = tempfile.mkdtemp()

        constants.CONFIG_PATH = self.temp_config_path
        write_default_config()
        save_config_value(constants.CONFIG_SPECS_REPO_KEY, 'github.com/org/dusty-specs')
        override_repo(get_specs_repo().remote_path, self.temp_specs_path)
        basic_specs_fixture()

        self.client_output = []
        self.capture_handler = TestCaptureHandler(self.client_output)
        logging.getLogger(constants.SOCKET_LOGGER_NAME).addHandler(self.capture_handler)

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        shutil.rmtree(self.temp_repos_path)
        logging.getLogger(constants.SOCKET_LOGGER_NAME).removeHandler(self.capture_handler)

    @property
    def last_client_output(self):
        return self.client_output[-1] if self.client_output else None

class CommandError(Exception):
    pass

class DustyIntegrationTestCase(TestCase):
    """This test case intentionally avoids mocking whenever possible
    in order to get as close as possible to the actual state that
    would be experienced on a system running Dusty. Therefore,
    integration tests are possibly destructive if run on a user's
    machine. To help protect the user from running them accidentally,
    integration tests will refuse to run unless the environment
    variable DUSTY_ALLOW_INTEGRATION_TESTS is set.

    Note that this also assumes it is running against an actual
    Dustyd process on the local host."""
    def setUp(self):
        if not os.getenv('DUSTY_ALLOW_INTEGRATION_TESTS'):
            raise RuntimeError('You must set the env var DUSTY_ALLOW_INTEGRATION_TESTS to run integration tests. '
                               'This may affect your local config, do not run integration tests on your actual '
                               "machine unless you know what you're doing!")
        self.previous_config = get_config()
        self._clear_stdout()
        self.overridden_specs_path = tempfile.mkdtemp()
        write_default_config()
        save_config_value(constants.CONFIG_SETUP_KEY, True)
        save_config_value(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/example-dusty-specs')
        save_config_value(constants.CONFIG_MAC_USERNAME_KEY, self.current_user)
        override_repo(get_specs_repo().remote_path, self.overridden_specs_path)
        self._clear_stdout()

    def tearDown(self):
        shutil.rmtree(self.overridden_specs_path)
        save_config(self.previous_config)

    def _clear_stdout(self):
        self.stdout_start = len(sys.stdout.getvalue())

    @property
    def current_user(self):
        return getpass.getuser()

    @property
    def CommandError(self):
        """Pure convenience to avoid having to import this explicitly"""
        return CommandError

    @property
    def stdout(self):
        """Returns any stdout that has been generated *since* the last time
        clear_stdout was called."""
        return sys.stdout.getvalue()[self.stdout_start:].strip()

    @patch('sys.exit')
    def run_command(self, args, fake_exit):
        """Run a command through the Dusty client entrypoint, e.g. simulating
        the Dusty CLI as close as possible without having to call a subprocess.
        This command raises if the command fails, otherwise it returns the
        stdout generated by the command."""
        sys.argv = ['dusty'] + args.split(' ')
        client_entrypoint()
        for call in fake_exit.mock_calls:
            name, args, kwargs = call
            if len(args) == 1 and args[0] > 0:
                self._clear_stdout()
                raise CommandError('Command {} returned with exit code: {}'.format(' '.join(sys.argv), args[0]))
        result = self.stdout
        self._clear_stdout()
        return result

    def _in_same_line(self, string, *values):
        for line in string.splitlines():
            if all(value in line for value in values):
                return True
        return False

    def assertInSameLine(self, string, *values):
        self.assertTrue(self._in_same_line(string, *values))

    def assertNotInSameLine(self, string, *values):
        self.assertFalse(self._in_same_line(string, *values))

    def assertFileContentsInContainer(self, service_name, file_path, contents):
        client = _get_docker_client()
        container = _get_container_for_app_or_service(client, service_name, raise_if_not_found=True)
        result = _exec_in_container(client, container, 'cat', file_path)
        self.assertEqual(result, contents)
