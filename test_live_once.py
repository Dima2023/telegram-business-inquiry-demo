import contextlib
import io
import sqlite3
import unittest
from unittest.mock import patch
import live_once

class Tests(unittest.TestCase):
 def test_sqlite_error_is_clean_and_network_not_called(self):
  output=io.StringIO()
  with patch('sys.argv',['live_once.py','--live','--test-chat','7','--admin-chat','9']), patch.object(live_once,'TelegramAPI') as api, patch.object(live_once,'Inbox',side_effect=sqlite3.DatabaseError('synthetic corrupt DB')), patch.object(live_once.os,'umask'), patch.dict(live_once.os.environ,{},clear=True),contextlib.redirect_stdout(output):
   self.assertEqual(live_once.main(),2)
   api.return_value.get_me.assert_not_called()
   api.return_value.get_updates.assert_not_called()
  self.assertIn('SQLite state unavailable',output.getvalue())
  self.assertNotIn('Traceback',output.getvalue())
 def test_uncertain_blocks_all_network(self):
  with patch('sys.argv',['live_once.py','--live','--test-chat','7','--admin-chat','9']),patch.object(live_once,'TelegramAPI') as api,patch.object(live_once,'Inbox') as inbox,patch.object(live_once.os,'umask'),patch.dict(live_once.os.environ,{},clear=True),contextlib.redirect_stdout(io.StringIO()):
   inbox.return_value.uncertain_count.return_value=1
   self.assertEqual(live_once.main(),2)
   api.return_value.get_me.assert_not_called();inbox.return_value.close.assert_called_once()
if __name__=='__main__':unittest.main()
