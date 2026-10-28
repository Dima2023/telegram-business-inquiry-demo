"""Explicit HTTPS transport. Importing this module never reads credentials or calls APIs."""
import json
import re
import urllib.request

class TransportError(RuntimeError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None

class TelegramAPI:
    def __init__(self, token, allowed_chats, sender=None):
        if not isinstance(token,str) or not re.fullmatch(r'[0-9]+:[A-Za-z0-9_-]+',token):
            raise ValueError('Invalid bot token format')
        if not allowed_chats or any(type(chat) is not int for chat in allowed_chats):
            raise ValueError('Explicit integer test chat allowlist required')
        self._token=token
        self.allowed_chats=frozenset(allowed_chats)
        self._sender=sender or urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect()).open

    def _call(self, method, payload):
        request=urllib.request.Request('https://api.telegram.org/bot'+self._token+'/'+method,
            data=json.dumps(payload).encode('utf-8'),headers={'Content-Type':'application/json'},method='POST')
        try:
            with self._sender(request,timeout=20) as response:
                raw=response.read(1024*1024+1)
            if len(raw)>1024*1024:raise ValueError('response limit')
            data=json.loads(raw)
            if not isinstance(data,dict) or data.get('ok') is not True or 'result' not in data:
                raise ValueError('API rejected request')
            return data['result']
        except Exception:
            # URLs contain bot credentials. Never expose raw HTTP errors or bodies.
            # No automatic retry: a failed send may have delivered remotely.
            raise TransportError('Telegram request failed; outcome may be unknown. No automatic retry.') from None

    def get_me(self):return self._call('getMe',{})

    def get_updates(self, offset=0):
        if type(offset) is not int or offset<0:raise ValueError('Invalid offset')
        result=self._call('getUpdates',{'offset':offset,'timeout':0,'limit':20,'allowed_updates':['message']})
        if not isinstance(result,list):raise TransportError('Unexpected updates response')
        return result

    def send_message(self,chat_id,text):
        if type(chat_id) is not int or chat_id not in self.allowed_chats:raise ValueError('Recipient is not approved')
        if not isinstance(text,str) or not 1<=len(text)<=4000:raise ValueError('Text length must be 1–4000')
        return self._call('sendMessage',{'chat_id':chat_id,'text':text})
