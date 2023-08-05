# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013-2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the Juju Quickstart base application functions."""

from __future__ import unicode_literals

from contextlib import contextmanager
import json
import unittest

import jujuclient
import mock
import yaml

from quickstart import (
    app,
    settings,
)
from quickstart.tests import helpers


class TestProgramExit(unittest.TestCase):

    def test_string_representation(self):
        # The error is properly represented as a string.
        exception = app.ProgramExit('bad wolf')
        self.assertEqual('juju-quickstart: error: bad wolf', bytes(exception))


class ProgramExitTestsMixin(object):
    """Set up some base methods for testing functions raising ProgramExit."""

    @contextmanager
    def assert_program_exit(self, error):
        """Ensure a ProgramExit is raised in the context block.

        Also check that the exception includes the expected error message.
        """
        with self.assertRaises(app.ProgramExit) as context_manager:
            yield
        expected = 'juju-quickstart: error: {}'.format(error)
        self.assertEqual(expected, bytes(context_manager.exception))

    def make_env_error(self, message):
        """Create and return a jujuclient.EnvError with the given message."""
        return jujuclient.EnvError({'Error': message})


@helpers.mock_print
class TestEnsureDependencies(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    add_repository = '/usr/bin/add-apt-repository'
    apt_get = '/usr/bin/apt-get'

    def call_ensure_dependencies(self, call_effects, distro_only=False):
        """Execute the quickstart.app.ensure_dependencies call.

        The call_effects argument is used to customize the values returned by
        quickstart.utils.call invocations.

        Return the mock call object and the ensure_dependencies return value.
        """
        with self.patch_multiple_calls(call_effects) as mock_call:
            juju_version = app.ensure_dependencies(distro_only)
        return mock_call, juju_version

    def test_success_install(self, mock_print):
        # All the missing packages are installed from the PPA.
        side_effects = (
            (127, '', 'no juju'),  # Retrieve the Juju version.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (0, 'install', ''),  # Install missing packages.
            (0, '1.18.0', ''),  # Retrieve the version again.
        )
        mock_call, juju_version = self.call_ensure_dependencies(side_effects)
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'version'),
            mock.call('lsb_release', '-cs'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'software-properties-common'),
            mock.call('sudo', self.add_repository, '-y', 'ppa:juju/stable'),
            mock.call('sudo', self.apt_get, 'update'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'juju-core', 'juju-local'),
            mock.call(settings.JUJU_CMD, 'version'),
        ])
        mock_print.assert_has_calls([
            mock.call('adding the ppa:juju/stable PPA repository'),
            mock.call('sudo privileges will be required for PPA installation'),
            mock.call('sudo privileges will be used for the installation of \n'
                      'the following packages: juju-core, juju-local\n'
                      'this can take a while...'),
        ])
        self.assertEqual((1, 18, 0), juju_version)

    def test_distro_only_install(self, mock_print):
        # All the missing packages are installed from the distro repository.
        side_effects = (
            (127, '', 'no juju'),  # Retrieve the Juju version.
            (0, 'install', ''),  # Install missing packages.
            (0, '1.17.42', ''),  # Retrieve the version again.
        )
        mock_call, juju_version = self.call_ensure_dependencies(
            side_effects, distro_only=True)
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'version'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'juju-core', 'juju-local'),
            mock.call(settings.JUJU_CMD, 'version'),
        ])
        mock_print.assert_called_once_with(
            'sudo privileges will be used for the installation of \n'
            'the following packages: juju-core, juju-local\n'
            'this can take a while...')
        self.assertEqual((1, 17, 42), juju_version)

    def test_success_no_install(self, mock_print):
        # There is no need to install packages/PPAs if everything is already
        # set up.
        side_effects = (
            (0, '1.16.2-amd64', ''),  # Check the juju command.
            (0, '', ''),  # Check the lxc-ls command.
            # The remaining call should be ignored.
            (1, '', 'not ignored'),
        )
        mock_call, juju_version = self.call_ensure_dependencies(side_effects)
        self.assertEqual(2, mock_call.call_count)
        self.assertFalse(mock_print.called)
        self.assertEqual((1, 16, 2), juju_version)

    def test_success_partial_install(self, mock_print):
        # One missing installation is correctly handled.
        side_effects = (
            (0, '1.16.42', ''),  # Check the juju command.
            (127, '', 'no lxc'),  # Check the lxc-ls command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (0, 'install', ''),  # Install missing packages.
        )
        mock_call, juju_version = self.call_ensure_dependencies(side_effects)
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'version'),
            mock.call('/usr/bin/lxc-ls'),
            mock.call('lsb_release', '-cs'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'software-properties-common'),
            mock.call('sudo', self.add_repository, '-y', 'ppa:juju/stable'),
            mock.call('sudo', self.apt_get, 'update'),
            mock.call('sudo', self.apt_get, 'install', '-y', 'juju-local'),
        ])
        mock_print.assert_has_calls([
            mock.call('adding the ppa:juju/stable PPA repository'),
            mock.call('sudo privileges will be required for PPA installation'),
            mock.call('sudo privileges will be used for the installation of \n'
                      'the following packages: juju-local\n'
                      'this can take a while...'),
        ])
        self.assertEqual((1, 16, 42), juju_version)

    def test_distro_only_partial_install(self, mock_print):
        # One missing installation is correctly handled when using distro only
        # packages.
        side_effects = (
            (0, '1.16.42', ''),  # Check the juju command.
            (127, '', 'no lxc'),  # Check the lxc-ls command.
            (0, 'install', ''),  # Install missing packages.
        )
        mock_call, juju_version = self.call_ensure_dependencies(
            side_effects, distro_only=True)
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'version'),
            mock.call('/usr/bin/lxc-ls'),
            mock.call('sudo', self.apt_get, 'install', '-y', 'juju-local'),
        ])
        mock_print.assert_called_once_with(
            'sudo privileges will be used for the installation of \n'
            'the following packages: juju-local\n'
            'this can take a while...')
        self.assertEqual((1, 16, 42), juju_version)

    def test_add_repository_failure(self, mock_print):
        # A ProgramExit is raised if the PPA is not successfully installed.
        side_effects = (
            (127, '', 'no juju'),  # Check the juju command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (1, '', 'add repo error'),  # Add the juju stable repository.
        )
        with self.assert_program_exit('add repo error'):
            mock_call = self.call_ensure_dependencies(side_effects)[0]
            self.assertEqual(3, mock_call.call_count)

    def test_install_failure(self, mock_print):
        # A ProgramExit is raised if the packages installation fails.
        side_effects = (
            (127, '', 'no juju'),  # Check the juju command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (1, '', 'install error'),  # Install missing packages.
        )
        with self.assert_program_exit('install error'):
            mock_call = self.call_ensure_dependencies(side_effects)[0]
            self.assertEqual(3, mock_call.call_count)

    def test_juju_version_failure(self, mock_print):
        # A ProgramExit is raised if an error occurs while retrieving the Juju
        # version after the packages installation.
        side_effects = (
            (127, '', 'no juju'),  # Check the juju command.
            (0, 'saucy', ''),  # Retrieve the Ubuntu release codename.
            (0, 'install add repo', ''),  # Install add-apt-repository.
            (0, 'add repo', ''),  # Add the juju stable repository.
            (0, 'update', ''),  # Update the repository with new sources.
            (0, 'install', ''),  # Install missing packages.
            (127, '', 'no juju (again)'),  # Retrieve the Juju version.
        )
        with self.assert_program_exit('no juju (again)'):
            mock_call = self.call_ensure_dependencies(side_effects)[0]
            self.assertEqual(3, mock_call.call_count)


