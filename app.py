from flask import Flask, request, session, redirect, render_template
from pymongo import MongoClient
import os, sys
import scraper
from pymessenger import Bot
from cryptography.fernet import Fernet
from wit import Wit
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired
#from pprint import pprint


app = Flask(__name__)
witClient = Wit("7RDXFP6UYEUHHZVJCB6HYMRFFQ6M55EK")
cluster = MongoClient("mongodb+srv://Orbviox:DyDbXczCO7XErtMC@cluster0-x4pbn.mongodb.net/test?retryWrites=true&w=majority")
#PAGE_ACCESS_TOKEN = "EAAHFHWcVN3oBAHQwZBZBVZCrB3jCrZCZCgSsY6ZAoFTdAcbWsRt7624McoEHRFBnzXugVlkcCx0PhOLUpAkdn4gZBKYGrRpRrT4OM0yEU5dYI0aVM1RosAThjqFIejvhx4m1L8REV29aMrmspjUeVDwTLVyLBabJKcZCaZC3kooRZCx8ZAbz1BiSZBrCgIOZC7ZBLBcfUZD"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
db = cluster['gutb']
collection = db['users']
#app.config['SECRET_KEY'] = 'BAHQwZBZBVZCrB3'
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")


file = open('key.key', 'rb')
key = file.read()
file.close()
f = Fernet(key)


bot = Bot(PAGE_ACCESS_TOKEN)


class RegisterForm(FlaskForm):
    fb_id = HiddenField('fb_id')
    gla_id = StringField('GUID', validators=[DataRequired()])
    gla_pass = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route('/', methods=['GET','POST'])
def main():
    if request.method == 'GET':
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            #if not request.args.get("hub.verify_token") == "gutbot":
            if not request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
        return "Hello World", 200
    
    else:
        data = request.get_json()
        #log(data)
        if data['object'] == 'page':
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            messaging_event = data['entry'][0]['messaging'][0]

            if collection.count_documents({"_id": sender_id}) > 0:
                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else:
                        messaging_text = 'no text'
                    response = parse_message(messaging_text, sender_id)
                    bot.send_text_message(sender_id, response)
            
            elif collection.count_documents({"_id": "W"+sender_id}) > 0:
                bot.send_text_message(sender_id, "Doesn't seem like you've registered yet.\nRegister here: https://boydbot.herokuapp.com/register?key={}".format(sender_id))
            
            else:
                collection.insert_one({"_id": "W"+sender_id})
                bot.send_text_message(sender_id, "New user!\nRegister here: https://boydbot.herokuapp.com/register?key={}".format(sender_id))
                return "ok", 200
        return "ok", 200


@app.route('/register', methods=['GET', 'POST'])
def new_user_registration():
    
    if request.method == 'GET':
        pk = request.args.get('key')
        
        if collection.count_documents({"_id": "W"+str(pk)}) > 0:
            form = RegisterForm(fb_id=pk)
            return render_template('register.html', form=form)
        else:
            return '404'
    
    else:
        fb_id = request.form.get('fb_id')
        gla_id = request.form.get('gla_id')
        gla_pass = request.form.get('gla_pass')
        loginResult = scraper.login(gla_id, gla_pass)
        
        if loginResult == 2:
            return '<h1> Wrong credentials. <a href="https://boydbot.herokuapp.com/register?key={}">Try again.</a></h1>'.format(fb_id)
        elif loginResult == 3:
            return '<h1> Something went wrong. <a href="https://boydbot.herokuapp.com/register?key={}">Try again.</a></h1>'.format(fb_id)
        
        collection.insert_one({"_id": fb_id, "guid": gla_id, "thing": f.encrypt(gla_pass.encode()), "loggedIn": 1})
        collection.delete_one({"_id": "W"+fb_id})
        return '<h1> Login successful! You can now close this page and chat to the bot. </h1>'


def parse_message(message, id):
    r = collection.find_one({"_id": id})
    
    if r['loggedIn'] == 0:
        bot.send_text_message(id, "Logging in..")
        bot.send_action(id, "typing_on")
        loginResult = scraper.login(r['guid'], (f.decrypt(r['thing'])).decode())
    
        if loginResult == 1:
            collection.update_one({"_id": id}, {'$set': {'loggedIn': 1}}) 
            bot.send_text_message(id, "Logged in!")
    
            try:
                parse = witClient.message(message)
                bot.send_action(id, "typing_on")
                
                if 'datetime' in parse['entities']:
                    return scraper.specific_day(parse['entities']['datetime'][0]['value'][:10], r['guid'])
                
                elif 'read_next' in parse['entities']:
                    return scraper.read_now(r['guid'])
                
                else:
                    return "What's up?"
            
            except:
                return "So, what's up?"
    
        else:
            collection.delete_one({"_id": id})
            collection.insert_one({"_id": "W"+id})
            return "Something went wrong.\nRegister here: https://boydbot.herokuapp.com/register?key={}".format(id)
    
    else:
        if scraper.check_browser(r['guid']):
    
            try:
                parse = witClient.message(message)
                bot.send_action(id, "typing_on")

                if 'logout' in parse['entities']:
                    scraper.close(r['guid'])
                    collection.update_one({"_id": id}, {'$set': {'loggedIn': 0}})
                    return "Logged out! Goodbye. :)"
                
                elif 'delete_data' in parse['entities']:
                    scraper.close(r['guid'])
                    collection.delete_one({"_id": id})
                    return "Deleted! :) "
                
                elif 'datetime' in parse['entities']:
                    return scraper.specific_day(parse['entities']['datetime'][0]['value'][:10], r['guid'])
                
                elif 'read_next' in parse['entities']:
                    return scraper.read_now(r['guid'])
                
                else:
                    return "Not sure how to answer that."
            
            except:
                return "Something went wrong with parsing that."
    
        else:
            collection.update_one({"_id": id}, {'$set': {'loggedIn': 0}})
            return "You have been logged out due to some error or being idle for too long. Say hello to log in again. :) "


def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug = True, port = 80)