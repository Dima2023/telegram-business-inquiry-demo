"""One bounded poll for an explicitly approved dedicated synthetic Telegram test bot."""
import argparse
import os
import sqlite3
from pathlib import Path
from telegram_transport import TelegramAPI,TransportError
from recovery import Inbox

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live',action='store_true',help='explicitly enable external requests')
    p.add_argument('--test-chat',type=int,required=True)
    p.add_argument('--admin-chat',type=int,required=True)
    p.add_argument('--state',type=Path,default=Path('telegram-state.db'))
    args=p.parse_args()
    if not args.live:p.error('No calls made. Explicit --live required after authorization.')
    box=None
    try:
        api=TelegramAPI(os.environ.get('TELEGRAM_BOT_TOKEN',''),{args.test_chat,args.admin_chat})
        if args.state.is_symlink():raise ValueError('State file must not be a symlink')
        os.umask(0o077)
        box=Inbox(args.state,{args.test_chat},args.admin_chat)
        if box.uncertain_count():raise ValueError('Uncertain deliveries require manual reconciliation before further sends')
        api.get_me()
        box.deliver(api)
        for update in api.get_updates(box.offset()):box.accept(update)
        box.deliver(api)
        print('One poll completed. Check the approved test chats; no credentials printed.')
        return 0
    except sqlite3.Error:
        print('Stopped: SQLite state unavailable or corrupt; no automatic retry.');return 2
    except (ValueError,OSError,TransportError) as exc:
        print('Stopped:',str(exc));return 2
    finally:
        if box:box.close()
if __name__=='__main__':raise SystemExit(main())