@helpers.mock_print
class TestEnsureSSHKeys(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    print_msg = (
        'Warning: no SSH keys were found in ~/.ssh\nTo proceed and generate '
        'keys, quickstart can\n[a] automatically create keys for you\n[m] '
        'provide commands to manually create your keys\n\nNote: ssh-keygen '
        'will prompt you for an optional\npassphrase to generate your key for '
        'you.\nQuickstart does not store it.\n'
    )
    exit_msg = (
        '\nIf you would like to create the keys yourself,\nplease run this '
        'command, follow its instructions,\nand then re-run quickstart:\n  '
        'ssh-keygen -b 4096 -t rsa'
    )

    def patch_raw_input(self, return_value='C', side_effect=None):
        """Patch the builtin raw_input function."""
        mock_raw_input = mock.Mock(
            return_value=return_value, side_effect=side_effect)
        return mock.patch('__builtin__.raw_input', mock_raw_input)

    def patch_check_keys(self, return_value=False):
        """Patch the quickstart.ssh.check_keys function."""
        mock_check_keys = mock.Mock(return_value=return_value)
        return mock.patch('quickstart.ssh.check_keys', mock_check_keys)

    def patch_start_agent(self, return_value=False, side_effect=None):
        """Patch the quickstart.ssh.start_agent function."""
        mock_start_agent = mock.Mock(
            return_value=return_value, side_effect=side_effect)
        return mock.patch('quickstart.ssh.start_agent', mock_start_agent)

    def patch_create_keys(self, return_value=False, side_effect=None):
        """Patch the quickstart.ssh.create_keys function."""
        mock_create_keys = mock.Mock(
            return_value=return_value, side_effect=side_effect)
        return mock.patch('quickstart.ssh.create_keys', mock_create_keys)

    def test_success(self, mock_print):
        # The function returns immediately if SSH keys are found.
        with self.patch_check_keys(return_value=True) as mock_check:
            with self.patch_start_agent(return_value=True):
                app.ensure_ssh_keys()
        self.assertEqual(1, mock_check.call_count)

    def test_error_starting_agent(self, mock_print):
        # The program is stopped if the SSH agent cannot be started.
        with self.assert_program_exit('foo'):
            with self.patch_check_keys():
                with self.patch_start_agent(side_effect=OSError('foo')):
                    app.ensure_ssh_keys()

    def test_extant_agent_returns(self, mock_print):
        # The SSH agent is not started if the keys are already available.
        with self.patch_check_keys(True):
            with self.patch_start_agent(side_effect=OSError('foo')) as mock_sa:
                app.ensure_ssh_keys()
        self.assertFalse(mock_sa.called)

    def test_successful_agent_start(self, mock_print):
        # The function returns if the agent is successfully started and keys
        # are available.
        mock_check_keys = mock.Mock(side_effect=(False, True))
        with mock.patch('quickstart.ssh.check_keys', mock_check_keys):
            with self.patch_start_agent(return_value=True):
                app.ensure_ssh_keys()
        self.assertFalse(mock_print.called)
        self.assertEqual(2, mock_check_keys.call_count)

    def test_failure_no_keygen(self, mock_print):
        # The program is stopped if the user disallows generating SSH keys.
        with mock.patch('sys.exit') as mock_exit:
            with self.patch_check_keys() as mock_check:
                with self.patch_start_agent(return_value=True):
                    with self.patch_raw_input() as mock_raw_input:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        mock_exit.assert_called_once_with(self.exit_msg)

    def test_failure_no_keygen_interrupt(self, mock_print):
        # The program is stopped if the user sends a SIGTERM.
        with mock.patch('sys.exit') as mock_exit:
            with self.patch_check_keys() as mock_check:
                with self.patch_start_agent(return_value=True):
                    with self.patch_raw_input(side_effect=KeyboardInterrupt) \
                            as mock_raw_input:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        mock_exit.assert_called_once_with(self.exit_msg)

    def test_keygen(self, mock_print):
        # Keys are automatically created on user request.
        with self.patch_check_keys() as mock_check:
            with self.patch_start_agent(return_value=True):
                with self.patch_raw_input(return_value='A') as mock_raw_input:
                    with self.patch_create_keys() as mock_create_keys:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        self.assertTrue(mock_create_keys.called)

    def test_watch(self, mock_print):
        # The function waits for the user to generate SSH keys.
        with self.patch_check_keys() as mock_check:
            with self.patch_start_agent(return_value=True):
                with self.patch_raw_input(return_value='M') as mock_raw_input:
                    with mock.patch('quickstart.ssh.watch_for_keys') \
                            as mock_watch_for_keys:
                        app.ensure_ssh_keys()
        self.assertTrue(mock_check.called)
        mock_print.assert_has_calls([mock.call(self.print_msg)])
        self.assertTrue(mock_raw_input.called)
        self.assertTrue(mock_watch_for_keys.called)

    def test_creation_error(self, mock_print):
        # Keys are automatically created on user request.
        error = OSError('bad wolf')
        with self.assert_program_exit('bad wolf'):
            with self.patch_check_keys():
                with self.patch_start_agent(return_value=True):
                    with self.patch_raw_input(return_value='A'):
                        with self.patch_create_keys(side_effect=error) \
                                as mock_create_keys:
                            app.ensure_ssh_keys()
        self.assertTrue(mock_create_keys.called)


@helpers.mock_print
class TestBootstrap(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    env_name = 'my-juju-env'
    status_message = 'retrieving the environment status'

    def make_status_output(self, agent_state, series='hoary'):
        """Create and return a YAML status output."""
        return yaml.safe_dump({
            'machines': {'0': {'agent-state': agent_state,
                               'series': series}},
        })

    def make_status_calls(self, number):
        """Return a list containing the given number of status calls."""
        call = mock.call(
            settings.JUJU_CMD, 'status', '-e', self.env_name,
            '--format', 'yaml')
        return [call for _ in range(number)]

    def make_side_effects(self):
        """Return the minimum number of side effects for a successful call."""
        return [
            (0, '', ''),  # Add a bootstrap call.
            (0, self.make_status_output('started'), ''),  # Add a status call.
        ]

    def assert_status_retried(self, side_effects):
        """Ensure the "juju status" command is retried several times.

        Receive the list of side effects the mock status call will return.
        """
        with self.patch_multiple_calls(side_effects) as mock_call:
            app.bootstrap(self.env_name)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(5))

    def test_success(self, mock_print):
        # The environment is successfully bootstrapped.
        with self.patch_multiple_calls(self.make_side_effects()) as mock_call:
            already_bootstrapped, series = app.bootstrap(self.env_name)
        self.assertFalse(already_bootstrapped)
        self.assertEqual(series, 'hoary')
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))
        mock_print.assert_called_once_with(self.status_message)

    def test_success_local_provider(self, mock_print):
        # The environment is bootstrapped with sudo using the local provider.
        with self.patch_multiple_calls(self.make_side_effects()) as mock_call:
            already_bootstrapped, series = app.bootstrap(
                self.env_name, requires_sudo=True)
        self.assertFalse(already_bootstrapped)
        self.assertEqual(series, 'hoary')
        mock_call.assert_has_calls([
            mock.call(
                'sudo', settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))
        mock_print.assert_called_once_with(self.status_message)

    def test_success_debug(self, mock_print):
        # The environment is successfully bootstrapped in debug mode.
        with self.patch_multiple_calls(self.make_side_effects()) as mock_call:
            already_bootstrapped, series = app.bootstrap(
                self.env_name, debug=True)
        self.assertFalse(already_bootstrapped)
        self.assertEqual(series, 'hoary')
        mock_call.assert_has_calls([
            mock.call(
                settings.JUJU_CMD, 'bootstrap', '-e', self.env_name,
                '--debug'),
        ] + self.make_status_calls(1))

    def test_already_bootstrapped(self, mock_print):
        # The function succeeds and returns True if the environment is already
        # bootstrapped.
        side_effects = [
            (1, '', '***environment is already bootstrapped**'),
            (0, self.make_status_output('started', 'precise'), ''),
        ]
        with self.patch_multiple_calls(side_effects) as mock_call:
            already_bootstrapped, series = app.bootstrap(self.env_name)
        self.assertTrue(already_bootstrapped)
        self.assertEqual(series, 'precise')
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))
        existing_message = 'reusing the already bootstrapped {} environment'
        mock_print.assert_has_calls([
            mock.call(existing_message.format(self.env_name)),
            mock.call(self.status_message),
        ])

    def test_bootstrap_failure(self, mock_print):
        # A ProgramExit is raised if an error occurs while bootstrapping.
        with self.patch_call(retcode=1, error='bad wolf') as mock_call:
            with self.assert_program_exit('bad wolf'):
                app.bootstrap(self.env_name)
        mock_call.assert_called_once_with(
            settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),

    def test_status_retry_error(self, mock_print):
        # Before raising a ProgramExit, the functions tries to call
        # "juju status" multiple times if it exits with an error.
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            # Add four status calls with a non-zero exit code.
            (1, '', 'these'),
            (2, '', 'are'),
            (3, '', 'the'),
            (4, '', 'voyages'),
            # Add a final valid status call.
            (0, self.make_status_output('started'), ''),
        ]
        self.assert_status_retried(side_effects)

    def test_status_retry_invalid_output(self, mock_print):
        # Before raising a ProgramExit, the functions tries to call
        # "juju status" multiple times if its output is not well formed or if
        # the agent is not started.
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (0, '', ''),  # Add the first status call: no output.
            (0, ':', ''),  # Add the second status call: not YAML.
            (0, 'just-a-string', ''),  # Add the third status call: bad YAML.
            # Add the fourth status call: the agent is still pending.
            (0, self.make_status_output('pending'), ''),
            # Add a final valid status call.
            (0, self.make_status_output('started'), ''),
        ]
        self.assert_status_retried(side_effects)

    def test_status_retry_both(self, mock_print):
        # Before raising a ProgramExit, the functions tries to call
        # "juju status" multiple times in any case.
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (1, '', 'error'),  # Add the first status call: error.
            (2, '', 'another error'),  # Add the second status call: error.
            # Add the third status call: the agent is still pending.
            (0, self.make_status_output('pending'), ''),
            (0, 'just-a-string', ''),  # Add the fourth status call: bad YAML.
            # Add a final valid status call.
            (0, self.make_status_output('started'), ''),
        ]
        self.assert_status_retried(side_effects)

    def test_agent_error(self, mock_print):
        # A ProgramExit is raised immediately if the Juju agent in the
        # bootstrap node is in an error state.
        status_output = self.make_status_output('error')
        side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (0, status_output, ''),  # Add the status call: agent error.
        ]
        expected = 'state server failure:\n{}'.format(status_output)
        with self.patch_multiple_calls(side_effects) as mock_call:
            with self.assert_program_exit(expected):
                app.bootstrap(self.env_name)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(1))

    def test_status_failure(self, mock_print):
        # A ProgramExit is raised if "juju status" keeps failing.
        call_side_effects = [
            (0, '', ''),  # Add the bootstrap call.
            (1, 'output1', 'error1'),  # Add the first status call: retried.
            (1, 'output2', 'error2'),  # Add the second status call: error.
        ]
        time_side_effects = [
            0,  # Start at time zero (expiration at time 600).
            10,  # First call before the timeout expiration.
            100,  # Second call before the timeout expiration.
            1000,  # Third call after the timeout expiration.
        ]
        mock_time = mock.Mock(side_effect=time_side_effects)
        expected = 'the state server is not ready:\noutput2error2'
        with self.patch_multiple_calls(call_side_effects) as mock_call:
            # Simulate the timeout expired: the first time call is used to
            # calculate the timeout, the second one for the first status check,
            # the third for the second status check, the fourth should fail.
            with mock.patch('time.time', mock_time):
                with self.assert_program_exit(expected):
                    app.bootstrap(self.env_name)
        mock_call.assert_has_calls([
            mock.call(settings.JUJU_CMD, 'bootstrap', '-e', self.env_name),
        ] + self.make_status_calls(2))


