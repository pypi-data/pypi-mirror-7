from unittest import TestCase
from unittest import mock

import asyncio


RESPONSES = {

    'http://localhost/test_xmlrpc_ok': {'status': 200,
                                        'body': """<?xml version="1.0"?>
<methodResponse>
   <params>
      <param>
         <value><int>1</int></value>
      </param>
   </params>
</methodResponse>"""
},
    'http://localhost/test_xmlrpc_fault': {'status': 200,
                                           'body': """<?xml version="1.0"?>
<methodResponse>
  <fault>
    <value>
      <struct>
        <member>
          <name>faultCode</name>
            <value><int>4</int></value>
            </member>
        <member>
           <name>faultString</name>
           <value><string>You are not lucky</string></value>
        </member>
      </struct>
    </value>
  </fault>
</methodResponse>
"""
},
    'http://localhost/test_http_500':  {'status': 500,
                                        'body': """
I am really broken
"""
}

    }


@asyncio.coroutine
def dummy_response(method, url, **kwargs):
    class Response:
        def __init__(self):
            response = RESPONSES[url]
            self.status = response['status']
            self.body = response['body']
            self.headers = {}

        @asyncio.coroutine
        def read_and_close(self):
            return self.body

    return Response()


@asyncio.coroutine
def dummy_request(*args, **kwargs):
    return dummy_response(*args, **kwargs)


class ServerProxyTestCase(TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.aiohttp_request = mock.patch('aiohttp.request', new=dummy_request)
        self.aiohttp_request.start()

    def tearDown(self):
        self.aiohttp_request.stop()

    def test_xmlrpc_ok(self):
        from aioxmlrpc.client import ServerProxy
        client = ServerProxy('http://localhost/test_xmlrpc_ok')
        response = self.loop.run_until_complete(
            client.name.space.proxfyiedcall()
            )
        self.assertEqual(response, 1)

    def test_xmlrpc_fault(self):
        from aioxmlrpc.client import ServerProxy, Fault
        client = ServerProxy('http://localhost/test_xmlrpc_fault')
        self.assertRaises(Fault,
                          self.loop.run_until_complete,
                          client.name.space.proxfyiedcall()
                          )

    def test_http_500(self):
        from aioxmlrpc.client import ServerProxy, ProtocolError
        client = ServerProxy('http://localhost/test_http_500')
        self.assertRaises(ProtocolError,
                          self.loop.run_until_complete,
                          client.name.space.proxfyiedcall()
                          )
