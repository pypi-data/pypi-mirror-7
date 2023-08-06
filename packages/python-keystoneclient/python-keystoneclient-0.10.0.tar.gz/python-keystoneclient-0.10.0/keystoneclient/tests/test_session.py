# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import uuid

import httpretty
import mock
from oslo.config import cfg
import requests
import six
from testtools import matchers

from keystoneclient import adapter
from keystoneclient.auth import base
from keystoneclient import exceptions
from keystoneclient.openstack.common.fixture import config
from keystoneclient.openstack.common import jsonutils
from keystoneclient import session as client_session
from keystoneclient.tests import utils


class SessionTests(utils.TestCase):

    TEST_URL = 'http://127.0.0.1:5000/'

    @httpretty.activate
    def test_get(self):
        session = client_session.Session()
        self.stub_url(httpretty.GET, body='response')
        resp = session.get(self.TEST_URL)

        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)

    @httpretty.activate
    def test_post(self):
        session = client_session.Session()
        self.stub_url(httpretty.POST, body='response')
        resp = session.post(self.TEST_URL, json={'hello': 'world'})

        self.assertEqual(httpretty.POST, httpretty.last_request().method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs(json={'hello': 'world'})

    @httpretty.activate
    def test_head(self):
        session = client_session.Session()
        self.stub_url(httpretty.HEAD)
        resp = session.head(self.TEST_URL)

        self.assertEqual(httpretty.HEAD, httpretty.last_request().method)
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs('')

    @httpretty.activate
    def test_put(self):
        session = client_session.Session()
        self.stub_url(httpretty.PUT, body='response')
        resp = session.put(self.TEST_URL, json={'hello': 'world'})

        self.assertEqual(httpretty.PUT, httpretty.last_request().method)
        self.assertEqual(resp.text, 'response')
        self.assertTrue(resp.ok)
        self.assertRequestBodyIs(json={'hello': 'world'})

    @httpretty.activate
    def test_delete(self):
        session = client_session.Session()
        self.stub_url(httpretty.DELETE, body='response')
        resp = session.delete(self.TEST_URL)

        self.assertEqual(httpretty.DELETE, httpretty.last_request().method)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.text, 'response')

    @httpretty.activate
    def test_patch(self):
        session = client_session.Session()
        self.stub_url(httpretty.PATCH, body='response')
        resp = session.patch(self.TEST_URL, json={'hello': 'world'})

        self.assertEqual(httpretty.PATCH, httpretty.last_request().method)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.text, 'response')
        self.assertRequestBodyIs(json={'hello': 'world'})

    @httpretty.activate
    def test_user_agent(self):
        session = client_session.Session(user_agent='test-agent')
        self.stub_url(httpretty.GET, body='response')
        resp = session.get(self.TEST_URL)

        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'test-agent')

        resp = session.get(self.TEST_URL, headers={'User-Agent': 'new-agent'})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = session.get(self.TEST_URL, headers={'User-Agent': 'new-agent'},
                           user_agent='overrides-agent')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

    @httpretty.activate
    def test_http_session_opts(self):
        session = client_session.Session(cert='cert.pem', timeout=5,
                                         verify='certs')

        FAKE_RESP = utils.TestResponse({'status_code': 200, 'text': 'resp'})
        RESP = mock.Mock(return_value=FAKE_RESP)

        with mock.patch.object(session.session, 'request', RESP) as mocked:
            session.post(self.TEST_URL, data='value')

            mock_args, mock_kwargs = mocked.call_args

            self.assertEqual(mock_args[0], 'POST')
            self.assertEqual(mock_args[1], self.TEST_URL)
            self.assertEqual(mock_kwargs['data'], 'value')
            self.assertEqual(mock_kwargs['cert'], 'cert.pem')
            self.assertEqual(mock_kwargs['verify'], 'certs')
            self.assertEqual(mock_kwargs['timeout'], 5)

    @httpretty.activate
    def test_not_found(self):
        session = client_session.Session()
        self.stub_url(httpretty.GET, status=404)
        self.assertRaises(exceptions.NotFound, session.get, self.TEST_URL)

    @httpretty.activate
    def test_server_error(self):
        session = client_session.Session()
        self.stub_url(httpretty.GET, status=500)
        self.assertRaises(exceptions.InternalServerError,
                          session.get, self.TEST_URL)

    @httpretty.activate
    def test_session_debug_output(self):
        session = client_session.Session(verify=False)
        headers = {'HEADERA': 'HEADERVALB'}
        body = 'BODYRESPONSE'
        data = 'BODYDATA'
        self.stub_url(httpretty.POST, body=body)
        session.post(self.TEST_URL, headers=headers, data=data)

        self.assertIn('curl', self.logger.output)
        self.assertIn('POST', self.logger.output)
        self.assertIn('--insecure', self.logger.output)
        self.assertIn(body, self.logger.output)
        self.assertIn("'%s'" % data, self.logger.output)

        for k, v in six.iteritems(headers):
            self.assertIn(k, self.logger.output)
            self.assertIn(v, self.logger.output)