class TestGetValueFromJenv(unittest.TestCase):

    def test_no_key(self):
        with mock.patch('quickstart.manage.envs.load_generated',
                        lambda x: {}):
            with self.assertRaises(ValueError) as exc:
                app.get_value_from_jenv(
                    'local', '/home/bac/.juju', 'my-key')
        expected = (
            u'my-key not found in '
            '/home/bac/.juju/environments/local.jenv')
        self.assertIn(expected, bytes(exc.exception))

    def test_success(self):
        expected = 'superchunk'
        with mock.patch('quickstart.manage.envs.load_generated',
                        lambda x: {'my-key': expected}):
            secret = app.get_value_from_jenv(
                'local', '~bac/.juju', 'my-key')
        self.assertEqual(expected, secret)


class TestGetApiUrl(
        helpers.CallTestsMixin, ProgramExitTestsMixin, unittest.TestCase):

    env_name = 'ec2'

    def test_success(self):
        # The API URL is correctly returned.
        api_addresses = json.dumps(['api.example.com:17070', 'not-today'])
        with self.patch_call(retcode=0, output=api_addresses) as mock_call:
            api_url = app.get_api_url(self.env_name)
        self.assertEqual('wss://api.example.com:17070', api_url)
        mock_call.assert_called_once_with(
            settings.JUJU_CMD, 'api-endpoints', '-e', self.env_name,
            '--format', 'json')

    def test_failure(self):
        # A ProgramExit is raised if an error occurs retrieving the API URL.
        with self.patch_call(retcode=1, error='bad wolf') as mock_call:
            with self.assert_program_exit('bad wolf'):
                app.get_api_url(self.env_name)
        mock_call.assert_called_once_with(
            settings.JUJU_CMD, 'api-endpoints', '-e', self.env_name,
            '--format', 'json')


