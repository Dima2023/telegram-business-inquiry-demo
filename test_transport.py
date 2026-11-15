import json
import unittest
from telegram_transport import TelegramAPI,TransportError
class Response:
 def __init__(self,body):self.body=body
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self,n):return self.body
class Tests(unittest.TestCase):
 def test_request_shape_and_allowlist(self):
  calls=[]
  def send(request,timeout):
   calls.append((request,timeout));return Response(b'{"ok":true,"result":{"message_id":1}}')
  api=TelegramAPI('123:TEST_ONLY',allowed_chats={7},sender=send)
  api.send_message(7,'Synthetic test')
  request,timeout=calls[0]
  self.assertEqual(json.loads(request.data),{'chat_id':7,'text':'Synthetic test'})
  self.assertTrue(request.full_url.startswith('https://api.telegram.org/'))
  with self.assertRaises(ValueError):api.send_message(8,'Blocked')
  self.assertEqual(len(calls),1)
 def test_errors_are_redacted_and_not_retried(self):
  count=[]
  def send(request,timeout):count.append(1);raise OSError('123:TEST_ONLY leaked URL')
  api=TelegramAPI('123:TEST_ONLY',allowed_chats={7},sender=send)
  with self.assertRaises(TransportError) as caught:api.send_message(7,'x')
  self.assertNotIn('TEST_ONLY',str(caught.exception));self.assertEqual(len(count),1)
 def test_api_and_json_failure(self):
  for body in [b'{"ok":false,"description":"token details"}',b'bad',b'[]',b'{"ok":true}',b'x'*1048577]:
   api=TelegramAPI('123:TEST_ONLY',allowed_chats={7},sender=lambda *a,**k:Response(body))
   with self.assertRaises(TransportError):api.get_me()
 def test_get_updates_arguments(self):
  seen=[]
  def send(request,timeout):seen.append(json.loads(request.data));return Response(b'{"ok":true,"result":[]}')
  api=TelegramAPI('123:TEST_ONLY',allowed_chats={7},sender=send)
  self.assertEqual(api.get_updates(50),[]); self.assertEqual(seen[0]['offset'],50)


class ProxyOptInTests(unittest.TestCase):
    def https_proxy_for(self, flag):
        import os, urllib.request
        from unittest.mock import patch
        env = {k: v for k, v in os.environ.items() if 'proxy' not in k.lower()}
        env.update({'TELEGRAM_USE_ENV_PROXY': flag, 'HTTPS_PROXY': 'http://proxy.example:3128'})
        with patch.dict(os.environ, env, clear=True):
            api = TelegramAPI('1:abc', {1})
        handlers = [h for h in api._sender.__self__.handlers if isinstance(h, urllib.request.ProxyHandler)]
        return handlers[0].proxies.get('https') if handlers else None

    def test_proxies_ignored_by_default(self):
        self.assertIsNone(self.https_proxy_for(''))

    def test_env_proxy_used_only_when_opted_in(self):
        self.assertEqual(self.https_proxy_for('1'), 'http://proxy.example:3128')


if __name__ == "__main__":
    unittest.main()
