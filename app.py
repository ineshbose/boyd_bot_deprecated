from flask import Flask, request
import os, sys
import scraper
#from details import guid,passw,uid,messagepass,loggedin
#from expect import expecting_start, expecting_guid, expecting_pass, expecting_input, expecting_day, expecting_date, expecting_dayno
#import redis
import details
import expect
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
    if details.uid == "":
        details.uid = data['entry'][0]['messaging'][0]['sender']['id']
    #log(data)
    if data['object'] == 'page':
        '''
        details.uid = data['entry']['messaging']['sender']['id']
        print(details.uid)
        if 'text' in data['entry']['messaging']['message']:
            messaging_text = handleExpect(data['entry']['messaging']['message']['text'])
        else:
            messaging_text = 'no text'
        response = messaging_text
        bot.send_text_message(details.uid, response)
        '''
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                #details.uid = messaging_event['sender']['id']
                #recipient_id = messaging_event['recipient']['id']
                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        #print(data['entry']['messaging']['message']['text'])
                        #messaging_text = "reply : "+messaging_event['message']['text']+"!!!!!!!"
                        #bot.send_text_message(details.uid, handleExpect(messaging_event['message']['text']))
                        messaging_text = messaging_event['message']['text']
                    else:
                        #bot.send_text_message(details.uid, "no text")
                        messaging_text = 'no text'
                    response = messaging_text
                    if sender_id == details.uid:
                        bot.send_text_message(details.uid, handleExpect(response))
                    else:
                        bot.send_text_message(sender_id, response)
                    #bot.send_text_message(details.uid, handleExpect(response))


    return "ok", 200

def handleExpect(message):
    if message == "no text":
        return "Hello there! Say START to wake me!"
    elif expect.expecting_start == 1 and message.upper() == "START":
        bot.send_text_message(details.uid, "Hello there!")
        expect.expecting_guid = 1
        expect.expecting_start = 0
        return "Enter GUID."
    elif expect.expecting_guid == 1:
        bot.send_text_message(details.uid, "Thank you for the GUID.")
        details.guid = message
        #print(details.guid)
        expect.expecting_guid = 0
        expect.expecting_pass = 1
        return "Enter password."
    elif expect.expecting_pass == 1:
        bot.send_text_message(details.uid, "Thank you for the password. You can delete it.")
        details.passw = message
        #print(details.passw)
        expect.expecting_pass = 0
        bot.send_text_message(details.uid, "Please wait..")
        result = scraper.login(details.guid, details.passw)
        if result == "success":
            expect.expecting_input = 1
            return "Logged in!\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day\n5 - Logout & Quit"
        else:
            expect.expecting_guid = 1
            return result+"Enter GUID again."
    elif expect.expecting_input == 1 and expect.expecting_day == 1:
        expect.expecting_day = 0
        return scraper.read_week(message)
    elif expect.expecting_input == 1 and expect.expecting_dayno == 1:
        expect.expecting_day = 0
        return scraper.loop_days(int(message))
    elif expect.expecting_input == 1 and expect.expecting_date == 1:
        expect.expecting_date = 0
        return scraper.specific_day(message)
    elif expect.expecting_input == 1:
        if message == "1":
            return scraper.read_today()
        elif message == "2":
            expect.expecting_day = 1
            return "What day?"
        elif message == "3":
            expect.expecting_dayno = 1
            return "How many days?"
        elif message == "4":
            expect.expecting_date = 1
            return "Enter date in DD/MM/YYYY format: "
        elif message == "5":
            expect.expecting_start = 1
            expect.expecting_input = 0
            scraper.close()
            return "Logged out! Goodbye. Say START to wake me. :)"



def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug = True, port = 80)