class TestConnect(ProgramExitTestsMixin, unittest.TestCase):

    admin_secret = 'Secret!'
    api_url = 'wss://api.example.com:17070'

    def test_connection_established(self):
        # The connection is done and the Environment instance is returned.
        with mock.patch('quickstart.juju.connect') as mock_connect:
            env = app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_once_with(self.api_url)
        mock_env = mock_connect()
        mock_env.login.assert_called_once_with(self.admin_secret)
        self.assertEqual(mock_env, env)

    @mock.patch('time.sleep')
    @mock.patch('logging.warn')
    def test_connection_error(self, mock_warn, mock_sleep):
        # if an error occurs in the connection, it retries and then raises.
        mock_connect = mock.Mock(side_effect=ValueError('bad wolf'))
        expected = 'unable to connect to the Juju API server on {}: bad wolf'
        with mock.patch('quickstart.juju.connect', mock_connect):
            with self.assert_program_exit(expected.format(self.api_url)):
                app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_with(self.api_url)
        self.assertEqual(30, mock_connect.call_count)
        mock_sleep.assert_called_with(1)
        self.assertEqual(29, mock_sleep.call_count)
        self.assertEqual(29, mock_warn.call_count)
        mock_warn.assert_called_with(
            'Retrying: ' + expected.format(self.api_url))

    @mock.patch('time.sleep')
    @mock.patch('logging.warn')
    def test_connection_retry(self, mock_warn, mock_sleep):
        # if an error occurs in the connection, it can succeed after retrying.
        mock_env = mock.Mock()
        mock_connect = mock.Mock(
            side_effect=[ValueError('bad wolf'), mock_env])
        with mock.patch('quickstart.juju.connect', mock_connect):
            env = app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_with(self.api_url)
        self.assertEqual(2, mock_connect.call_count)
        mock_env.login.assert_called_once_with(self.admin_secret)
        self.assertEqual(mock_env, env)
        mock_sleep.assert_called_once_with(1)
        expected = 'unable to connect to the Juju API server on {}: bad wolf'
        mock_warn.assert_called_once_with(
            'Retrying: ' + expected.format(self.api_url))

    def test_authentication_error(self):
        # A ProgramExit is raised if an error occurs in the authentication.
        expected = 'unable to log in to the Juju API server on {}: bad wolf'
        with mock.patch('quickstart.juju.connect') as mock_connect:
            mock_login = mock_connect().login
            mock_login.side_effect = self.make_env_error('bad wolf')
            with self.assert_program_exit(expected.format(self.api_url)):
                app.connect(self.api_url, self.admin_secret)
        mock_connect.assert_called_with(self.api_url)
        mock_login.assert_called_once_with(self.admin_secret)

    def test_other_errors(self):
        # Any other errors occurred during the log in process are not trapped.
        error = ValueError('explode!')
        with mock.patch('quickstart.juju.connect') as mock_connect:
            mock_login = mock_connect().login
            mock_login.side_effect = error
            with self.assertRaises(ValueError) as context_manager:
                app.connect(self.api_url, self.admin_secret)
        self.assertIs(error, context_manager.exception)


class TestCreateAuthToken(unittest.TestCase):

    def test_success(self):
        # A successful call returns a token.
        env = mock.Mock()
        token = 'TOKEN-STRING'
        env.create_auth_token.return_value = {
            'Token': token,
            'Created': '2013-11-21T12:34:46.778866Z',
            'Expires': '2013-11-21T12:36:46.778866Z'
        }
        self.assertEqual(token, app.create_auth_token(env))

    def test_legacy_failure(self):
        # A legacy charm call returns None.
        env = mock.Mock()
        error = jujuclient.EnvError(
            {'Error': 'unknown object type "GUIToken"'})
        env.create_auth_token.side_effect = error
        self.assertIsNone(app.create_auth_token(env))

    def test_other_errors(self):
        # Any other errors are not trapped.
        env = mock.Mock()
        error = jujuclient.EnvError({
            'Error': 'tokens can only be created by authenticated users.',
            'ErrorCode': 'unauthorized access'
        })
        env.create_auth_token.side_effect = error
        with self.assertRaises(jujuclient.EnvError) as context_manager:
            app.create_auth_token(env)
        self.assertIs(error, context_manager.exception)


