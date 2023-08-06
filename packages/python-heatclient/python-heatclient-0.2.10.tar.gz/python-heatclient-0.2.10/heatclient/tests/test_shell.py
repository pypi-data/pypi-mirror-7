# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import six
from six.moves.urllib import parse
from six.moves.urllib import request
import sys

import fixtures
import tempfile
import testscenarios
import testtools

from heatclient.openstack.common import jsonutils
from heatclient.openstack.common import strutils
from mox3 import mox

from keystoneclient.v2_0 import client as ksclient

from heatclient.common import http
from heatclient import exc
import heatclient.shell
from heatclient.tests import fakes


load_tests = testscenarios.load_tests_apply_scenarios
TEST_VAR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'var'))


class TestCase(testtools.TestCase):

    def set_fake_env(self, fake_env):
        client_env = ('OS_USERNAME', 'OS_PASSWORD', 'OS_TENANT_ID',
                      'OS_TENANT_NAME', 'OS_AUTH_URL', 'OS_REGION_NAME',
                      'OS_AUTH_TOKEN', 'OS_NO_CLIENT_AUTH', 'OS_SERVICE_TYPE',
                      'OS_ENDPOINT_TYPE', 'HEAT_URL')

        for key in client_env:
            self.useFixture(
                fixtures.EnvironmentVariable(key, fake_env.get(key)))

    # required for testing with Python 2.6
    def assertRegexpMatches(self, text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, six.string_types):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (
                msg, expected_regexp.pattern, text)
            raise self.failureException(msg)

    def shell_error(self, argstr, error_match):
        orig = sys.stderr
        sys.stderr = six.StringIO()
        _shell = heatclient.shell.HeatShell()
        e = self.assertRaises(Exception, _shell.main, argstr.split())
        self.assertRegexpMatches(e.__str__(), error_match)
        err = sys.stderr.getvalue()
        sys.stderr.close()
        sys.stderr = orig
        return err


class EnvVarTest(TestCase):

    scenarios = [
        ('username', dict(
            remove='OS_USERNAME',
            err='You must provide a username')),
        ('password', dict(
            remove='OS_PASSWORD',
            err='You must provide a password')),
        ('tenant_name', dict(
            remove='OS_TENANT_NAME',
            err='You must provide a tenant_id')),
        ('auth_url', dict(
            remove='OS_AUTH_URL',
            err='You must provide an auth url')),
    ]

    def test_missing_auth(self):

        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        fake_env[self.remove] = None
        self.set_fake_env(fake_env)
        self.shell_error('stack-list', self.err)


class EnvVarTestToken(TestCase):

    scenarios = [
        ('tenant_id', dict(
            remove='OS_TENANT_ID',
            err='You must provide a tenant_id')),
        ('auth_url', dict(
            remove='OS_AUTH_URL',
            err='You must provide an auth url')),
    ]

    def test_missing_auth(self):

        fake_env = {
            'OS_AUTH_TOKEN': 'atoken',
            'OS_TENANT_ID': 'tenant_id',
            'OS_AUTH_URL': 'http://no.where',
        }
        fake_env[self.remove] = None
        self.set_fake_env(fake_env)
        self.shell_error('stack-list', self.err)


class ShellParamValidationTest(TestCase):

    scenarios = [
        ('create', dict(
            command='create ts -P "a!b"',
            err='Malformed parameter')),
        ('stack-create', dict(
            command='stack-create ts -P "ab"',
            err='Malformed parameter')),
        ('update', dict(
            command='update ts -P "a~b"',
            err='Malformed parameter')),
        ('stack-update', dict(
            command='stack-update ts -P "a-b"',
            err='Malformed parameter')),
    ]

    def setUp(self):
        super(ShellParamValidationTest, self).setUp()
        self.m = mox.Mox()
        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)

    def test_bad_parameters(self):
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(http.HTTPClient, 'json_request')
        fakes.script_keystone_client()

        self.m.ReplayAll()
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        cmd = '%s --template-file=%s ' % (self.command, template_file)
        self.shell_error(cmd, self.err)


class ShellValidationTest(TestCase):

    def setUp(self):
        super(ShellValidationTest, self).setUp()
        self.m = mox.Mox()
        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)

    def test_failed_auth(self):
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(http.HTTPClient, 'json_request')
        fakes.script_keystone_client()
        failed_msg = 'Unable to authenticate user with credentials provided'
        http.HTTPClient.json_request(
            'GET', '/stacks?').AndRaise(exc.Unauthorized(failed_msg))

        self.m.ReplayAll()
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        self.shell_error('stack-list', failed_msg)

    def test_stack_create_validation(self):
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(http.HTTPClient, 'json_request')
        fakes.script_keystone_client()

        self.m.ReplayAll()
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        self.shell_error(
            'stack-create teststack '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"',
            'Need to specify exactly one of')


