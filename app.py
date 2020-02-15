from flask import Flask, request
import os, sys
import scraper
from details import guid,passw,uid,messagepass,loggedin
from expect import expecting_start, expecting_guid, expecting_pass, expecting_input, expecting_day, expecting_date, expecting_dayno
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
                uid = sender_id
                recipient_id = messaging_event['recipient']['id']
                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        #messaging_text = "reply : "+messaging_event['message']['text']+"!!!!!!!"
                        messaging_text = handleExpect(messaging_event['message']['text'])
                    else:
                        messaging_text = 'no text'
                    response = messaging_text
                    bot.send_text_message(sender_id, response)

    return "ok", 200

def handleExpect(message):
    if expecting_start == 1 and message == "start":
        expecting_guid = 1
        expecting_start = 0
        return "Enter GUID: "
    elif expecting_guid == 1:
        guid = message
        expecting_guid = 0
        expecting_pass = 1
        return "Enter password: "
    elif expecting_pass == 1:
        passw = message
        expecting_pass = 0
        bot.send_text_message(uid, "Please wait..")
        result = login(guid, passw)
        if result == "success":
            expecting_input = 1
            return "Logged in!\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day\5 - Log out and Quit"
        else:
            expecting_guid = 1
            return result+"Enter GUID again."
    elif expecting_input == 1 and expecting_day == 1:
        expecting_day = 0
        return read_week(message)
    elif expecting_input == 1 and expecting_dayno == 1:
        expecting_day = 0
        return loop_days(int(message))
    elif expecting_input == 1 and expecting_date == 1:
        expecting_date = 1
        return specific_day(message)
    elif expecting_input == 1:
        if message == "1":
            return read_today()
        elif message == "2":
            expecting_day = 1
            return "What day?"
        elif message == "3":
            expecting_dayno = 1
            return "How many days?"
        elif message == "4":
            expecting_date = 1
            return "Enter date in DD/MM/YYYY format: "
        elif message == "5":
            expecting_start = 1
            expecting_input = 0
            exit()



def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug = True, port = 80)