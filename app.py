from flask import Flask, request, session, redirect
#from flask_pymongo import PyMongo
from pymongo import MongoClient
import os, sys
import scraper
#import details, expect
from pymessenger import Bot
from cryptography.fernet import Fernet

app = Flask(__name__)
path = os.path.dirname(os.path.realpath(__file__))
PAGE_ACCESS_TOKEN = "EAAHFHWcVN3oBAHQwZBZBVZCrB3jCrZCZCgSsY6ZAoFTdAcbWsRt7624McoEHRFBnzXugVlkcCx0PhOLUpAkdn4gZBKYGrRpRrT4OM0yEU5dYI0aVM1RosAThjqFIejvhx4m1L8REV29aMrmspjUeVDwTLVyLBabJKcZCaZC3kooRZCx8ZAbz1BiSZBrCgIOZC7ZBLBcfUZD"
#PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
cluster = MongoClient("mongodb+srv://Orbviox:DyDbXczCO7XErtMC@cluster0-x4pbn.mongodb.net/test?retryWrites=true&w=majority")
db = cluster['test']
collection = db['test']

file = open(path+'/key.key', 'rb')
key = file.read()
file.close()
f = Fernet(key)

bot = Bot(PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
        #if not request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
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
                #details.uid = messaging_event['sender']['id']
                sender_id = messaging_event['sender']['id']
                #if collection.find({"id": sender_id}).count()==0 and collection.find({"id": "W"+sender_id}).count()==0:  # Work here!
                if collection.find({"id": sender_id}).count()==0 and collection.find({"id": "W"+sender_id}).count()==0:
                    bot.send_text_message(sender_id, "New user! Enter your GUID.")
                    collection.insert({"id": "W"+sender_id, "guid": "", "thing": "", "expect":{"expecting_start": 0, "expecting_guid": 1, "expecting_pass": 0, "expecting_input": 0, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}})
                    return "ok", 200
                if collection.find({"id": "W"+sender_id}).count()>0:
                    result = collection.find_one({"id": "W"+sender_id})
                    if result['expect']['expecting_guid'] == 1:
                        try:
                            if type(int(messaging_event['message']['text'][:7])) == type(123) and type(messaging_event['message']['text'][7]) == type("a"):
                                collection.update_one(
                                    {"id": "W"+sender_id}, 
                                    {'$set': {"guid": messaging_event['message']['text'], "expect":{"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 1, "expecting_input": 0, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
                                bot.send_text_message(sender_id, "Enter password (No one will see it and you can delete it afterwards :) ).")
                                return "ok", 200
                            else:
                                bot.send_text_message(sender_id, "Invalid GUID. It is seven integers with your surname's initial. Enter it again.")
                                return "ok", 200
                        except:
                            bot.send_text_message(sender_id, "Invalid GUID. It is seven integers with your surname's initial. Enter it again.")
                            return "ok", 200
                    elif result['expect']['expecting_pass'] == 1:
                        bot.send_text_message(sender_id, "Attempting to log you in..")
                        if scraper.login(result['guid'], messaging_event['message']['text']) == 1:
                            bot.send_text_message(sender_id, "Logged in!\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day\n5 - Logout & Quit")
                            collection.update_one(
                            {"id": "W"+sender_id},
                            {'$set': {"id": sender_id, "thing": f.encrypt(messaging_event['message']['text'].encode()), "expect":{"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
                            return "ok", 200
                        elif scraper.login(result['guid'], (f.decrypt(result['thing'])).decode()) == 2:
                            bot.send_text_message(sender_id, "Invalid credentials. Enter GUID again.")
                            collection.update_one(
                            {"id": "W"+sender_id}, 
                            {'$set': {"guid": "", "thing": "", "expect":{"expecting_start": 0, "expecting_guid": 1, "expecting_pass": 0, "expecting_input": 0, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
                            return "ok", 200
                        elif scraper.login(result['guid'], (f.decrypt(result['thing'])).decode()) == 3:
                            bot.send_text_message(sender_id, "Something went wrong. Maybe the connection was too slow. Enter GUID again.")
                            collection.update_one(
                            {"id": "W"+sender_id}, 
                            {'$set': {"guid": "", "thing": "", "expect":{"expecting_start": 0, "expecting_guid": 1, "expecting_pass": 0, "expecting_input": 0, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
                            return "ok", 200
                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        #print(data['entry']['messaging']['message']['text'])
                        #messaging_text = "reply : "+messaging_event['message']['text']+"!!!!!!!"
                        #bot.send_text_message(details.uid, handleExpect(messaging_event['message']['text']))
                        messaging_text = messaging_event['message']['text']
                    else:
                        #bot.send_text_message(details.uid, "no text")
                        messaging_text = 'no text'
                    response = handleExpect(messaging_text, sender_id)
                    ### Work needed here.
                    '''
                    if sender_id == details.uid:
                        bot.send_text_message(details.uid, handleExpect(response))
                    else:
                        bot.send_text_message(sender_id, response)
                    '''
                    bot.send_text_message(sender_id, response)
    return "ok", 200

'''
def handleExpect(message, id):
    if expect.expecting_start == 1 and message.upper()!= "START":
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
        return "Enter password (No one will see it and you can delete it afterwards :) )."
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
        expect.expecting_dayno = 0
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
'''

def handleExpect(message, id):
    r = collection.find_one({"id": id})
    if r['expect']['expecting_start'] == 1:
        collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
        scraper.login(r['guid'], (f.decrypt(r['thing'])).decode())
        return "Logged in!\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day\n5 - Logout & Quit"
    elif r['expect']['expecting_input'] == 1 and r['expect']['expecting_day'] == 1:
        collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
        return scraper.read_week(message, r['guid'])
    elif r['expect']['expecting_input'] == 1 and r['expect']['expecting_dayno'] == 1:
        collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
        return scraper.loop_days(int(message), r['guid'])
    elif r['expect']['expecting_input'] == 1 and r['expect']['expecting_date'] == 1:
        collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
        return scraper.specific_day(message, r['guid'])
    elif r['expect']['expecting_input'] == 1:
        if message == "1":
            return scraper.read_today(r['guid'])
        elif message == "2":
            collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 1, "expecting_dayno": 0, "expecting_date": 0}}})
            return "What day?"
        elif message == "3":
            collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 1, "expecting_date": 0}}})
            return "How many days?"
        elif message == "4":
            collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 0, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 1, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 1}}})
            return "Enter date in DD/MM/YYYY format: "
        elif message == "5":
            collection.update_one({"id": id}, {'$set': {'expect': {"expecting_start": 1, "expecting_guid": 0, "expecting_pass": 0, "expecting_input": 0, "expecting_day": 0, "expecting_dayno": 0, "expecting_date": 0}}})
            scraper.close(r['guid'])
            return "Logged out! Goodbye. :)"

def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug = True, port = 80)
