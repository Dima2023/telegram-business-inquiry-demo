# Live Telegram run — 2026-11-15

Real Telegram Bot API, dedicated test bot `@dmitry_inquiry_demo_bot`, one owner-controlled private chat used as both the test chat and the admin chat.
The token was read from a local file on the owner's machine and never printed. No webhook was set; one runner only.

Runner: `live_once.py --live --test-chat <id> --admin-chat <id>`, one bounded poll per call, called after each message
(`TELEGRAM_USE_ENV_PROXY=1`, because that machine reaches the internet only through a proxy).

Conversation (Telegram Web, screenshot `live-telegram-chat.jpg`):

| You | Bot |
|---|---|
| /start | Choose catalog or faq. This is a synthetic test workflow. |
| catalog | REPORT: Weekly reporting setup / CLEAN: CSV cleanup consultation |
| REPORT → 2 | Enter quantity… → Preview: Weekly reporting setup x 2. Type confirm or cancel. |
| confirm | Inquiry recorded locally; synthetic admin notification queued. + admin message `SYNTHETIC TEST INQUIRY {"id": 1, …}` |
| confirm (again) | Choose catalog or faq; select a service before confirming. — **no duplicate inquiry** |
| catalog → CLEAN → 3 → confirm | Preview … x 3 → recorded, admin message `{"id": 2, "service": "CLEAN", "quantity": 3}` |

Outbox after the run: 12 messages `delivered`, 0 `uncertain`; 10 updates processed, each exactly once.
The first four messages were sent before the runner was polling, so their replies arrived together; from "confirm (again)" on, each message was answered right away.

Not covered by this run: restart in the middle of a send, groups, several runners, load.
