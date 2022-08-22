from urllib import response
from flask import Flask, render_template, request, redirect, make_response, jsonify
import sqlite3
import json

app = Flask(__name__)

class Message:
    def __init__(self, sender, message, id=-1, claps=0):
        self.id = id
        self.author = sender
        self.message = message
        self.claps = claps

def read_messages():
    messages = []

    try:
        sqlite_connection = sqlite3.connect('messagesDB.sqlite')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = """SELECT * from messages"""
        cursor.execute(sqlite_select_query)
        rows = cursor.fetchall()

        for row in rows:
            messages.append(Message(id=row[0], sender=row[1], message=row[2], claps=row[3]))

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

    return messages

def insert_message(message):
    id = -1
    try:
        sqlite_connection = sqlite3.connect('messagesDB.sqlite')
        cursor = sqlite_connection.cursor()

        sqlite_insert_query = """INSERT INTO messages(sender, text) VALUES (?, ?)"""
        cursor.execute(sqlite_insert_query, (message.author, message.message))
        sqlite_connection.commit()
        id = cursor.lastrowid

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

    return id

def update_message(id, claps):
    try:
        sqlite_connection = sqlite3.connect('messagesDB.sqlite')
        cursor = sqlite_connection.cursor()

        sql_update_query = """Update messages set claps = ? where id = ?"""
        cursor.execute(sql_update_query, (claps, id))
        sqlite_connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

messages = read_messages()
messages.sort(key=lambda x: x.claps, reverse=True)

@app.get('/')
def index():
    return render_template('index.html', messages=messages)

@app.post('/')
def add_message():
    errors = []

    new_sender = request.form['sender']
    new_message_text = request.form['message']

    if not new_sender:
        errors.append('Введите имя отправителя')
    if not new_message_text:
        errors.append('Введите текст сообщения')
    if len(new_sender) > 30:
        errors.append('Имя отправителя не может быть длиннее 30 символов')
    if len(new_message_text) > 1000:
        errors.append('Текст сообщения не может быть длиннее 1000 символов')

    if errors:
        return render_template('index.html',
                                messages=messages, 
                                errors=errors, 
                                new_sender=new_sender, 
                                new_message_text=new_message_text)

    new_message = Message(new_sender, new_message_text)
    new_message.id = insert_message(new_message)
    messages.append(new_message)

    return render_template('index.html', messages=messages)


@app.get('/messages/<int:id>')
def message_page(id):
    message = [m for m in messages if m.id == id]
    if not message:
        return redirect('/')
    return render_template('message.html', message=message[0])

@app.post('/clap/<int:id>')
def add_clap(id):
    message = [m for m in messages if m.id == id]
    if not message:
        return redirect('/')

    message[0].claps += 1
    update_message(id, message[0].claps)

    messages.sort(key=lambda x: x.claps, reverse=True)    

    render_template('index.html', messages=messages)
    return redirect('/')

@app.post('/messages/<int:id>')
def add_clap_message_page(id):
    message = [m for m in messages if m.id == id]
    if not message:
        return redirect('/')

    message[0].claps += 1
    update_message(id, message[0].claps)

    messages.sort(key=lambda x: x.claps, reverse=True)    

    return render_template('message.html', message=message[0])



# API____________________________________________________________________________________

@app.get('/api/messages')
def getMessages():
    return jsonify([m.__dict__ for m in messages])

@app.post('/api/messages')
def addMessage():
    if 'author' not in request.json:
        response = make_response(json.dumps({
                "message": "Не найдено поле author"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 422

    if 'message' not in request.json:
        response = make_response(json.dumps({
                "message": "Не найдено поле message"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 422

    if not request.json['author']:
        response = make_response(json.dumps({
                "message": "Введите имя отправителя"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 422

    if not request.json['message']:
        response = make_response(json.dumps({
                "message": "Введите текст сообщения"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 422

    new_sender = request.json['author']
    new_message_text = request.json['message']

    if len(new_sender) > 30:
        response = make_response(json.dumps({
                "message": "Имя отправителя не может быть длиннее 30 символов"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 422

    if len(new_message_text) > 1000:
        response = make_response(json.dumps({
                "message": "Текст сообщения не может быть длиннее 1000 символов"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 422

    new_message = Message(new_sender, new_message_text)
    new_message.id = insert_message(new_message)
    messages.append(new_message)

    return jsonify(new_message.__dict__ )

@app.get('/api/messages/<int:id>')
def getMessage(id):
    message = [m for m in messages if m.id == id]
    if not message:
        response = make_response(json.dumps({
                "message": "Сообщение не найдено"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 404
    return jsonify(message[0].__dict__)

@app.post('/api/messages/<int:id>/claps')
def clapMessage(id):
    message = [m for m in messages if m.id == id]
    if not message:
        response = make_response(json.dumps({
                "message": "Сообщение не найдено"
            }))
        response.headers.set('Content-Type', 'application/json')
        return response, 404

    message[0].claps += 1
    update_message(id, message[0].claps)

    messages.sort(key=lambda x: x.claps, reverse=True)    

    response = make_response(json.dumps({
            "claps": message[0].claps
        }))
    response.headers.set('Content-Type', 'application/json')    
    return response

app.env = 'development'
app.run(port=3000, host='0.0.0.0', debug=True)