# Telegram inquiry bot with a safe delivery log

Catalog → quantity → preview → confirm → owner notification, with every update stored before replying, an outbox that marks sends uncertain/delivered, and a recipient allowlist.

Live run on real Telegram with a dedicated test bot on 15.11.2026: full flow, no duplicate on repeated confirm, 12 messages delivered, 0 uncertain (evidence/live-telegram-run.md). 21 automated tests. Portfolio demo with synthetic services, built with AI assistance; not client work. Single runner, polling only; no groups, payments or load testing.
