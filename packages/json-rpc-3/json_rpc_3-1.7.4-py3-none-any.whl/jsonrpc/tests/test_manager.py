import unittest

from mock import MagicMock

from ..manager import JSONRPCResponseManager
from ..jsonrpc import JSONRPCBatchRequest, JSONRPCBatchResponse, JSONRPCRequest, JSONRPCResponse


class TestJSONRPCResponseManager(unittest.TestCase):
    def setUp(self):
        def raise_(e):
            raise e

        self.long_time_method = MagicMock()
        self.dispatcher = {
            "add": sum,
            "list_len": len,
            "101_base": lambda **kwargs: int("101", **kwargs),
            "error": lambda: raise_(KeyError("error_explanation")),
            "long_time_method": self.long_time_method,
        }
        self.manager = JSONRPCResponseManager()

    def test_returned_type_response(self):
        request = JSONRPCRequest("add", [[]], _id=0)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCResponse))

    def test_returned_type_butch_response(self):
        request = JSONRPCBatchRequest(
            [JSONRPCRequest("add", [[]], _id=0)])
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCBatchResponse))

    def test_parse_error(self):
        req = '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
        response = self.manager.handle(req, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCResponse))
        self.assertEqual(response.error["message"], "Parse error")
        self.assertEqual(response.error["code"], -32700)

    def test_invalid_request(self):
        req = '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        response = self.manager.handle(req, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCResponse))
        self.assertEqual(response.error["message"], "Invalid Request")
        self.assertEqual(response.error["code"], -32600)

    def test_method_not_found(self):
        request = JSONRPCRequest("does_not_exist", [[]], _id=0)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCResponse))
        self.assertEqual(response.error["message"], "Method not found")
        self.assertEqual(response.error["code"], -32601)

    def test_invalid_params(self):
        request = JSONRPCRequest("add", {"a": 0}, _id=0)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCResponse))
        self.assertEqual(response.error["message"], "Invalid params")
        self.assertEqual(response.error["code"], -32602)

    def test_server_error(self):
        request = JSONRPCRequest("error", _id=0)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPCResponse))
        self.assertEqual(response.error["message"], "Server error")
        self.assertEqual(response.error["code"], -32000)
        self.assertEqual(response.error["data"], {
            "type": "KeyError",
            "args": ('error_explanation',),
            "message": "'error_explanation'",
        })

    def test_notification_calls_method(self):
        request = JSONRPCRequest("long_time_method", is_notification=True)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)
        self.long_time_method.assert_called_once_with()

    def test_notification_does_not_return_error_does_not_exist(self):
        request = JSONRPCRequest("does_not_exist", is_notification=True)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)

    def test_notification_does_not_return_error_invalid_params(self):
        request = JSONRPCRequest("add", {"a": 0}, is_notification=True)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)

    def test_notification_does_not_return_error(self):
        request = JSONRPCRequest("error", is_notification=True)
        response = self.manager.handle(request.json, self.dispatcher)
        self.assertEqual(response, None)
