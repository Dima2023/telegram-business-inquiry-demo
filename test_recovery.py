import tempfile
import sqlite3
import subprocess
import sys
import contextlib
import io
from unittest.mock import patch
import live_once
from pathlib import Path
import unittest
from recovery import Inbox
class Tests(unittest.TestCase):
 def test_duplicate_and_restart(self):
  with tempfile.TemporaryDirectory() as tmp:
   db=Path(tmp)/'state.db'
   for ident,text in [(1,'REPORT'),(2,'2'),(3,'confirm')]:
    box=Inbox(db,{7},9);self.assertTrue(box.accept({'update_id':ident,'message':{'chat':{'id':7,'type':'private'},'text':text}}));box.close()
   box=Inbox(db,{7},9)
   self.assertFalse(box.accept({'update_id':3,'message':{'chat':{'id':7,'type':'private'},'text':'confirm'}}))
   self.assertEqual(len(box.pending()),4);self.assertEqual(box.offset(),4);box.close()
 def test_uncertain_is_not_retried(self):
  with tempfile.TemporaryDirectory() as tmp:
   box=Inbox(Path(tmp)/'db',{7},9);box.accept({'update_id':1,'message':{'chat':{'id':7,'type':'private'},'text':'catalog'}})
   class API:
    def send_message(self,*args):raise OSError('synthetic failure')
   with self.assertRaises(OSError):box.deliver(API())
   self.assertEqual(box.pending(),[]);self.assertEqual(box.uncertain_count(),1);box.close()
 def test_unapproved_recipient(self):
  with tempfile.TemporaryDirectory() as tmp:
   box=Inbox(Path(tmp)/'db',{7},9)
   box.accept({'update_id':1,'message':{'chat':{'id':8,'type':'private'},'text':'catalog'}})
   self.assertEqual(box.pending(),[]);box.close()
 def test_successful_send_then_delivered_write_fails(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'state.db'
   box=Inbox(path,{7},9)
   box.accept({'update_id':1,'message':{'chat':{'id':7,'type':'private'},'text':'catalog'}})
   # Fail only the final local status write, after the fake remote returns success.
   box.db.execute("CREATE TRIGGER fail_delivered BEFORE UPDATE OF status ON outbox WHEN NEW.status='delivered' BEGIN SELECT RAISE(ABORT, 'synthetic status-write failure'); END")
   box.db.commit()
   calls=[]
   class API:
    def send_message(self,*args):calls.append(args);return {'message_id':42}
   with self.assertRaises(sqlite3.DatabaseError):box.deliver(API())
   self.assertEqual(len(calls),1)
   box.close()
   restarted=Inbox(path,{7},9)
   self.assertEqual(restarted.uncertain_count(),1)
   self.assertEqual(restarted.pending(),[])
   restarted.deliver(API())
   self.assertEqual(len(calls),1)
   restarted.close()
   # Exercise the actual runner with real reopened SQLite and a mocked transport.
   with patch('sys.argv',['live_once.py','--live','--test-chat','7','--admin-chat','9','--state',str(path)]),patch.object(live_once,'TelegramAPI') as api,patch.object(live_once.os,'umask'),patch.dict(live_once.os.environ,{},clear=True),contextlib.redirect_stdout(io.StringIO()):
    self.assertEqual(live_once.main(),2)
    api.return_value.get_me.assert_not_called()
    api.return_value.get_updates.assert_not_called()
    api.return_value.send_message.assert_not_called()
 def test_process_exit_after_fake_remote_acceptance(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'state.db';marker=Path(tmp)/'fake-acceptance.txt'
   box=Inbox(path,{7},9)
   box.accept({'update_id':1,'message':{'chat':{'id':7,'type':'private'},'text':'catalog'}})
   box.close()
   code="""import os,sys
from pathlib import Path
from recovery import Inbox
class FakeAPI:
 def send_message(self,*args):
  Path(sys.argv[2]).write_text('synthetic remote acceptance')
  os._exit(73)
Inbox(Path(sys.argv[1]),{7},9).deliver(FakeAPI())
"""
   result=subprocess.run([sys.executable,'-c',code,str(path),str(marker)],cwd=Path(__file__).parent,capture_output=True,text=True)
   self.assertEqual(result.returncode,73,result.stderr)
   self.assertEqual(marker.read_text(),'synthetic remote acceptance')
   restarted=Inbox(path,{7},9)
   self.assertEqual(restarted.uncertain_count(),1)
   class NeverSend:
    def send_message(self,*args):raise AssertionError('duplicate send attempted')
   restarted.deliver(NeverSend())
   restarted.close()
if __name__=='__main__':unittest.main()
