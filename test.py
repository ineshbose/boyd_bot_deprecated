from app import webhook,bot

def main(uid):
    bot.send_text_message(uid, "First number: ")
    a1 = int(webhook())
    bot.send_text_message(uid, "Second number: ")
    a2 = int(webhook())
    bot.send_text_message(uid, a1+a2)