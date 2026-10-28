"""SQLite inbox/outbox for one dedicated synthetic test bot and one runner."""
import json
import sqlite3
from bot import Bot,telegram_payload

class Inbox:
    def __init__(self,path,allowed_chats,admin_chat):
        self.allowed=frozenset(allowed_chats);self.admin=admin_chat
        self.db=sqlite3.connect(path)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS updates(id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY, chat INTEGER NOT NULL, text TEXT NOT NULL, status TEXT NOT NULL);''')
    def close(self):self.db.close()
    def offset(self):return self.db.execute('SELECT coalesce(max(id)+1,0) FROM updates').fetchone()[0]
    def accept(self,update):
        if not isinstance(update,dict) or type(update.get('update_id')) is not int or update['update_id']<0:raise ValueError('Invalid update')
        with self.db:
            if self.db.execute('SELECT 1 FROM updates WHERE id=?',(update['update_id'],)).fetchone():return False
            self.db.execute('INSERT INTO updates VALUES (?)',(update['update_id'],))
            message=update.get('message');chat=message.get('chat') if isinstance(message,dict) else None
            if not isinstance(chat,dict) or type(chat.get('id')) is not int or chat['id'] not in self.allowed:return True
            bot=Bot();saved=self.db.execute('SELECT value FROM state WHERE id=1').fetchone()
            if saved:
                data=json.loads(saved[0]);bot.sessions=data['sessions'];bot.admin_log=data['admin_log']
            before=len(bot.admin_log);payload=telegram_payload(bot,update)
            if payload:
                text=payload['text'].replace('synthetic offline simulation','synthetic test workflow').replace('Recorded in the mock admin log. No Telegram message was sent.','Inquiry recorded locally; synthetic admin notification queued.')
                self.db.execute('INSERT INTO outbox(chat,text,status) VALUES (?,?,?)',(payload['chat_id'],text,'pending'))
            if len(bot.admin_log)>before:
                self.db.execute('INSERT INTO outbox(chat,text,status) VALUES (?,?,?)',(self.admin,'SYNTHETIC TEST INQUIRY '+json.dumps(bot.admin_log[-1]),'pending'))
            self.db.execute('INSERT OR REPLACE INTO state VALUES (1,?)',(json.dumps({'sessions':bot.sessions,'admin_log':bot.admin_log}),))
        return True
    def pending(self):return self.db.execute("SELECT id,chat,text FROM outbox WHERE status='pending' ORDER BY id").fetchall()
    def uncertain_count(self):return self.db.execute("SELECT count(*) FROM outbox WHERE status='uncertain'").fetchone()[0]
    def deliver(self,api):
        for ident,chat,text in self.pending():
            with self.db:self.db.execute("UPDATE outbox SET status='uncertain' WHERE id=?",(ident,))
            api.send_message(chat,text)
            with self.db:self.db.execute("UPDATE outbox SET status='delivered' WHERE id=?",(ident,))