class RedirectTests(utils.TestCase):

    REDIRECT_CHAIN = ['http://myhost:3445/',
                      'http://anotherhost:6555/',
                      'http://thirdhost/',
                      'http://finaldestination:55/']

    DEFAULT_REDIRECT_BODY = 'Redirect'
    DEFAULT_RESP_BODY = 'Found'

    def setup_redirects(self, method=httpretty.GET, status=305,
                        redirect_kwargs={}, final_kwargs={}):
        redirect_kwargs.setdefault('body', self.DEFAULT_REDIRECT_BODY)

        for s, d in zip(self.REDIRECT_CHAIN, self.REDIRECT_CHAIN[1:]):
            httpretty.register_uri(method, s, status=status, location=d,
                                   **redirect_kwargs)

        final_kwargs.setdefault('status', 200)
        final_kwargs.setdefault('body', self.DEFAULT_RESP_BODY)
        httpretty.register_uri(method, self.REDIRECT_CHAIN[-1], **final_kwargs)

    def assertResponse(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, self.DEFAULT_RESP_BODY)

    @httpretty.activate
    def test_basic_get(self):
        session = client_session.Session()
        self.setup_redirects()
        resp = session.get(self.REDIRECT_CHAIN[-2])
        self.assertResponse(resp)

    @httpretty.activate
    def test_basic_post_keeps_correct_method(self):
        session = client_session.Session()
        self.setup_redirects(method=httpretty.POST, status=301)
        resp = session.post(self.REDIRECT_CHAIN[-2])
        self.assertResponse(resp)

    @httpretty.activate
    def test_redirect_forever(self):
        session = client_session.Session(redirect=True)
        self.setup_redirects()
        resp = session.get(self.REDIRECT_CHAIN[0])
        self.assertResponse(resp)
        self.assertTrue(len(resp.history), len(self.REDIRECT_CHAIN))

    @httpretty.activate
    def test_no_redirect(self):
        session = client_session.Session(redirect=False)
        self.setup_redirects()
        resp = session.get(self.REDIRECT_CHAIN[0])
        self.assertEqual(resp.status_code, 305)
        self.assertEqual(resp.url, self.REDIRECT_CHAIN[0])

    @httpretty.activate
    def test_redirect_limit(self):
        self.setup_redirects()
        for i in (1, 2):
            session = client_session.Session(redirect=i)
            resp = session.get(self.REDIRECT_CHAIN[0])
            self.assertEqual(resp.status_code, 305)
            self.assertEqual(resp.url, self.REDIRECT_CHAIN[i])
            self.assertEqual(resp.text, self.DEFAULT_REDIRECT_BODY)

    @httpretty.activate
    def test_history_matches_requests(self):
        self.setup_redirects(status=301)
        session = client_session.Session(redirect=True)
        req_resp = requests.get(self.REDIRECT_CHAIN[0],
                                allow_redirects=True)

        ses_resp = session.get(self.REDIRECT_CHAIN[0])

        self.assertEqual(len(req_resp.history), len(ses_resp.history))

        for r, s in zip(req_resp.history, ses_resp.history):
            self.assertEqual(r.url, s.url)
            self.assertEqual(r.status_code, s.status_code)


