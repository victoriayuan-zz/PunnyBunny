import os
import sys
import json

import random
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    
    # endpoint for processing incoming messaging events
    
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    
    if data["object"] == "page":
        
        first_time = True
        
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                
                if messaging_event.get("message"):  # someone sent us a message
                    
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    
                    if first_time:
                        send_message(sender_id, "Hi, I'm Punny Bunny! I can tell you a funny bunny pun. Do you want to hear it?")
                        first_time = False

                    else:
                        puns = ["Every bunny was kungfu fighting~!",
                                "I'd make a veggie pun but no one would carrot all!",
                                "I whip my hare back and forth~",
                                "And now he's just some bunny that I used to know~",
                                "How do you know if I'm getting old? It's the gray hare.",
                                "You seem to be having a bad hare day",
                                "What is my favorite dance style? Hip-hop!",
                                "What do you get when you cross a bunny with a leaf blower? A hare dryer!",
                                "What did the bunny give his girlfriend? A 14-carrot ring!",
                                "How do you know carrots are good for your eyes? Because you never see a bunny wearing glasses!",
                                "If you have a line of 100 bunnies in a row and 99 of them take one step backwards, what do you have? A receding hare line!",
                                "How many bunnies does it take to change a lightbulb? Only one if it hops right to it!",
                                "You must be a chocolate bunny, because I just want to nibble on your ears ;)",
                                "You must be the Easter Bunny, because you've got a basket full of sweetness ;D",
                                "What do you call a bunny who was raised in a hotel? An inn-grown hare",
                                "Where did the bunny groom and the bunny bride go after their wedding? On a bunnymoon!",
                                "What do you call a bunny housekeeper? A dust bunny!",
                                "How are bunnies and calculators alike? They both multiply quickly!"]
                        send_message(sender_id, random.choice(puns))
                
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
