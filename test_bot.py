import unittest
from bot import Bot, telegram_payload
class Tests(unittest.TestCase):
 def test_full_flow_and_repeat_confirm(self):
  b=Bot(); self.assertIn('catalog',b.reply('one','/start').lower())
  self.assertIn('REPORT',b.reply('one','catalog'))
  self.assertIn('quantity',b.reply('one','REPORT'))
  self.assertIn('Preview',b.reply('one','2'))
  self.assertEqual(len(b.admin_log),0)
  self.assertIn('Recorded',b.reply('one','confirm')); self.assertEqual(len(b.admin_log),1)
  b.reply('one','confirm'); self.assertEqual(len(b.admin_log),1)
 def test_errors_cancel_and_isolation(self):
  b=Bot(); b.reply('a','REPORT')
  for value in ['0','-1','2.5','101','abc']: self.assertIn('1 to 100',b.reply('a',value))
  self.assertIn('catalog',b.reply('b','confirm').lower()); self.assertEqual(b.admin_log,[])
  b.reply('a','cancel'); self.assertIn('catalog',b.reply('a','confirm').lower())
 def test_faq_keeps_state(self):
  b=Bot(); b.reply('a','CLEAN'); self.assertIn('synthetic',b.reply('a','faq')); self.assertIn('Preview',b.reply('a','1'))
 def test_transport_shape_and_private_only(self):
  b=Bot(); update={'message':{'chat':{'id':123,'type':'private'},'text':'catalog'}}
  self.assertEqual(telegram_payload(b,update)['chat_id'],123)
  self.assertIsNone(telegram_payload(b,{'message':{'chat':{'id':1,'type':'group'},'text':'catalog'}}))
  self.assertIsNone(telegram_payload(b,{}))
 def test_malformed_updates(self):
  for update in [None, {'message':None}, {'message':{'chat':None}}, {'message':{'chat':{'type':'private','id':True},'text':'catalog'}}]:
   self.assertIsNone(telegram_payload(Bot(),update))
 def test_oversize_quantity(self):
  b=Bot(); b.reply('a','REPORT'); self.assertIn('1 to 100',b.reply('a','1'*5000))
if __name__=='__main__': unittest.main()