class ConstructSessionFromArgsTests(utils.TestCase):

    KEY = 'keyfile'
    CERT = 'certfile'
    CACERT = 'cacert-path'

    def _s(self, k=None, **kwargs):
        k = k or kwargs
        return client_session.Session.construct(k)

    def test_verify(self):
        self.assertFalse(self._s(insecure=True).verify)
        self.assertTrue(self._s(verify=True, insecure=True).verify)
        self.assertFalse(self._s(verify=False, insecure=True).verify)
        self.assertEqual(self._s(cacert=self.CACERT).verify, self.CACERT)

    def test_cert(self):
        tup = (self.CERT, self.KEY)
        self.assertEqual(self._s(cert=tup).cert, tup)
        self.assertEqual(self._s(cert=self.CERT, key=self.KEY).cert, tup)
        self.assertIsNone(self._s(key=self.KEY).cert)

    def test_pass_through(self):
        value = 42  # only a number because timeout needs to be
        for key in ['timeout', 'session', 'original_ip', 'user_agent']:
            args = {key: value}
            self.assertEqual(getattr(self._s(args), key), value)
            self.assertNotIn(key, args)


class AuthPlugin(base.BaseAuthPlugin):
    """Very simple debug authentication plugin.

    Takes Parameters such that it can throw exceptions at the right times.
    """

    TEST_TOKEN = 'aToken'

    SERVICE_URLS = {
        'identity': {'public': 'http://identity-public:1111/v2.0',
                     'admin': 'http://identity-admin:1111/v2.0'},
        'compute': {'public': 'http://compute-public:2222/v1.0',
                    'admin': 'http://compute-admin:2222/v1.0'},
        'image': {'public': 'http://image-public:3333/v2.0',
                  'admin': 'http://image-admin:3333/v2.0'}
    }

    def __init__(self, token=TEST_TOKEN, invalidate=True):
        self.token = token
        self._invalidate = invalidate

    def get_token(self, session):
        return self.token

    def get_endpoint(self, session, service_type=None, interface=None,
                     **kwargs):
        try:
            return self.SERVICE_URLS[service_type][interface]
        except (KeyError, AttributeError):
            return None

    def invalidate(self):
        return self._invalidate


class CalledAuthPlugin(base.BaseAuthPlugin):

    ENDPOINT = 'http://fakeendpoint/'

    def __init__(self, invalidate=True):
        self.get_token_called = False
        self.get_endpoint_called = False
        self.endpoint_arguments = {}
        self.invalidate_called = False
        self._invalidate = invalidate

    def get_token(self, session):
        self.get_token_called = True
        return 'aToken'

    def get_endpoint(self, session, **kwargs):
        self.get_endpoint_called = True
        self.endpoint_arguments = kwargs
        return self.ENDPOINT

    def invalidate(self):
        self.invalidate_called = True
        return self._invalidate


