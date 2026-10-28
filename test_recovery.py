import tempfile
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
if __name__=='__main__':unittest.main()
