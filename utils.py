from wit import Wit

access_token = "UYW4Y4L4A5XQB3DSWJHAQZSH5HBFGYZ7"

client = Wit(access_token = access_token)

def wit_response(message_text):
    resp = client.message(message_text)
    

print(resp)