import sys
import tempfile
import unittest
from pathlib import Path

from recovery import Inbox

sys.path.insert(0, str(Path(__file__).parent / 'evidence'))
from state_summary import summary  # noqa: E402

CHAT, ADMIN = 5550001234, 5550009876


class Tests(unittest.TestCase):
    def test_summary_counts_inquiries_and_hides_chats_and_texts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'state.db'
            box = Inbox(path, {CHAT}, ADMIN)
            for ident, text in enumerate(['/start', 'catalog', 'REPORT', '2', 'confirm', 'confirm'], 1):
                box.accept({'update_id': ident, 'message': {'chat': {'id': CHAT, 'type': 'private'}, 'text': text}})
            box.close()
            lines = summary(str(path))
            before = path.read_bytes()
        self.assertEqual(lines[0], 'updates processed: 6')
        self.assertTrue(lines[1].startswith('outbox by status: pending '))
        self.assertEqual(lines[2:], ['inquiries recorded: 1',
                                     '  id=1 service=REPORT quantity=2 status=mock_admin_record'])
        text = '\n'.join(lines)
        for secret in (str(CHAT), str(ADMIN), 'SYNTHETIC TEST INQUIRY', 'Preview'):
            self.assertNotIn(secret, text)
        self.assertTrue(before)  # file was readable; summary opened it read-only

    def test_missing_file_is_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nope.db'
            with self.assertRaises(Exception):
                summary(str(path))
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
