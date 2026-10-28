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
if __name__=='__main__':unittest.main()