@helpers.mock_print
class TestCheckEnvironment(
        ProgramExitTestsMixin, helpers.WatcherDataTestsMixin,
        unittest.TestCase):

    def make_env(self, include_data=False, side_effect=None):
        """Create and return a mock environment object.

        If include_data is True, set up the object so that a call to status
        returns a status object containing service and unit data.

        The side_effect argument can be used to simulate status errors.
        """
        env = mock.Mock()
        # Set up the get_status return value.
        status = []
        if include_data:
            status = [self.make_service_change(), self.make_unit_change()]
        env.get_status.return_value = status
        env.get_status.side_effect = side_effect
        return env

    def patch_get_charm_url(self, return_value=None, side_effect=None):
        """Patch the get_charm_url helper function."""
        mock_get_charm_url = mock.Mock(
            return_value=return_value, side_effect=side_effect)
        return mock.patch('quickstart.utils.get_charm_url', mock_get_charm_url)

    def test_environment_just_bootstrapped(self, mock_print):
        # The function correctly retrieves the charm URL and machine, and
        # handles the case when the charm URL is not provided by the user.
        # In this scenario, the environment has been bootstrapped by
        # quickstart, so there is no need to check its status. For this reason,
        # service_data and unit_data should be set to None.
        env = self.make_env()
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'trusty'
        check_preexisting = False
        with self.patch_get_charm_url(
                return_value='cs:trusty/juju-gui-42') as mock_get_charm_url:
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # There is no need to call status if the environment was just created.
        self.assertFalse(env.get_status.called)
        # The charm URL has been retrieved from charmworld based on the current
        # bootstrap node series.
        self.assertEqual('cs:trusty/juju-gui-42', url)
        mock_get_charm_url.assert_called_once_with(bootstrap_node_series)
        # Since the bootstrap node series is supported by the GUI charm, the
        # GUI unit can be deployed to machine 0.
        self.assertEqual('0', machine)
        # When not checking for pre-existing service and/or unit, the
        # corresponding service and unit data are set to None.
        self.assertIsNone(service_data)
        self.assertIsNone(unit_data)
        # Ensure the function output makes sense.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('bootstrap node series: trusty'),
            mock.call('charm URL: cs:trusty/juju-gui-42'),
        ])

    def test_existing_environment_without_entities(self, mock_print):
        # The function correctly retrieves the charm URL and machine.
        # In this scenario, the environment was already bootstrapped, but it
        # does not include the GUI. For this reason, service_data and unit_data
        # are set to None.
        env = self.make_env()
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'precise'
        check_preexisting = True
        with self.patch_get_charm_url(
                return_value='cs:precise/juju-gui-42') as mock_get_charm_url:
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # The environment status has been retrieved.
        env.get_status.assert_called_once_with()
        # The charm URL has been retrieved from charmworld based on the current
        # bootstrap node series.
        self.assertEqual('cs:precise/juju-gui-42', url)
        mock_get_charm_url.assert_called_once_with(bootstrap_node_series)
        # Since the bootstrap node series is supported by the GUI charm, the
        # GUI unit can be deployed to machine 0.
        self.assertEqual('0', machine)
        # The service and unit data are set to None.
        self.assertIsNone(service_data)
        self.assertIsNone(unit_data)
        # Ensure the function output makes sense.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('bootstrap node series: precise'),
            mock.call('charm URL: cs:precise/juju-gui-42'),
        ])

    def test_existing_environment_with_entities(self, mock_print):
        # The function correctly retrieves the charm URL and machine when the
        # environment is already bootstrapped and includes a Juju GUI unit.
        # In this case service_data and unit_data are actually populated.
        env = self.make_env(include_data=True)
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'precise'
        check_preexisting = True
        with self.patch_get_charm_url() as mock_get_charm_url:
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # The environment status has been retrieved.
        env.get_status.assert_called_once_with()
        # The charm URL has been retrieved from the environment.
        self.assertEqual('cs:precise/juju-gui-47', url)
        self.assertFalse(mock_get_charm_url.called)
        # Since the bootstrap node series is supported by the GUI charm, the
        # GUI unit can be safely deployed to machine 0.
        self.assertEqual('0', machine)
        # The service and unit data are correctly returned.
        self.assertEqual(self.make_service_data(), service_data)
        self.assertEqual(self.make_unit_data(), unit_data)

    def test_bootstrap_node_series_not_supported(self, mock_print):
        # If the bootstrap node is not suitable for hosting the Juju GUI unit,
        # the returned machine is set to None.
        env = self.make_env()
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'saucy'
        check_preexisting = False
        with self.patch_get_charm_url(
                return_value='cs:trusty/juju-gui-42') as mock_get_charm_url:
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # The charm URL has been retrieved from charmworld using the most
        # recent supported series.
        self.assertEqual('cs:trusty/juju-gui-42', url)
        mock_get_charm_url.assert_called_once_with('trusty')
        # The Juju GUI unit cannot be deployed to saucy machine 0.
        self.assertIsNone(machine)
        # Ensure the function output makes sense.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('bootstrap node series: saucy'),
            mock.call('charm URL: cs:trusty/juju-gui-42'),
        ])

    def test_local_provider(self, mock_print):
        # If the local provider is used the Juju GUI unit cannot be deployed to
        # machine 0.
        env = self.make_env()
        charm_url = None
        env_type = 'local'
        bootstrap_node_series = 'trusty'
        check_preexisting = False
        with self.patch_get_charm_url(return_value='cs:trusty/juju-gui-42'):
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # The charm URL has been correctly retrieved from charmworld.
        self.assertEqual('cs:trusty/juju-gui-42', url)
        # The Juju GUI unit cannot be deployed to localhost.
        self.assertIsNone(machine)

    def test_default_charm_url(self, mock_print):
        # A default charm URL suitable to be deployed in the bootstrap node is
        # returned if the charmworld API is not reachable.
        env = self.make_env()
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'precise'
        check_preexisting = False
        with self.patch_get_charm_url(side_effect=IOError('boo!')):
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # The default charm URL for the given series is returned.
        self.assertEqual(settings.DEFAULT_CHARM_URLS['precise'], url)
        self.assertEqual('0', machine)

    def test_most_recent_default_charm_url(self, mock_print):
        # The default charm URL corresponding to the most recent series
        # supported by the GUI is returned if the charmworld API is not
        # reachable and the bootstrap node cannot host the Juju GUI unit.
        env = self.make_env()
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'saucy'
        check_preexisting = False
        with self.patch_get_charm_url(side_effect=IOError('boo!')):
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # The default charm URL for the given series is returned.
        series = settings.JUJU_GUI_SUPPORTED_SERIES[-1]
        self.assertEqual(settings.DEFAULT_CHARM_URLS[series], url)
        self.assertIsNone(machine)

    def test_charm_url_provided(self, mock_print):
        # The function knows when a custom charm URL can be deployed in the
        # bootstrap node.
        env = self.make_env()
        charm_url = 'cs:~juju-gui/trusty/juju-gui-100'
        env_type = 'ec2'
        bootstrap_node_series = 'trusty'
        check_preexisting = False
        with self.patch_get_charm_url() as mock_get_charm_url:
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # There is no need to call the charmword API if the charm URL is
        # provided by the user.
        self.assertFalse(mock_get_charm_url.called)
        # The provided charm URL has been correctly returned.
        self.assertEqual(charm_url, url)
        # Since the provided charm series is trusty, the charm itself can be
        # safely deployed to machine 0.
        self.assertEqual('0', machine)
        # Ensure the function output makes sense.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('bootstrap node series: trusty'),
            mock.call('charm URL: cs:~juju-gui/trusty/juju-gui-100'),
        ])

    def test_charm_url_provided_series_not_supported(self, mock_print):
        # The function knows when a custom charm URL cannot be deployed in the
        # bootstrap node.
        env = self.make_env()
        charm_url = 'cs:~juju-gui/trusty/juju-gui-100'
        env_type = 'ec2'
        bootstrap_node_series = 'precise'
        check_preexisting = False
        with self.patch_get_charm_url() as mock_get_charm_url:
            url, machine, service_data, unit_data = app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        # There is no need to call the charmword API if the charm URL is
        # provided by the user.
        self.assertFalse(mock_get_charm_url.called)
        # The provided charm URL has been correctly returned.
        self.assertEqual(charm_url, url)
        # Since the provided charm series is not precise, the charm must be
        # deployed to a new machine.
        self.assertIsNone(machine)
        # Ensure the function output makes sense.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('bootstrap node series: precise'),
            mock.call('charm URL: cs:~juju-gui/trusty/juju-gui-100'),
        ])

    def test_status_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the status API call.
        env = self.make_env(side_effect=self.make_env_error('bad wolf'))
        charm_url = None
        env_type = 'ec2'
        bootstrap_node_series = 'trusty'
        check_preexisting = True
        with self.assert_program_exit('bad API response: bad wolf'):
            app.check_environment(
                env, 'my-gui', charm_url, env_type, bootstrap_node_series,
                check_preexisting)
        env.get_status.assert_called_once_with()