class ShellBase(TestCase):

    def setUp(self):
        super(ShellBase, self).setUp()
        self.m = mox.Mox()
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(http.HTTPClient, 'json_request')
        self.m.StubOutWithMock(http.HTTPClient, 'raw_request')
        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)

        # Some tests set exc.verbose = 1, so reset on cleanup
        def unset_exc_verbose():
            exc.verbose = 0

        self.addCleanup(unset_exc_verbose)

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = six.StringIO()
            _shell = heatclient.shell.HeatShell()
            _shell.main(argstr.split())
            self.subcommands = _shell.subcommands.keys()
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(0, exc_value.code)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig

        return out


class ShellTestCommon(ShellBase):

    def setUp(self):
        super(ShellTestCommon, self).setUp()

    def test_help_unknown_command(self):
        self.assertRaises(exc.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '^usage: heat',
            '(?m)^See "heat help COMMAND" for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)

    def test_command_help(self):
        output = self.shell('help help')
        self.assertIn('usage: heat help [<subcommand>]', output)
        subcommands = list(self.subcommands)
        for command in subcommands:
            if command.replace('_', '-') == 'bash-completion':
                continue
            output1 = self.shell('help %s' % command)
            output2 = self.shell('%s --help' % command)
            self.assertEqual(output1, output2)
            self.assertRegexpMatches(output1, '^usage: heat %s' % command)

    def test_debug_switch_raises_error(self):
        fakes.script_keystone_client()
        http.HTTPClient.json_request(
            'GET', '/stacks?').AndRaise(exc.Unauthorized("FAIL"))

        self.m.ReplayAll()

        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        args = ['--debug', 'stack-list']
        self.assertRaises(exc.Unauthorized, heatclient.shell.main, args)

    def test_dash_d_switch_raises_error(self):
        fakes.script_keystone_client()
        http.HTTPClient.json_request(
            'GET', '/stacks?').AndRaise(exc.CommandError("FAIL"))

        self.m.ReplayAll()

        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        args = ['-d', 'stack-list']
        self.assertRaises(exc.CommandError, heatclient.shell.main, args)

    def test_no_debug_switch_no_raises_errors(self):
        fakes.script_keystone_client()
        http.HTTPClient.json_request(
            'GET', '/stacks?').AndRaise(exc.Unauthorized("FAIL"))

        self.m.ReplayAll()

        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        args = ['stack-list']
        self.assertRaises(SystemExit, heatclient.shell.main, args)

    def test_help_on_subcommand(self):
        required = [
            '^usage: heat stack-list',
            "(?m)^List the user's stacks",
        ]
        argstrings = [
            'help stack-list',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)


class ShellTestUserPass(ShellBase):

    def setUp(self):
        super(ShellTestUserPass, self).setUp()
        self._set_fake_env()

    # Patch os.environ to avoid required auth info.
    def _set_fake_env(self):
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)

    def _script_keystone_client(self):
        fakes.script_keystone_client()

    def test_stack_list(self):
        self._script_keystone_client()
        fakes.script_heat_list()

        self.m.ReplayAll()

        list_text = self.shell('stack-list')

        required = [
            'id',
            'stack_status',
            'creation_time',
            'teststack',
            '1',
            'CREATE_COMPLETE',
            'IN_PROGRESS',
        ]
        for r in required:
            self.assertRegexpMatches(list_text, r)

    def test_stack_list_with_args(self):
        self._script_keystone_client()
        expected_url = '/stacks?%s' % parse.urlencode({
            'limit': 2,
            'status': ['COMPLETE', 'FAILED'],
            'marker': 'fake_id',
            'global_tenant': True,
            'show_deleted': 'True',
        }, True)
        fakes.script_heat_list(expected_url)

        self.m.ReplayAll()

        list_text = self.shell('stack-list'
                               ' --limit 2'
                               ' --marker fake_id'
                               ' --filters=status=COMPLETE'
                               ' --filters=status=FAILED'
                               ' --global-tenant'
                               ' --show-deleted')

        required = [
            'teststack',
            'teststack2',
        ]
        for r in required:
            self.assertRegexpMatches(list_text, r)

    def test_parsable_error(self):
        message = "The Stack (bad) could not be found."
        resp_dict = {
            "explanation": "The resource could not be found.",
            "code": 404,
            "error": {
                "message": message,
                "type": "StackNotFound",
                "traceback": "",
            },
            "title": "Not Found"
        }

        self._script_keystone_client()
        fakes.script_heat_error(jsonutils.dumps(resp_dict))

        self.m.ReplayAll()

        e = self.assertRaises(exc.HTTPException, self.shell, "stack-show bad")
        self.assertEqual("ERROR: " + message, str(e))

    def test_parsable_verbose(self):
        message = "The Stack (bad) could not be found."
        resp_dict = {
            "explanation": "The resource could not be found.",
            "code": 404,
            "error": {
                "message": message,
                "type": "StackNotFound",
                "traceback": "<TRACEBACK>",
            },
            "title": "Not Found"
        }

        self._script_keystone_client()
        fakes.script_heat_error(jsonutils.dumps(resp_dict))

        self.m.ReplayAll()

        exc.verbose = 1

        e = self.assertRaises(exc.HTTPException, self.shell, "stack-show bad")
        self.assertIn(message, str(e))

    def test_parsable_malformed_error(self):
        invalid_json = "ERROR: {Invalid JSON Error."
        self._script_keystone_client()
        fakes.script_heat_error(invalid_json)
        self.m.ReplayAll()
        e = self.assertRaises(exc.HTTPException, self.shell, "stack-show bad")
        self.assertEqual("ERROR: " + invalid_json, str(e))

    def test_parsable_malformed_error_missing_message(self):
        missing_message = {
            "explanation": "The resource could not be found.",
            "code": 404,
            "error": {
                "type": "StackNotFound",
                "traceback": "",
            },
            "title": "Not Found"
        }

        self._script_keystone_client()
        fakes.script_heat_error(jsonutils.dumps(missing_message))
        self.m.ReplayAll()

        e = self.assertRaises(exc.HTTPException, self.shell, "stack-show bad")
        self.assertEqual("ERROR: Internal Error", str(e))

    def test_parsable_malformed_error_missing_traceback(self):
        message = "The Stack (bad) could not be found."
        resp_dict = {
            "explanation": "The resource could not be found.",
            "code": 404,
            "error": {
                "message": message,
                "type": "StackNotFound",
            },
            "title": "Not Found"
        }

        self._script_keystone_client()
        fakes.script_heat_error(jsonutils.dumps(resp_dict))
        self.m.ReplayAll()

        exc.verbose = 1

        e = self.assertRaises(exc.HTTPException, self.shell, "stack-show bad")
        self.assertEqual("ERROR: The Stack (bad) could not be found.\n",
                         str(e))

    def test_stack_show(self):
        self._script_keystone_client()
        resp_dict = {"stack": {
            "id": "1",
            "stack_name": "teststack",
            "stack_status": 'CREATE_COMPLETE',
            "creation_time": "2012-10-25T01:58:47Z"
        }}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        http.HTTPClient.json_request(
            'GET', '/stacks/teststack/1').AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        list_text = self.shell('stack-show teststack/1')

        required = [
            'id',
            'stack_name',
            'stack_status',
            'creation_time',
            'teststack',
            'CREATE_COMPLETE',
            '2012-10-25T01:58:47Z'
        ]
        for r in required:
            self.assertRegexpMatches(list_text, r)

    def test_stack_abandon(self):
        self._script_keystone_client()

        resp_dict = {"stack": {
            "id": "1",
            "stack_name": "teststack",
            "stack_status": 'CREATE_COMPLETE',
            "creation_time": "2012-10-25T01:58:47Z"
        }}

        abandoned_stack = {
            "action": "CREATE",
            "status": "COMPLETE",
            "name": "teststack",
            "id": "1",
            "resources": {
                "foo": {
                    "name": "foo",
                    "resource_id": "test-res-id",
                    "action": "CREATE",
                    "status": "COMPLETE",
                    "resource_data": {},
                    "metadata": {},
                }
            }
        }

        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        http.HTTPClient.json_request(
            'GET', '/stacks/teststack/1').AndReturn((resp, resp_dict))
        http.HTTPClient.json_request(
            'DELETE',
            '/stacks/teststack/1/abandon').AndReturn((resp, abandoned_stack))

        self.m.ReplayAll()
        abandon_resp = self.shell('stack-abandon teststack/1')
        self.assertEqual(abandoned_stack, jsonutils.loads(abandon_resp))

    def _output_fake_response(self):
        self._script_keystone_client()

        resp_dict = {"stack": {
            "id": "1",
            "stack_name": "teststack",
            "stack_status": 'CREATE_COMPLETE',
            "creation_time": "2012-10-25T01:58:47Z",
            "outputs": [
                {
                    "output_value": "value1",
                    "output_key": "output1",
                    "description": "test output 1",
                },
                {
                    "output_value": ["output", "value", "2"],
                    "output_key": "output2",
                    "description": "test output 2",
                },
                {
                    "output_value": u"test\u2665",
                    "output_key": "output_uni",
                    "description": "test output unicode",
                },
            ],
            "creation_time": "2012-10-25T01:58:47Z"
        }}

        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))

        http.HTTPClient.json_request(
            'GET', '/stacks/teststack/1').AndReturn((resp, resp_dict))

        self.m.ReplayAll()

    def test_output_list(self):
        self._output_fake_response()
        list_text = self.shell('output-list teststack/1')
        for r in ['output1', 'output2', 'output_uni']:
            self.assertRegexpMatches(list_text, r)

    def test_output_show(self):
        self._output_fake_response()
        list_text = self.shell('output-show teststack/1 output1')
        self.assertRegexpMatches(list_text, 'value1')

    def test_output_show_unicode(self):
        self._output_fake_response()
        list_text = self.shell('output-show teststack/1 output_uni')
        self.assertRegexpMatches(list_text, u'test\u2665')

    def test_template_show_cfn(self):
        self._script_keystone_client()
        template_data = open(os.path.join(TEST_VAR_DIR,
                                          'minimal.template')).read()
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            template_data)
        resp_dict = jsonutils.loads(template_data)
        http.HTTPClient.json_request(
            'GET', '/stacks/teststack/template').AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        show_text = self.shell('template-show teststack')
        required = [
            '{',
            '  "AWSTemplateFormatVersion": "2010-09-09"',
            '  "Outputs": {}',
            '  "Resources": {}',
            '  "Parameters": {}',
            '}'
        ]
        for r in required:
            self.assertRegexpMatches(show_text, r)

    def test_template_show_cfn_unicode(self):
        self._script_keystone_client()
        resp_dict = {"AWSTemplateFormatVersion": "2010-09-09",
                     "Description": u"test\u2665",
                     "Outputs": {},
                     "Resources": {},
                     "Parameters": {}}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        http.HTTPClient.json_request(
            'GET', '/stacks/teststack/template').AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        show_text = self.shell('template-show teststack')
        required = [
            '{',
            '  "AWSTemplateFormatVersion": "2010-09-09"',
            '  "Outputs": {}',
            '  "Parameters": {}',
            u'  "Description": "test\u2665"',
            '  "Resources": {}',
            '}'
        ]
        for r in required:
            self.assertRegexpMatches(show_text, r)

    def test_template_show_hot(self):
        self._script_keystone_client()
        resp_dict = {"heat_template_version": "2013-05-23",
                     "parameters": {},
                     "resources": {},
                     "outputs": {}}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        http.HTTPClient.json_request(
            'GET', '/stacks/teststack/template').AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        show_text = self.shell('template-show teststack')
        required = [
            "heat_template_version: '2013-05-23'",
            "outputs: {}",
            "parameters: {}",
            "resources: {}"
        ]
        for r in required:
            self.assertRegexpMatches(show_text, r)

    def test_stack_preview(self):
        self._script_keystone_client()
        resp_dict = {"stack": {
            "id": "1",
            "stack_name": "teststack",
            "stack_status": 'CREATE_COMPLETE',
            "resources": {'1': {'name': 'r1'}},
            "creation_time": "2012-10-25T01:58:47Z",
        }}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            jsonutils.dumps(resp_dict))
        http.HTTPClient.json_request(
            'POST', '/stacks/preview', data=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        preview_text = self.shell(
            'stack-preview teststack '
            '--template-file=%s '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack',
            '1',
            'resources'
        ]

        for r in required:
            self.assertRegexpMatches(preview_text, r)

    def test_stack_create(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        http.HTTPClient.json_request(
            'POST', '/stacks', data=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        create_text = self.shell(
            'stack-create teststack '
            '--template-file=%s '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]

        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_stack_create_timeout(self):
        self._script_keystone_client()
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        template_data = open(template_file).read()
        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        expected_data = {
            'files': {},
            'disable_rollback': True,
            'parameters': {'DBUsername': 'wp',
                           'KeyName': 'heat_key',
                           'LinuxDistribution': 'F17"',
                           '"InstanceType': 'm1.large',
                           'DBPassword': 'verybadpassword'},
            'stack_name': 'teststack',
            'environment': {},
            'template': jsonutils.loads(template_data),
            'timeout_mins': 123}
        http.HTTPClient.json_request(
            'POST', '/stacks', data=expected_data,
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        create_text = self.shell(
            'stack-create teststack '
            '--template-file=%s '
            '--timeout=123 '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]

        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_stack_update_timeout(self):
        self._script_keystone_client()
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        template_data = open(template_file).read()
        resp = fakes.FakeHTTPResponse(
            202,
            'Accepted',
            {},
            'The request is accepted for processing.')

        expected_data = {
            'files': {},
            'environment': {},
            'template': jsonutils.loads(template_data),
            'parameters': {'DBUsername': 'wp',
                           'KeyName': 'heat_key',
                           'LinuxDistribution': 'F17"',
                           '"InstanceType': 'm1.large',
                           'DBPassword': 'verybadpassword'},
            'timeout_mins': 123,
            'disable_rollback': True}
        http.HTTPClient.json_request(
            'PUT', '/stacks/teststack2/2',
            data=expected_data,
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        update_text = self.shell(
            'stack-update teststack2/2 '
            '--template-file=%s '
            '--timeout 123 '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack2',
            '1'
        ]
        for r in required:
            self.assertRegexpMatches(update_text, r)

    def test_stack_create_url(self):

        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        self.m.StubOutWithMock(request, 'urlopen')
        request.urlopen('http://no.where/minimal.template').AndReturn(
            six.StringIO('{"AWSTemplateFormatVersion" : "2010-09-09"}'))

        expected_data = {
            'files': {},
            'disable_rollback': True,
            'stack_name': 'teststack',
            'environment': {},
            'template': {"AWSTemplateFormatVersion": "2010-09-09"},
            'parameters': {'DBUsername': 'wp',
                           'KeyName': 'heat_key',
                           'LinuxDistribution': 'F17"',
                           '"InstanceType': 'm1.large',
                           'DBPassword': 'verybadpassword'}}

        http.HTTPClient.json_request(
            'POST', '/stacks', data=expected_data,
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        create_text = self.shell(
            'stack-create teststack '
            '--template-url=http://no.where/minimal.template '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"')

        required = [
            'stack_name',
            'id',
            'teststack2',
            '2'
        ]
        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_stack_create_object(self):

        self._script_keystone_client()
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        template_data = open(template_file).read()
        http.HTTPClient.raw_request(
            'GET',
            'http://no.where/container/minimal.template',
        ).AndReturn(template_data)

        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        http.HTTPClient.json_request(
            'POST', '/stacks', data=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))

        fakes.script_heat_list()

        self.m.ReplayAll()

        create_text = self.shell(
            'stack-create teststack2 '
            '--template-object=http://no.where/container/minimal.template '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"')

        required = [
            'stack_name',
            'id',
            'teststack2',
            '2'
        ]
        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_stack_adopt(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack/1'},
            None)
        http.HTTPClient.json_request(
            'POST', '/stacks', data=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        adopt_data_file = os.path.join(TEST_VAR_DIR, 'adopt_stack_data.json')
        adopt_text = self.shell(
            'stack-adopt teststack '
            '--template-file=%s '
            '--adopt-file=%s '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % (template_file, adopt_data_file))

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]

        for r in required:
            self.assertRegexpMatches(adopt_text, r)

    def test_stack_adopt_without_data(self):
        failed_msg = 'Need to specify --adopt-file'
        self._script_keystone_client()
        self.m.ReplayAll()
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        self.shell_error(
            'stack-adopt teststack '
            '--template-file=%s ' % template_file, failed_msg)

    def test_stack_update(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            202,
            'Accepted',
            {},
            'The request is accepted for processing.')
        http.HTTPClient.json_request(
            'PUT', '/stacks/teststack2/2',
            data=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        update_text = self.shell(
            'stack-update teststack2/2 '
            '--template-file=%s '
            '--enable-rollback '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack2',
            '1'
        ]
        for r in required:
            self.assertRegexpMatches(update_text, r)

    def test_stack_delete(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            204,
            'No Content',
            {},
            None)
        http.HTTPClient.raw_request(
            'DELETE', '/stacks/teststack2/2',
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        delete_text = self.shell('stack-delete teststack2/2')

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]
        for r in required:
            self.assertRegexpMatches(delete_text, r)

    def test_stack_delete_multiple(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            204,
            'No Content',
            {},
            None)
        http.HTTPClient.raw_request(
            'DELETE', '/stacks/teststack1/1',
        ).AndReturn((resp, None))
        http.HTTPClient.raw_request(
            'DELETE', '/stacks/teststack2/2',
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        delete_text = self.shell('stack-delete teststack1/1 teststack2/2')

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]
        for r in required:
            self.assertRegexpMatches(delete_text, r)

    def test_build_info(self):
        self._script_keystone_client()
        resp_dict = {
            'build_info': {
                'api': {'revision': 'api_revision'},
                'engine': {'revision': 'engine_revision'}
            }
        }
        resp_string = jsonutils.dumps(resp_dict)
        headers = {'content-type': 'application/json'}
        http_resp = fakes.FakeHTTPResponse(200, 'OK', headers, resp_string)
        response = (http_resp, resp_dict)
        http.HTTPClient.json_request('GET', '/build_info').AndReturn(response)

        self.m.ReplayAll()

        build_info_text = self.shell('build-info')

        required = [
            'api',
            'engine',
            'revision',
            'api_revision',
            'engine_revision',
        ]
        for r in required:
            self.assertRegexpMatches(build_info_text, r)


class ShellTestEvents(ShellBase):
    def setUp(self):
        super(ShellTestEvents, self).setUp()
        self._set_fake_env()

    # Patch os.environ to avoid required auth info.
    def _set_fake_env(self):
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)

    def _script_keystone_client(self):
        fakes.script_keystone_client()

    scenarios = [
        ('integer_id', dict(
            event_id_one='24',
            event_id_two='42')),
        ('uuid_id', dict(
            event_id_one='3d68809e-c4aa-4dc9-a008-933823d2e44f',
            event_id_two='43b68bae-ed5d-4aed-a99f-0b3d39c2418a'))]

    def test_event_list(self):
        self._script_keystone_client()
        resp_dict = {"events": [
                     {"event_time": "2013-12-05T14:14:30Z",
                      "id": self.event_id_one,
                      "links": [{"href": "http://heat.example.com:8004/foo",
                                 "rel": "self"},
                                {"href": "http://heat.example.com:8004/foo2",
                                 "rel": "resource"},
                                {"href": "http://heat.example.com:8004/foo3",
                                 "rel": "stack"}],
                      "logical_resource_id": "aResource",
                      "physical_resource_id": None,
                      "resource_name": "aResource",
                      "resource_status": "CREATE_IN_PROGRESS",
                      "resource_status_reason": "state changed"},
                     {"event_time": "2013-12-05T14:14:30Z",
                      "id": self.event_id_two,
                      "links": [{"href": "http://heat.example.com:8004/foo",
                                 "rel": "self"},
                                {"href": "http://heat.example.com:8004/foo2",
                                 "rel": "resource"},
                                {"href": "http://heat.example.com:8004/foo3",
                                 "rel": "stack"}],
                      "logical_resource_id": "aResource",
                      "physical_resource_id":
                      "bce15ec4-8919-4a02-8a90-680960fb3731",
                      "resource_name": "aResource",
                      "resource_status": "CREATE_COMPLETE",
                      "resource_status_reason": "state changed"}]}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        stack_id = 'teststack/1'
        resource_name = 'testresource/1'
        http.HTTPClient.json_request(
            'GET', '/stacks/%s/resources/%s/events' % (
                parse.quote(stack_id, ''),
                parse.quote(strutils.safe_encode(
                    resource_name), ''))).AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        event_list_text = self.shell('event-list {0} --resource {1}'.format(
                                     stack_id, resource_name))

        required = [
            'resource_name',
            'id',
            'resource_status_reason',
            'resource_status',
            'event_time',
            'aResource',
            self.event_id_one,
            self.event_id_two,
            'state changed',
            'CREATE_IN_PROGRESS',
            'CREATE_COMPLETE',
            '2013-12-05T14:14:30Z',
            '2013-12-05T14:14:30Z',
        ]
        for r in required:
            self.assertRegexpMatches(event_list_text, r)

    def test_event_show(self):
        self._script_keystone_client()
        resp_dict = {"event":
                     {"event_time": "2013-12-05T14:14:30Z",
                      "id": self.event_id_one,
                      "links": [{"href": "http://heat.example.com:8004/foo",
                                 "rel": "self"},
                                {"href": "http://heat.example.com:8004/foo2",
                                 "rel": "resource"},
                                {"href": "http://heat.example.com:8004/foo3",
                                 "rel": "stack"}],
                      "logical_resource_id": "aResource",
                      "physical_resource_id": None,
                      "resource_name": "aResource",
                      "resource_properties": {"admin_user": "im_powerful",
                                              "availability_zone": "nova"},
                      "resource_status": "CREATE_IN_PROGRESS",
                      "resource_status_reason": "state changed",
                      "resource_type": "OS::Nova::Server"
                      }}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        stack_id = 'teststack/1'
        resource_name = 'testresource/1'
        http.HTTPClient.json_request(
            'GET', '/stacks/%s/resources/%s/events/%s' %
            (
                parse.quote(stack_id, ''),
                parse.quote(strutils.safe_encode(
                    resource_name), ''),
                parse.quote(self.event_id_one, '')
            )).AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        event_list_text = self.shell('event-show {0} {1} {2}'.format(
                                     stack_id, resource_name,
                                     self.event_id_one))

        required = [
            'Property',
            'Value',
            'event_time',
            '2013-12-05T14:14:30Z',
            'id',
            self.event_id_one,
            'links',
            'http://heat.example.com:8004/foo[0-9]',
            'logical_resource_id',
            'physical_resource_id',
            'resource_name',
            'aResource',
            'resource_properties',
            'admin_user',
            'availability_zone',
            'resource_status',
            'CREATE_IN_PROGRESS',
            'resource_status_reason',
            'state changed',
            'resource_type',
            'OS::Nova::Server',
        ]
        for r in required:
            self.assertRegexpMatches(event_list_text, r)


class ShellTestResources(ShellBase):
    def setUp(self):
        super(ShellTestResources, self).setUp()
        self._set_fake_env()

    # Patch os.environ to avoid required auth info.
    def _set_fake_env(self):
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)

    def _script_keystone_client(self):
        fakes.script_keystone_client()

    def _test_resource_list(self, with_resource_name):
        self._script_keystone_client()
        resp_dict = {"resources": [
                     {"links": [{"href": "http://heat.example.com:8004/foo",
                                 "rel": "self"},
                                {"href": "http://heat.example.com:8004/foo2",
                                 "rel": "resource"}],
                      "logical_resource_id": "aLogicalResource",
                      "physical_resource_id":
                      "43b68bae-ed5d-4aed-a99f-0b3d39c2418a",
                      "resource_status": "CREATE_COMPLETE",
                      "resource_status_reason": "state changed",
                      "resource_type": "OS::Nova::Server",
                      "updated_time": "2014-01-06T16:14:26Z"}]}
        if with_resource_name:
            resp_dict["resources"][0]["resource_name"] = "aResource"
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        stack_id = 'teststack/1'
        http.HTTPClient.json_request(
            'GET', '/stacks/%s/resources' % (
                stack_id)).AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        resource_list_text = self.shell('resource-list {0}'.format(stack_id))

        required = [
            'resource_type',
            'resource_status',
            'updated_time',
            'OS::Nova::Server',
            'CREATE_COMPLETE',
            '2014-01-06T16:14:26Z'
        ]
        if with_resource_name:
            required.append('resource_name')
            required.append('aResource')
        else:
            required.append('logical_resource_id')
            required.append("aLogicalResource")

        for r in required:
            self.assertRegexpMatches(resource_list_text, r)

    def test_resource_list(self):
        self._test_resource_list(True)

    def test_resource_list_no_resource_name(self):
        self._test_resource_list(False)

    def test_resource_list_empty(self):
        self._script_keystone_client()
        resp_dict = {"resources": []}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        stack_id = 'teststack/1'
        http.HTTPClient.json_request(
            'GET', '/stacks/%s/resources' % (
                stack_id)).AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        resource_list_text = self.shell('resource-list {0}'.format(stack_id))

        self.assertEqual('''\
+---------------+---------------+-----------------+--------------+
| resource_name | resource_type | resource_status | updated_time |
+---------------+---------------+-----------------+--------------+
+---------------+---------------+-----------------+--------------+
''', resource_list_text)

    def test_resource_show(self):
        self._script_keystone_client()
        resp_dict = {"resource":
                     {"description": "",
                      "links": [{"href": "http://heat.example.com:8004/foo",
                                 "rel": "self"},
                                {"href": "http://heat.example.com:8004/foo2",
                                 "rel": "resource"}],
                      "logical_resource_id": "aResource",
                      "physical_resource_id":
                      "43b68bae-ed5d-4aed-a99f-0b3d39c2418a",
                      "required_by": [],
                      "resource_name": "aResource",
                      "resource_status": "CREATE_COMPLETE",
                      "resource_status_reason": "state changed",
                      "resource_type": "OS::Nova::Server",
                      "updated_time": "2014-01-06T16:14:26Z"}}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            jsonutils.dumps(resp_dict))
        stack_id = 'teststack/1'
        resource_name = 'aResource'
        http.HTTPClient.json_request(
            'GET', '/stacks/%s/resources/%s' %
            (
                parse.quote(stack_id, ''),
                parse.quote(strutils.safe_encode(
                    resource_name), '')
            )).AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        resource_show_text = self.shell('resource-show {0} {1}'.format(
                                        stack_id, resource_name))

        required = [
            'description',
            'links',
            'http://heat.example.com:8004/foo[0-9]',
            'logical_resource_id',
            'aResource',
            'physical_resource_id',
            '43b68bae-ed5d-4aed-a99f-0b3d39c2418a',
            'required_by',
            'resource_name',
            'aResource',
            'resource_status',
            'CREATE_COMPLETE',
            'resource_status_reason',
            'state changed',
            'resource_type',
            'OS::Nova::Server',
            'updated_time',
            '2014-01-06T16:14:26Z',
        ]
        for r in required:
            self.assertRegexpMatches(resource_show_text, r)

    def test_resource_signal(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {},
            '')
        stack_id = 'teststack/1'
        resource_name = 'aResource'
        http.HTTPClient.json_request(
            'POST', '/stacks/%s/resources/%s/signal' %
            (
                parse.quote(stack_id, ''),
                parse.quote(strutils.safe_encode(
                    resource_name), '')
            ),
            data={'message': 'Content'}).AndReturn((resp, ''))

        self.m.ReplayAll()

        text = self.shell(
            'resource-signal {0} {1} -D {{"message":"Content"}}'.format(
                stack_id, resource_name))
        self.assertEqual("", text)

    def test_resource_signal_no_data(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {},
            '')
        stack_id = 'teststack/1'
        resource_name = 'aResource'
        http.HTTPClient.json_request(
            'POST', '/stacks/%s/resources/%s/signal' %
            (
                parse.quote(stack_id, ''),
                parse.quote(strutils.safe_encode(
                    resource_name), '')
            ), data=None).AndReturn((resp, ''))

        self.m.ReplayAll()

        text = self.shell(
            'resource-signal {0} {1}'.format(stack_id, resource_name))
        self.assertEqual("", text)

    def test_resource_signal_no_json(self):
        self._script_keystone_client()
        stack_id = 'teststack/1'
        resource_name = 'aResource'

        self.m.ReplayAll()

        error = self.assertRaises(
            exc.CommandError, self.shell,
            'resource-signal {0} {1} -D [2'.format(
                stack_id, resource_name))
        self.assertIn('Data should be in JSON format', str(error))

    def test_resource_signal_no_dict(self):
        self._script_keystone_client()
        stack_id = 'teststack/1'
        resource_name = 'aResource'

        self.m.ReplayAll()

        error = self.assertRaises(
            exc.CommandError, self.shell,
            'resource-signal {0} {1} -D "message"'.format(
                stack_id, resource_name))
        self.assertEqual('Data should be a JSON dict', str(error))

    def test_resource_signal_both_data(self):
        self._script_keystone_client()
        stack_id = 'teststack/1'
        resource_name = 'aResource'

        self.m.ReplayAll()

        error = self.assertRaises(
            exc.CommandError, self.shell,
            'resource-signal {0} {1} -D "message" -f foo'.format(
                stack_id, resource_name))
        self.assertEqual('Can only specify one of data and data-file',
                         str(error))

    def test_resource_signal_data_file(self):
        self._script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {},
            '')
        stack_id = 'teststack/1'
        resource_name = 'aResource'
        http.HTTPClient.json_request(
            'POST', '/stacks/%s/resources/%s/signal' %
            (
                parse.quote(stack_id, ''),
                parse.quote(strutils.safe_encode(
                    resource_name), '')
            ),
            data={'message': 'Content'}).AndReturn((resp, ''))

        self.m.ReplayAll()

        with tempfile.NamedTemporaryFile() as data_file:
            data_file.write(b'{"message":"Content"}')
            data_file.flush()
            text = self.shell(
                'resource-signal {0} {1} -f {2}'.format(
                    stack_id, resource_name, data_file.name))
            self.assertEqual("", text)


class ShellTestBuildInfo(ShellBase):
    def setUp(self):
        super(ShellTestBuildInfo, self).setUp()
        self._set_fake_env()

    def _set_fake_env(self):
        '''Patch os.environ to avoid required auth info.'''

        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)

    def test_build_info(self):
        fakes.script_keystone_client()
        resp_dict = {
            'build_info': {
                'api': {'revision': 'api_revision'},
                'engine': {'revision': 'engine_revision'}
            }
        }
        resp_string = jsonutils.dumps(resp_dict)
        headers = {'content-type': 'application/json'}
        http_resp = fakes.FakeHTTPResponse(200, 'OK', headers, resp_string)
        response = (http_resp, resp_dict)
        http.HTTPClient.json_request('GET', '/build_info').AndReturn(response)

        self.m.ReplayAll()

        build_info_text = self.shell('build-info')

        required = [
            'api',
            'engine',
            'revision',
            'api_revision',
            'engine_revision',
        ]
        for r in required:
            self.assertRegexpMatches(build_info_text, r)


class ShellTestToken(ShellTestUserPass):

    # Rerun all ShellTestUserPass test with token auth
    def setUp(self):
        self.token = 'a_token'
        super(ShellTestToken, self).setUp()

    def _set_fake_env(self):
        fake_env = {
            'OS_AUTH_TOKEN': self.token,
            'OS_TENANT_ID': 'tenant_id',
            'OS_AUTH_URL': 'http://no.where',
            # Note we also set username/password, because create/update
            # pass them even if we have a token to support storing credentials
            # Hopefully at some point we can remove this and move to only
            # storing trust id's in heat-engine instead..
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password'
        }
        self.set_fake_env(fake_env)

    def _script_keystone_client(self):
        fakes.script_keystone_client(token=self.token)


class ShellTestStandaloneToken(ShellTestUserPass):

    # Rerun all ShellTestUserPass test in standalone mode, where we
    # specify --os-no-client-auth, a token and Heat endpoint
    def setUp(self):
        self.token = 'a_token'
        super(ShellTestStandaloneToken, self).setUp()

    def _set_fake_env(self):
        fake_env = {
            'OS_AUTH_TOKEN': self.token,
            'OS_NO_CLIENT_AUTH': 'True',
            'HEAT_URL': 'http://no.where',
            # Note we also set username/password, because create/update
            # pass them even if we have a token to support storing credentials
            # Hopefully at some point we can remove this and move to only
            # storing trust id's in heat-engine instead..
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password'
        }
        self.set_fake_env(fake_env)

    def _script_keystone_client(self):
        # The StanaloneMode shouldn't need any keystoneclient stubbing
        pass

    def test_bad_template_file(self):
        failed_msg = 'Error parsing template '

        with tempfile.NamedTemporaryFile() as bad_json_file:
            bad_json_file.write(b"{foo:}")
            bad_json_file.flush()
            self.shell_error("stack-create ts -f %s" % bad_json_file.name,
                             failed_msg)

        with tempfile.NamedTemporaryFile() as bad_json_file:
            bad_json_file.write(b'{"foo": None}')
            bad_json_file.flush()
            self.shell_error("stack-create ts -f %s" % bad_json_file.name,
                             failed_msg)