class SessionAuthTests(utils.TestCase):

    TEST_URL = 'http://127.0.0.1:5000/'
    TEST_JSON = {'hello': 'world'}

    def stub_service_url(self, service_type, interface, path,
                         method=httpretty.GET, **kwargs):
        base_url = AuthPlugin.SERVICE_URLS[service_type][interface]
        uri = "%s/%s" % (base_url.rstrip('/'), path.lstrip('/'))

        httpretty.register_uri(method, uri, **kwargs)

    @httpretty.activate
    def test_auth_plugin_default_with_plugin(self):
        self.stub_url('GET', base_url=self.TEST_URL, json=self.TEST_JSON)

        # if there is an auth_plugin then it should default to authenticated
        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        resp = sess.get(self.TEST_URL)
        self.assertDictEqual(resp.json(), self.TEST_JSON)

        self.assertRequestHeaderEqual('X-Auth-Token', AuthPlugin.TEST_TOKEN)

    @httpretty.activate
    def test_auth_plugin_disable(self):
        self.stub_url('GET', base_url=self.TEST_URL, json=self.TEST_JSON)

        auth = AuthPlugin()
        sess = client_session.Session(auth=auth)
        resp = sess.get(self.TEST_URL, authenticated=False)
        self.assertDictEqual(resp.json(), self.TEST_JSON)

        self.assertRequestHeaderEqual('X-Auth-Token', None)

    @httpretty.activate
    def test_service_type_urls(self):
        service_type = 'compute'
        interface = 'public'
        path = '/instances'
        status = 200
        body = 'SUCCESS'

        self.stub_service_url(service_type=service_type,
                              interface=interface,
                              path=path,
                              status=status,
                              body=body)

        sess = client_session.Session(auth=AuthPlugin())
        resp = sess.get(path,
                        endpoint_filter={'service_type': service_type,
                                         'interface': interface})

        self.assertEqual(httpretty.last_request().path, '/v1.0/instances')
        self.assertEqual(resp.text, body)
        self.assertEqual(resp.status_code, status)

    def test_service_url_raises_if_no_auth_plugin(self):
        sess = client_session.Session()
        self.assertRaises(exceptions.MissingAuthPlugin,
                          sess.get, '/path',
                          endpoint_filter={'service_type': 'compute',
                                           'interface': 'public'})

    def test_service_url_raises_if_no_url_returned(self):
        sess = client_session.Session(auth=AuthPlugin())
        self.assertRaises(exceptions.EndpointNotFound,
                          sess.get, '/path',
                          endpoint_filter={'service_type': 'unknown',
                                           'interface': 'public'})

    @httpretty.activate
    def test_raises_exc_only_when_asked(self):
        # A request that returns a HTTP error should by default raise an
        # exception by default, if you specify raise_exc=False then it will not

        self.stub_url(httpretty.GET, status=401)

        sess = client_session.Session()
        self.assertRaises(exceptions.Unauthorized, sess.get, self.TEST_URL)

        resp = sess.get(self.TEST_URL, raise_exc=False)
        self.assertEqual(401, resp.status_code)

    @httpretty.activate
    def test_passed_auth_plugin(self):
        passed = CalledAuthPlugin()
        sess = client_session.Session()

        httpretty.register_uri(httpretty.GET,
                               CalledAuthPlugin.ENDPOINT + 'path',
                               status=200)
        endpoint_filter = {'service_type': 'identity'}

        # no plugin with authenticated won't work
        self.assertRaises(exceptions.MissingAuthPlugin, sess.get, 'path',
                          authenticated=True)

        # no plugin with an endpoint filter won't work
        self.assertRaises(exceptions.MissingAuthPlugin, sess.get, 'path',
                          authenticated=False, endpoint_filter=endpoint_filter)

        resp = sess.get('path', auth=passed, endpoint_filter=endpoint_filter)

        self.assertEqual(200, resp.status_code)
        self.assertTrue(passed.get_endpoint_called)
        self.assertTrue(passed.get_token_called)

    @httpretty.activate
    def test_passed_auth_plugin_overrides(self):
        fixed = CalledAuthPlugin()
        passed = CalledAuthPlugin()

        sess = client_session.Session(fixed)

        httpretty.register_uri(httpretty.GET,
                               CalledAuthPlugin.ENDPOINT + 'path',
                               status=200)

        resp = sess.get('path', auth=passed,
                        endpoint_filter={'service_type': 'identity'})

        self.assertEqual(200, resp.status_code)
        self.assertTrue(passed.get_endpoint_called)
        self.assertTrue(passed.get_token_called)
        self.assertFalse(fixed.get_endpoint_called)
        self.assertFalse(fixed.get_token_called)

    def test_requests_auth_plugin(self):
        sess = client_session.Session()

        requests_auth = object()

        FAKE_RESP = utils.TestResponse({'status_code': 200, 'text': 'resp'})
        RESP = mock.Mock(return_value=FAKE_RESP)

        with mock.patch.object(sess.session, 'request', RESP) as mocked:
            sess.get(self.TEST_URL, requests_auth=requests_auth)

            mocked.assert_called_once_with('GET', self.TEST_URL,
                                           headers=mock.ANY,
                                           allow_redirects=mock.ANY,
                                           auth=requests_auth,
                                           verify=mock.ANY)

    @httpretty.activate
    def test_reauth_called(self):
        auth = CalledAuthPlugin(invalidate=True)
        sess = client_session.Session(auth=auth)

        responses = [httpretty.Response(body='Failed', status=401),
                     httpretty.Response(body='Hello', status=200)]
        httpretty.register_uri(httpretty.GET, self.TEST_URL,
                               responses=responses)

        # allow_reauth=True is the default
        resp = sess.get(self.TEST_URL, authenticated=True)

        self.assertEqual(200, resp.status_code)
        self.assertEqual('Hello', resp.text)
        self.assertTrue(auth.invalidate_called)

    @httpretty.activate
    def test_reauth_not_called(self):
        auth = CalledAuthPlugin(invalidate=True)
        sess = client_session.Session(auth=auth)

        responses = [httpretty.Response(body='Failed', status=401),
                     httpretty.Response(body='Hello', status=200)]
        httpretty.register_uri(httpretty.GET, self.TEST_URL,
                               responses=responses)

        self.assertRaises(exceptions.Unauthorized, sess.get, self.TEST_URL,
                          authenticated=True, allow_reauth=False)
        self.assertFalse(auth.invalidate_called)