@helpers.mock_print
class TestDeployGui(
        ProgramExitTestsMixin, helpers.WatcherDataTestsMixin,
        unittest.TestCase):

    charm_url = 'cs:trusty/juju-gui-42'

    def make_env(self, unit_name=None):
        """Create and return a mock environment object.

        Set up the mock object so that a call to env.add_unit returns the given
        unit_name.
        """
        env = mock.Mock()
        # Set up the add_unit return value.
        if unit_name is not None:
            env.add_unit.return_value = {'Units': [unit_name]}
        return env

    def test_deployment(self, mock_print):
        # The function correctly deploys and exposes the service in the case
        # the service and its unit are not present in the environment.
        env = self.make_env(unit_name='my-gui/42')
        service_data = unit_data = None
        unit_name = app.deploy_gui(
            env, 'my-gui', self.charm_url, '0', service_data, unit_data)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            # The service has been deployed.
            mock.call.deploy('my-gui', self.charm_url, num_units=0),
            # The service has been exposed.
            mock.call.expose('my-gui'),
            # One service unit has been added.
            mock.call.add_unit('my-gui', machine_spec='0'),
        ])
        self.assertEqual(5, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('requesting my-gui deployment'),
            mock.call('my-gui deployment request accepted'),
            mock.call('exposing service my-gui'),
            mock.call('requesting new unit deployment'),
            mock.call('my-gui/42 deployment request accepted'),
        ])

    def test_existing_service(self, mock_print):
        # The deployment is executed reusing an already deployed service.
        env = self.make_env(unit_name='my-gui/42')
        service_data = self.make_service_data()
        unit_data = None
        unit_name = app.deploy_gui(
            env, 'my-gui', self.charm_url, '0', service_data, unit_data)
        self.assertEqual('my-gui/42', unit_name)
        # One service unit has been added.
        env.add_unit.assert_called_once_with('my-gui', machine_spec='0')
        # The service is not re-deployed.
        self.assertFalse(env.deploy.called)
        # The service is not re-exposed.
        self.assertFalse(env.expose.called)
        self.assertEqual(3, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('requesting new unit deployment'),
            mock.call('my-gui/42 deployment request accepted'),
        ])

    def test_existing_service_unexposed(self, mock_print):
        # The existing service is exposed if required.
        env = self.make_env(unit_name='my-gui/42')
        service_data = self.make_service_data({'Exposed': False})
        unit_data = None
        unit_name = app.deploy_gui(
            env, 'my-gui', self.charm_url, '1', service_data, unit_data)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            # The service has been exposed.
            mock.call.expose('my-gui'),
            # One service unit has been added.
            mock.call.add_unit('my-gui', machine_spec='1'),
        ])
        # The service is not re-deployed.
        self.assertFalse(env.deploy.called)
        self.assertEqual(4, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('exposing service my-gui'),
            mock.call('requesting new unit deployment'),
            mock.call('my-gui/42 deployment request accepted'),
        ])

    def test_existing_service_and_unit(self, mock_print):
        # A unit is reused if a suitable one is already present.
        env = self.make_env()
        service_data = self.make_service_data()
        unit_data = self.make_unit_data()
        unit_name = app.deploy_gui(
            env, 'my-gui', self.charm_url, '0', service_data, unit_data)
        self.assertEqual('my-gui/47', unit_name)
        # The service is not re-deployed.
        self.assertFalse(env.deploy.called)
        # The service is not re-exposed.
        self.assertFalse(env.expose.called)
        # The unit is not re-added.
        self.assertFalse(env.add_unit.called)
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('service my-gui already deployed'),
            mock.call('reusing unit my-gui/47'),
        ])

    def test_new_machine(self, mock_print):
        # The unit is correctly deployed in a new machine.
        env = self.make_env(unit_name='my-gui/42')
        service_data = unit_data = None
        unit_name = app.deploy_gui(
            env, 'my-gui', self.charm_url, None, service_data, unit_data)
        self.assertEqual('my-gui/42', unit_name)
        env.assert_has_calls([
            # The service has been deployed.
            mock.call.deploy('my-gui', self.charm_url, num_units=0),
            # The service has been exposed.
            mock.call.expose('my-gui'),
            # One service unit has been added to a new machine.
            mock.call.add_unit('my-gui', machine_spec=None),
        ])

    def test_deploy_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the deploy API call.
        env = self.make_env()
        env.deploy.side_effect = self.make_env_error('bad wolf')
        service_data = unit_data = None
        with self.assert_program_exit('bad API response: bad wolf'):
            app.deploy_gui(
                env, 'another-gui', self.charm_url, '0',
                service_data, unit_data)
        env.deploy.assert_called_once_with(
            'another-gui', self.charm_url, num_units=0)

    def test_expose_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the expose API call.
        env = self.make_env()
        env.expose.side_effect = self.make_env_error('bad wolf')
        service_data = unit_data = None
        with self.assert_program_exit('bad API response: bad wolf'):
            app.deploy_gui(
                env, 'another-gui', self.charm_url, '0',
                service_data, unit_data)
        env.expose.assert_called_once_with('another-gui')

    def test_add_unit_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in the add_unit API call.
        env = self.make_env()
        env.add_unit.side_effect = self.make_env_error('bad wolf')
        service_data = unit_data = None
        with self.assert_program_exit('bad API response: bad wolf'):
            app.deploy_gui(
                env, 'another-gui', self.charm_url, '0',
                service_data, unit_data)
        env.add_unit.assert_called_once_with('another-gui', machine_spec='0')

    def test_other_errors(self, mock_print):
        # Any other errors occurred during the process are not trapped.
        error = ValueError('explode!')
        env = self.make_env(unit_name='my-gui/42')
        env.expose.side_effect = error
        service_data = unit_data = None
        with self.assertRaises(ValueError) as context_manager:
            app.deploy_gui(
                env, 'juju-gui', self.charm_url, '0',
                service_data, unit_data)
        env.deploy.assert_called_once_with(
            'juju-gui', self.charm_url, num_units=0)
        env.expose.assert_called_once_with('juju-gui')
        self.assertIs(error, context_manager.exception)


