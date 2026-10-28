"""Offline synthetic inquiry workflow. No Telegram requests are made."""
CATALOG = {'REPORT': 'Weekly reporting setup', 'CLEAN': 'CSV cleanup consultation'}

class Bot:
    def __init__(self):
        self.sessions = {}
        self.admin_log = []

    def reply(self, session, text):
        text = text.strip()
        command = text.lower()
        state = self.sessions.setdefault(session, {})
        if command in ('/start', 'cancel'):
            state.clear()
            return 'Choose catalog or faq. This is a synthetic offline simulation.'
        if command == 'catalog':
            return '\n'.join(f'{key}: {value}' for key, value in CATALOG.items())
        if command == 'faq':
            return 'This synthetic demo records inquiries only. No payments or real service booking. Type cancel to reset.'
        if text.upper() in CATALOG:
            state.clear()
            state['service'] = text.upper()
            return 'Enter quantity from 1 to 100.'
        if 'service' in state and 'quantity' not in state:
            if len(text) > 3 or not text.isascii() or not text.isdigit() or not 1 <= int(text) <= 100:
                return 'Enter a whole quantity from 1 to 100.'
            state['quantity'] = int(text)
            return f"Preview: {CATALOG[state['service']]} x {state['quantity']}. Type confirm or cancel."
        if command == 'confirm' and 'quantity' in state:
            self.admin_log.append({'id': len(self.admin_log)+1, 'service': state['service'], 'quantity': state['quantity'], 'status':'mock_admin_record'})
            state.clear()
            return 'Recorded in the mock admin log. No Telegram message was sent.'
        return 'Choose catalog or faq; select a service before confirming.'


def telegram_payload(bot, update):
    """Transport contract only: map a private text Update to sendMessage parameters.

    Caller must handle update_id deduplication, persistence and delivery retries.
    This function does not call Telegram or imply delivery.
    """
    if not isinstance(update, dict): return None
    message = update.get('message', {})
    if not isinstance(message, dict): return None
    chat = message.get('chat', {})
    if not isinstance(chat, dict): return None
    if chat.get('type') != 'private' or type(chat.get('id')) is not int or not isinstance(message.get('text'), str):
        return None
    return {'chat_id': chat['id'], 'text': bot.reply(str(chat['id']), message['text'])}

if __name__ == '__main__':
    import json
    bot = Bot()
    print('OFFLINE SIMULATION — synthetic inquiries only. Type quit to exit.')
    while True:
        try: text = input('You > ')
        except EOFError: break
        if text == 'quit': break
        print('Bot > '+bot.reply('local', text))
    print(json.dumps(bot.admin_log, indent=2))
