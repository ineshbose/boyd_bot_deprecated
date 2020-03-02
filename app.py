from flask import Flask, request, session, redirect
from pymongo import MongoClient
import os, sys
import scraper
from pymessenger import Bot
from cryptography.fernet import Fernet
from wit import Wit

app = Flask(__name__)
#witClient = Wit("7RDXFP6UYEUHHZVJCB6HYMRFFQ6M55EK")
#cluster = MongoClient("mongodb+srv://Orbviox:DyDbXczCO7XErtMC@cluster0-x4pbn.mongodb.net/test?retryWrites=true&w=majority")
#PAGE_ACCESS_TOKEN = "EAAHFHWcVN3oBAHQwZBZBVZCrB3jCrZCZCgSsY6ZAoFTdAcbWsRt7624McoEHRFBnzXugVlkcCx0PhOLUpAkdn4gZBKYGrRpRrT4OM0yEU5dYI0aVM1RosAThjqFIejvhx4m1L8REV29aMrmspjUeVDwTLVyLBabJKcZCaZC3kooRZCx8ZAbz1BiSZBrCgIOZC7ZBLBcfUZD"
witClient = Wit(os.environ.get("WIT_ACCESS_TOKEN"))
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
cluster = MongoClient(os.environ.get("MONGO_TOKEN"))
db = cluster['gutb']
collection = db['users']

file = open('key.key', 'rb')
key = file.read()
file.close()
f = Fernet(key)

bot = Bot(PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "gutbot":
        #if not request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello World", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    #log(data)
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                if collection.find({"_id": sender_id}).count()==0 and collection.find({"_id": "W"+sender_id}).count()==0:
                    bot.send_text_message(sender_id, "New user! Enter your GUID.")
                    collection.insert({"_id": "W"+sender_id, "guid": "", "thing": "", "expect":{"expecting_guid": 1, "expecting_pass": 0}})
                    return "ok", 200
                if collection.find({"_id": "W"+sender_id}).count()>0:
                    result = collection.find_one({"_id": "W"+sender_id})
                    if result['expect']['expecting_guid'] == 1:
                        try:
                            if type(int(messaging_event['message']['text'][:7])) == type(123) and type(messaging_event['message']['text'][7]) == type("a") and len(messaging_event['message']['text']) == 8:
                                collection.update_one({"_id": "W"+sender_id}, {'$set': {"guid": messaging_event['message']['text'], "expect":{"expecting_guid": 0, "expecting_pass": 1}}})
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
                        bot.send_action(sender_id, "typing_on")
                        loginResult = scraper.login(result['guid'], messaging_event['message']['text'])
                        if loginResult == 1:
                            bot.send_text_message(sender_id, "Logged in!")
                            collection.insert({"_id": sender_id, "guid": result['guid'], "thing": f.encrypt(messaging_event['message']['text'].encode()), "loggedIn": 1})
                            collection.delete_one({"_id": "W"+sender_id})
                            return "ok", 200
                        elif loginResult == 2:
                            bot.send_text_message(sender_id, "Invalid credentials. Enter GUID again.")
                            collection.update_one(
                            {"_id": "W"+sender_id}, 
                            {'$set': {"guid": "", "thing": "", "expect":{"expecting_guid": 1, "expecting_pass": 0}}})
                            return "ok", 200
                        elif loginResult == 3:
                            bot.send_text_message(sender_id, "Something went wrong. Maybe the connection was too slow. Enter GUID again.")
                            collection.update_one(
                            {"_id": "W"+sender_id}, 
                            {'$set': {"guid": "", "thing": "", "expect":{"expecting_guid": 1, "expecting_pass": 0}}})
                            return "ok", 200
                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else:
                        messaging_text = 'no text'
                    response = handleExpect(messaging_text, sender_id)
                    bot.send_text_message(sender_id, response)
    return "ok", 200

def handleExpect(message, id):
    r = collection.find_one({"_id": id})
    if r['loggedIn'] == 0:
        bot.send_text_message(id, "Logging in..")
        bot.send_action(id, "typing_on")
        collection.update_one({"_id": id}, {'$set': {'loggedIn': 1}})
        scraper.login(r['guid'], (f.decrypt(r['thing'])).decode())
        return "Logged in!"
    else:
        if message.lower() == "logout":
            collection.update_one({"_id": id}, {'$set': {'loggedIn': 0}})
            scraper.close(r['guid'])
            return "Logged out! Goodbye. :)"
        elif message.lower() == "delete data":
            collection.delete_one({"_id": id})
            return "Deleted! :) "
        else:
            try:
                parse = witClient.message(message)
                print(parse['entities']['datetime'][0]['value'][:10])
                bot.send_action(id, "typing_on")
                return scraper.specific_day(parse['entities']['datetime'][0]['value'][:10], r['guid'])
            except:
                return "Not sure how to answer that."

def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug = True, port = 80)