################################# Messaging system #################################

from datetime import datetime
from flask import request
from app import app
from apsw import Error
import dbManager
from json import dumps
timestamp_format = '%Y-%m-%d %H:%M:%S'


@app.get('/showInbox')
def showInbox():
    receiver = request.args.get('sender')
    result = ""
    try:
        c = dbManager.getMessagesInInbox(receiver)
        rows = c.fetchall()
        result = result + 'You have '+ str(len(rows)) + ' messages:\n'
        for row in rows:
            result = f'{result} From {dumps(row[1])} message: {dumps(row[2])} Date sent: {dumps(row[4])}\n'
        c.close()
        return result
    except Error as e:
        return f'ERROR: {e}'

@app.route('/send', methods=['POST'])
def send():
    try:
        sender = request.args.get('sender')
        message = request.args.get('message') 
        receiver = request.args.get('receiver')
        timestamp = datetime.now().strftime(timestamp_format)
        if not dbManager.usernameExists(receiver):
            return f'ERROR: {receiver} is not a valid user'
        if not sender or not message or not receiver:
            return f'ERROR: missing sender, message or receiver'
        dbManager.sendMessage(sender, message, receiver, timestamp)
        return f'Message: "{message}" sent successfully to {receiver}'
    except Error as e:
        return f'ERROR: {e}'