class AdapterTest(utils.TestCase):

    SERVICE_TYPE = uuid.uuid4().hex
    SERVICE_NAME = uuid.uuid4().hex
    INTERFACE = uuid.uuid4().hex
    REGION_NAME = uuid.uuid4().hex
    USER_AGENT = uuid.uuid4().hex

    TEST_URL = CalledAuthPlugin.ENDPOINT

    @httpretty.activate
    def test_setting_variables(self):
        response = uuid.uuid4().hex
        self.stub_url(httpretty.GET, body=response)

        auth = CalledAuthPlugin()
        sess = client_session.Session()
        adpt = adapter.Adapter(sess,
                               auth=auth,
                               service_type=self.SERVICE_TYPE,
                               service_name=self.SERVICE_NAME,
                               interface=self.INTERFACE,
                               region_name=self.REGION_NAME,
                               user_agent=self.USER_AGENT)

        resp = adpt.get('/')
        self.assertEqual(resp.text, response)

        self.assertEqual(self.SERVICE_TYPE,
                         auth.endpoint_arguments['service_type'])
        self.assertEqual(self.SERVICE_NAME,
                         auth.endpoint_arguments['service_name'])
        self.assertEqual(self.INTERFACE,
                         auth.endpoint_arguments['interface'])
        self.assertEqual(self.REGION_NAME,
                         auth.endpoint_arguments['region_name'])

        self.assertTrue(auth.get_token_called)
        self.assertRequestHeaderEqual('User-Agent', self.USER_AGENT)

    @httpretty.activate
    def test_legacy_binding(self):
        key = uuid.uuid4().hex
        val = uuid.uuid4().hex
        response = jsonutils.dumps({key: val})

        self.stub_url(httpretty.GET, body=response)

        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)
        adpt = adapter.LegacyJsonAdapter(sess,
                                         service_type=self.SERVICE_TYPE,
                                         user_agent=self.USER_AGENT)

        resp, body = adpt.get('/')
        self.assertEqual(self.SERVICE_TYPE,
                         auth.endpoint_arguments['service_type'])
        self.assertEqual(resp.text, response)
        self.assertEqual(val, body[key])

    @httpretty.activate
    def test_legacy_binding_non_json_resp(self):
        response = uuid.uuid4().hex
        self.stub_url(httpretty.GET, body=response, content_type='text/html')

        auth = CalledAuthPlugin()
        sess = client_session.Session(auth=auth)
        adpt = adapter.LegacyJsonAdapter(sess,
                                         service_type=self.SERVICE_TYPE,
                                         user_agent=self.USER_AGENT)

        resp, body = adpt.get('/')
        self.assertEqual(self.SERVICE_TYPE,
                         auth.endpoint_arguments['service_type'])
        self.assertEqual(resp.text, response)
        self.assertIsNone(body)

    def test_methods(self):
        sess = client_session.Session()
        adpt = adapter.Adapter(sess)
        url = 'http://url'

        for method in ['get', 'head', 'post', 'put', 'patch', 'delete']:
            with mock.patch.object(adpt, 'request') as m:
                getattr(adpt, method)(url)
                m.assert_called_once_with(url, method.upper())


