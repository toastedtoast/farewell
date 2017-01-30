# -*- coding: utf-8 -*-

from flask import Flask
from flask_ask import Ask, statement, question, session, request
import json
import requests

app = Flask(__name__)
ask = Ask(app, '/ask')

@app.route("/")
def hello_web():

    return "Hello World"


@ask.on_session_started
def session_start():

    sess = requests.Session()
    sess.headers.update({'Authorization': 'Bearer N8qaPmzFDvo.cwA.RU4.p7j3hagKTcTYvF1K1lSNKfn-e5-rPujgttTpKip_5wc'})
    res = sess.post('https://directline.botframework.com/v3/directline/conversations')

    j = json.loads(res.content)
    session.attributes["ConversationId"] = j['conversationId']


@ask.launch
@ask.intent('Hello')
def hello():

    print("Hello")

    sess = requests.Session()
    sess.headers.update({'Authorization': 'Bearer N8qaPmzFDvo.cwA.RU4.p7j3hagKTcTYvF1K1lSNKfn-e5-rPujgttTpKip_5wc'})
    
    if session.attritbutes is None or "ConversationId" not in session.attritbutes:
        startConversation()

    conversationId = session.attributes["ConversationId"] if "ConversationId" in session.attributes else None
    watermark = None #session.attributes["Watermark"] if "Watermark" in session.attributes else None

    b = {"type": "message", "from": {"id": "dirk"}, "text": "hello"}
    res = sess.post('https://directline.botframework.com/v3/directline/conversations/{0}/activities'.format(conversationId), json=b)
    # j = json.loads(res.content)

    watermarkParameter = "?watermark={0}".format(watermark) if watermark is not None else ""
    res = sess.get('https://directline.botframework.com/v3/directline/conversations/{0}/activities{1}'.format(conversationId, watermarkParameter))

    text, image, watermark = textAndImageFromResponse(res)
    # image = "https://raw.githubusercontent.com/snorpey/jpg-glitch/master/images/lincoln.jpg"
    session.attributes["Watermark"] = watermark

    return question(text).standard_card(title="Farewell Dirk", text=text, large_image_url=image).reprompt("You can ask for a specific farewell using the name of your coworker or just ask for a random.")


@ask.intent('Random')
def random():

    print("Random")

    sess = requests.Session()
    sess.headers.update({'Authorization': 'Bearer N8qaPmzFDvo.cwA.RU4.p7j3hagKTcTYvF1K1lSNKfn-e5-rPujgttTpKip_5wc'})
    
    if session.attritbutes is None or "ConversationId" not in session.attritbutes:
        startConversation()

    conversationId = session.attributes["ConversationId"] if "ConversationId" in session.attributes else None
    watermark = None #session.attributes["Watermark"] if "Watermark" in session.attributes else None

    b = {"type": "message", "from": {"id": "dirk"}, "text": "random"}
    res = sess.post('https://directline.botframework.com/v3/directline/conversations/{0}/activities'.format(conversationId), json=b)
    # j = json.loads(res.content)
    
    watermarkParameter = "?watermark={0}".format(watermark) if watermark is not None else ""
    res = sess.get('https://directline.botframework.com/v3/directline/conversations/{0}/activities{1}'.format(conversationId, watermarkParameter))

    text, image, watermark = textAndImageFromResponse(res)
    session.attributes["Watermark"] = watermark

    return question(text).standard_card(title="Farewell Dirk", text=text, large_image_url=image).reprompt("You can ask for a specific farewell using the name of your coworker or just ask for a random.")


@ask.intent('FarewellByName')
def farewellByName(name):

    print("Searching Farewell from {0}".format(name))

    if session.attritbutes is None or "ConversationId" not in session.attritbutes:
        startConversation()

    sess = requests.Session()
    sess.headers.update({'Authorization': 'Bearer N8qaPmzFDvo.cwA.RU4.p7j3hagKTcTYvF1K1lSNKfn-e5-rPujgttTpKip_5wc'})
    
    conversationId = session.attributes["ConversationId"] if "ConversationId" in session.attributes else None
    watermark = None #session.attributes["Watermark"] if "Watermark" in session.attributes else None

    b = {u"type": u"message", u"from": {u"id": u"dirk"}, u"text": name}
    res = sess.post('https://directline.botframework.com/v3/directline/conversations/{0}/activities'.format(conversationId), json=b)
    # j = json.loads(res.content)

    watermarkParameter = "?watermark={0}".format(watermark) if watermark is not None else ""
    res = sess.get('https://directline.botframework.com/v3/directline/conversations/{0}/activities{1}'.format(conversationId, watermarkParameter))

    text, image, watermark = textAndImageFromResponse(res)
    session.attributes["Watermark"] = watermark

    return question(text).standard_card(title="Farewell Dirk", text=text, large_image_url=image).reprompt("You can ask for a specific farewell using the name of your coworker or just ask for a random.")


def startConversation():

    sess = requests.Session()
    sess.headers.update({'Authorization': 'Bearer N8qaPmzFDvo.cwA.RU4.p7j3hagKTcTYvF1K1lSNKfn-e5-rPujgttTpKip_5wc'})
    res = sess.post('https://directline.botframework.com/v3/directline/conversations')

    j = json.loads(res.content)
    session.attributes["ConversationId"] = j['conversationId']


def textAndImageFromResponse(response):

    j = json.loads(response.content)

    text = u""
    image = None

    for activity in j["activities"]:
        if activity["from"]["id"] == "farewell_dirk":
            if activity["type"] == "message":

                text += u"{0} ".format(activity["text"])

                if image is None and "attachments" in activity > 0:
                    for a in activity["attachments"]:
                        if "image" in a["contentType"]:
                            image = a["contentUrl"].replace("http://", "https://")
                            break

    if image is not None:
        text += u". With this message there is an image attachment you can see in the Alexa App."

    text = text.encode("utf-8")
    watermark = j["watermark"]

    return text, image, watermark


if __name__ == '__main__':
    app.run(debug=False, port=5000, host="0.0.0.0")