@helpers.mock_print
class TestWatch(
        ProgramExitTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    address = 'unit.example.com'
    machine_pending_call = mock.call('machine 0 provisioning is pending')
    unit_placed_machine_call = mock.call('unit placed on unit.example.com')
    machine_started_call = mock.call('machine 0 is started')
    unit_pending_call = mock.call('django/42 deployment is pending')
    unit_placed_unit_call = mock.call('django/42 placed on {}'.format(address))
    unit_installed_call = mock.call('django/42 is installed')
    unit_started_call = mock.call('django/42 is ready on machine 0')

    def make_env(self, changes):
        """Create and return a patched Environment instance.

        The watch_changes method of the resulting Environment object returns
        the provided changes.
        """
        env = mock.Mock()
        env.watch_changes().next.side_effect = changes
        return env

    def make_machine_change(self, status, name='0', address=None):
        """Create and return a machine change.

        If the address argument is None, the change does not include the
        corresponding address field.
        """
        data = {'Id': name, 'Status': status}
        if address is not None:
            data['Addresses'] = [{
                'NetworkName': '',
                'NetworkScope': 'public',
                'Type': 'hostname',
                'Value': address,
            }]
        return 'change', data

    def make_unit_change(self, status, name='django/42', address=None):
        """Create and return a unit change.

        If the address argument is None, the change does not include the
        corresponding address field.
        """
        data = {'MachineId': '0', 'Name': name, 'Status': status}
        if address is not None:
            data['PublicAddress'] = address
        return 'change', data

    # The following group of tests exercises both the function return value and
    # the function output, even if the output is handled by sub-functions.
    # This is done to simulate the different user experiences of observing the
    # environment evolution while the unit is deploying.

    def test_unit_life(self, mock_print):
        # The glorious moments in the unit's life are properly highlighted.
        # The machine achievements are also celebrated.
        env = self.make_env([
            ([self.make_unit_change('pending', address='')],
             [self.make_machine_change('pending')]),
            ([], [self.make_machine_change('started')]),
            ([self.make_unit_change('pending', address=self.address)], []),
            ([self.make_unit_change('installed', address=self.address)], []),
            ([self.make_unit_change('started', address=self.address)], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_pending_call,
            self.machine_started_call,
            self.unit_placed_unit_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_unit_life_with_machine_address(self, mock_print):
        # The glorious moments in the unit's life are properly highlighted.
        # The machine achievements are also celebrated.
        # This time the new mega-watcher behavior is simulated, in which
        # addresses are included in the machine change.
        env = self.make_env([
            ([self.make_unit_change('pending')],
             [self.make_machine_change('pending', address='')]),
            ([], [self.make_machine_change('started', address=self.address)]),
            ([self.make_unit_change('pending')], []),
            ([self.make_unit_change('installed')], []),
            ([self.make_unit_change('started')], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_pending_call,
            self.unit_placed_machine_call,
            self.machine_started_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_weird_order(self, mock_print):
        # Strange unit evolutions are handled.
        env = self.make_env([
            # The unit is first reachable and then pending. The machine starts
            # when the unit is already installed. All of this makes no sense
            # and should never happen, but if it does, we deal with it.
            ([self.make_unit_change('pending', address=self.address)], []),
            ([self.make_unit_change('pending', address='')],
             [self.make_machine_change('pending')]),
            ([self.make_unit_change('installed', address=self.address)], []),
            ([], [self.make_machine_change('started')]),
            ([self.make_unit_change('started', address=self.address)], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_placed_unit_call,
            self.unit_pending_call,
            self.machine_pending_call,
            self.unit_installed_call,
            self.machine_started_call,
            self.unit_started_call,
        ])

    def test_missing_changes(self, mock_print):
        # Only the unit started change is strictly required when the unit
        # change includes the public address.
        env = self.make_env([
            ([self.make_unit_change('started', address=self.address)], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_placed_unit_call,
            self.unit_started_call,
        ])

    def test_missing_changes_with_machine_address(self, mock_print):
        # When using the new mega-watcher, a machine change including its
        # public address is also required.
        env = self.make_env([
            ([self.make_unit_change('started')], []),
            ([], [self.make_machine_change('started', address=self.address)]),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(3, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_started_call,
            self.unit_placed_machine_call,
            self.machine_started_call,
        ])

    def test_ignored_machine_changes(self, mock_print):
        # All machine changes are ignored until the application knows what
        # machine the unit belongs to.
        env = self.make_env([
            ([], [self.make_machine_change('pending')]),
            ([], [self.make_machine_change('started')]),
            ([self.make_unit_change('started', address=self.address)], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        # No machine related messages have been printed.
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_placed_unit_call,
            self.unit_started_call,
        ])

    def test_ignored_machine_changes_with_machine_address(self, mock_print):
        # All machine changes are ignored until the application knows what
        # machine the unit belongs to. When the above happens, previously
        # collected machine changes are still parsed in the case the address
        # is not yet known.
        env = self.make_env([
            ([], [self.make_machine_change('pending')]),
            ([],
             [self.make_machine_change('installed', address=self.address)]),
            ([], [self.make_machine_change('started', address=self.address)]),
            ([self.make_unit_change('started')], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        # No machine related messages have been printed.
        self.assertEqual(3, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_started_call,
            self.unit_placed_machine_call,
            self.machine_started_call,
        ])

    def test_unit_already_deployed(self, mock_print):
        # Simulate the unit we are observing has been already deployed.
        # This happens, e.g., when executing Quickstart a second time, and both
        # the unit and the machine are already started.
        env = self.make_env([
            ([self.make_unit_change('started', address=self.address)],
             [self.make_machine_change('started')]),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(2, mock_print.call_count)

    def test_unit_already_deployed_with_machine_address(self, mock_print):
        # Simulate the unit we are observing has been already deployed.
        # This happens, e.g., when executing Quickstart a second time, and both
        # the unit and the machine are already started.
        # This time the new mega-watcher behavior is simulated, in which
        # addresses are included in the machine change.
        env = self.make_env([
            ([self.make_unit_change('started')],
             [self.make_machine_change('started', address=self.address)]),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(3, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_started_call,
            self.unit_placed_machine_call,
            self.machine_started_call,
        ])

    def test_machine_already_started(self, mock_print):
        # Simulate the unit is being deployed on an already started machine.
        # This happens, e.g., when running Quickstart on a non-local
        # environment type: the unit is deployed on the bootstrap node, which
        # is assumed to be started.
        env = self.make_env([
            ([self.make_unit_change('pending', address='')],
             [self.make_machine_change('started')]),
            ([self.make_unit_change('pending', address=self.address)], []),
            ([self.make_unit_change('installed', address=self.address)], []),
            ([self.make_unit_change('started', address=self.address)], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(5, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_started_call,
            self.unit_placed_unit_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_machine_already_started_with_machine_address(self, mock_print):
        # Simulate the unit is being deployed on an already started machine.
        # This happens, e.g., when running Quickstart on a non-local
        # environment type: the unit is deployed on the bootstrap node, which
        # is assumed to be started.
        # This time the new mega-watcher behavior is simulated, in which
        # addresses are included in the machine change.
        env = self.make_env([
            ([self.make_unit_change('pending')],
             [self.make_machine_change('started', address=self.address)]),
            ([self.make_unit_change('pending')], []),
            ([self.make_unit_change('installed')], []),
            ([self.make_unit_change('started')], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(5, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.unit_placed_machine_call,
            self.machine_started_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_extraneous_changes(self, mock_print):
        # Changes to units or machines we are not observing are ignored. Also
        # ensure that repeated changes to a single entity are ignored, even if
        # they are unlikely to happen.
        pending_unit_change = self.make_unit_change('pending', address='')
        started_unit_change = self.make_unit_change(
            'started', address=self.address)
        env = self.make_env([
            # Add a repeated change.
            ([pending_unit_change, pending_unit_change],
             [self.make_machine_change('pending')]),
            # Add extraneous unit and machine changes.
            ([self.make_unit_change('pending', name='haproxy/0')],
             [self.make_machine_change('pending', name='42')]),
            # Add a change to an extraneous machine.
            ([], [self.make_machine_change('started', name='42'),
                  self.make_machine_change('started')]),
            # Add a change to an extraneous unit.
            ([self.make_unit_change('started', name='haproxy/0'),
              self.make_unit_change('pending', address=self.address)], []),
            ([self.make_unit_change('installed', address=self.address)], []),
            # Add another repeated change.
            ([started_unit_change, started_unit_change], []),
        ])
        address = app.watch(env, 'django/42')
        self.assertEqual(self.address, address)
        self.assertEqual(6, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_pending_call,
            self.machine_pending_call,
            self.machine_started_call,
            self.unit_placed_unit_call,
            self.unit_installed_call,
            self.unit_started_call,
        ])

    def test_api_error(self, mock_print):
        # A ProgramExit is raised if an error occurs in one of the API calls.
        env = self.make_env([
            ([self.make_unit_change('pending', address='')], []),
            self.make_env_error('next returned an error'),
        ])
        expected = 'bad API server response: next returned an error'
        with self.assert_program_exit(expected):
            app.watch(env, 'django/42')
        self.assertEqual(1, mock_print.call_count)
        mock_print.assert_has_calls([self.unit_pending_call])

    def test_other_errors(self, mock_print):
        # Any other errors occurred during the process are not trapped.
        env = self.make_env([
            ([self.make_unit_change('installed', address=self.address)], []),
            ValueError('explode!'),
        ])
        with self.assert_value_error('explode!'):
            app.watch(env, 'django/42')
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            self.unit_placed_unit_call, self.unit_installed_call])

    def test_machine_status_error(self, mock_print):
        # A ProgramExit is raised if an the machine is found in an error state.
        change_machine_error = ('change', {
            'Id': '0',
            'Status': 'error',
            'StatusInfo': 'oddities',
        })
        self.make_machine_change('error')
        # The unit pending change is required to make the function know which
        # machine to observe.
        env = self.make_env([
            ([self.make_unit_change('pending', address='')],
             [change_machine_error]),
        ])
        expected = 'machine 0 is in an error state: error: oddities'
        with self.assert_program_exit(expected):
            app.watch(env, 'django/42')
        self.assertEqual(1, mock_print.call_count)
        mock_print.assert_has_calls([self.unit_pending_call])

    def test_unit_status_error(self, mock_print):
        # A ProgramExit is raised if an the unit is found in an error state.
        change_unit_error = ('change', {
            'MachineId': '0',
            'Name': 'django/42',
            'Status': 'error',
            'StatusInfo': 'install failure',
        })
        env = self.make_env([([change_unit_error], [])])
        expected = 'django/42 is in an error state: error: install failure'
        with self.assert_program_exit(expected):
            app.watch(env, 'django/42')
        self.assertFalse(mock_print.called)


class TestDeployBundle(ProgramExitTestsMixin, unittest.TestCase):

    name = 'mybundle'
    yaml = 'mybundle: contents'
    bundle_id = '~fake/basket/bundle'

    def test_bundle_deployment(self):
        # A bundle is successfully deployed.
        env = mock.Mock()
        app.deploy_bundle(env, self.yaml, self.name, self.bundle_id)
        env.deploy_bundle.assert_called_once_with(
            self.yaml, name=self.name, bundle_id=self.bundle_id)
        self.assertFalse(env.close.called)

    def test_api_error(self):
        # A ProgramExit is raised if an error occurs in one of the API calls.
        env = mock.Mock()
        env.deploy_bundle.side_effect = self.make_env_error(
            'bundle deployment failure')
        expected = 'bad API server response: bundle deployment failure'
        with self.assert_program_exit(expected):
            app.deploy_bundle(env, self.yaml, self.name, self.bundle_id)

    def test_other_errors(self):
        # Any other errors occurred during the process are not trapped.
        env = mock.Mock()
        error = ValueError('explode!')
        env.deploy_bundle.side_effect = error
        with self.assertRaises(ValueError) as context_manager:
            app.deploy_bundle(env, self.yaml, self.name, None)
        self.assertIs(error, context_manager.exception)