class ConfLoadingTests(utils.TestCase):

    GROUP = 'sessiongroup'

    def setUp(self):
        super(ConfLoadingTests, self).setUp()

        self.conf_fixture = self.useFixture(config.Config())
        client_session.Session.register_conf_options(self.conf_fixture.conf,
                                                     self.GROUP)

    def config(self, **kwargs):
        kwargs['group'] = self.GROUP
        self.conf_fixture.config(**kwargs)

    def get_session(self, **kwargs):
        return client_session.Session.load_from_conf_options(
            self.conf_fixture.conf,
            self.GROUP,
            **kwargs)

    def test_insecure_timeout(self):
        self.config(insecure=True, timeout=5)
        s = self.get_session()

        self.assertFalse(s.verify)
        self.assertEqual(5, s.timeout)

    def test_client_certs(self):
        cert = '/path/to/certfile'
        key = '/path/to/keyfile'

        self.config(certfile=cert, keyfile=key)
        s = self.get_session()

        self.assertTrue(s.verify)
        self.assertEqual((cert, key), s.cert)

    def test_cacert(self):
        cafile = '/path/to/cacert'

        self.config(cafile=cafile)
        s = self.get_session()

        self.assertEqual(cafile, s.verify)

    def test_deprecated(self):
        def new_deprecated():
            return cfg.DeprecatedOpt(uuid.uuid4().hex, group=uuid.uuid4().hex)

        opt_names = ['cafile', 'certfile', 'keyfile', 'insecure', 'timeout']
        depr = dict([(n, [new_deprecated()]) for n in opt_names])
        opts = client_session.Session.get_conf_options(deprecated_opts=depr)

        self.assertThat(opt_names, matchers.HasLength(len(opts)))
        for opt in opts:
            self.assertIn(depr[opt.name][0], opt.deprecated_opts)


class CliLoadingTests(utils.TestCase):

    def setUp(self):
        super(CliLoadingTests, self).setUp()

        self.parser = argparse.ArgumentParser()
        client_session.Session.register_cli_options(self.parser)

    def get_session(self, val, **kwargs):
        args = self.parser.parse_args(val.split())
        return client_session.Session.load_from_cli_options(args, **kwargs)

    def test_insecure_timeout(self):
        s = self.get_session('--insecure --timeout 5.5')

        self.assertFalse(s.verify)
        self.assertEqual(5.5, s.timeout)

    def test_client_certs(self):
        cert = '/path/to/certfile'
        key = '/path/to/keyfile'

        s = self.get_session('--os-cert %s --os-key %s' % (cert, key))

        self.assertTrue(s.verify)
        self.assertEqual((cert, key), s.cert)

    def test_cacert(self):
        cacert = '/path/to/cacert'

        s = self.get_session('--os-cacert %s' % cacert)

        self.assertEqual(cacert, s.verify)
