from flask import Flask, request
import os, sys
#import scraper, expect, details
#import redis
from pymessenger import Bot
#from scraper import main
#from details import uid,guid,passw,message,loggedin

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAHFHWcVN3oBAHQwZBZBVZCrB3jCrZCZCgSsY6ZAoFTdAcbWsRt7624McoEHRFBnzXugVlkcCx0PhOLUpAkdn4gZBKYGrRpRrT4OM0yEU5dYI0aVM1RosAThjqFIejvhx4m1L8REV29aMrmspjUeVDwTLVyLBabJKcZCaZC3kooRZCx8ZAbz1BiSZBrCgIOZC7ZBLBcfUZD"

bot = Bot(PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello World", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']
                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = "reply : "+messaging_event['message']['text']
                    else:
                        messaging_text = 'no text'
                    response = messaging_text
                    bot.send_text_message(sender_id, response)

    return "ok", 200

def handleExpectation(message):
    if message == "start":
        expecting_start = 1

def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug = True, port = 80)