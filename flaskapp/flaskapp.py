import sqlite3

from flask import Flask, request, g, render_template, url_for, flash, redirect, json, send_file
from collections import Counter
app = Flask(__name__)

DATABASE = '/var/www/html/flaskapp/Project2AWS.db'

app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/countme/<input_str>')
def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    return rows

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT * FROM AWSusers""")
    htmlStr = '<br>'.join(str(row) for row in rows)
    htmlStr = htmlStr + '<br><br><a href=\"/\"><button>Back Home</button></a>'
    return htmlStr

@app.route("/username/<username>")
def sortby(username):
    rows = execute_query("SELECT * FROM AWSusers WHERE Username = \'" + username + "\'")
    return '<br>'.join(str(row) for row in rows)

@app.route("/createLogin/", methods=('GET', 'POST'))
def createLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        message = json.dumps({"username":username,"password":password})

        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        else:
            conn = get_db()
            rows = conn.execute("SELECT FirstName, LastName, Email FROM AWSusers WHERE Username = ? AND Password = ?",
                (username,password)).fetchone()

            if rows is None:
                conn.execute("INSERT INTO AWSusers (Username, Password) VALUES (?, ?)",
                    (username, password))
                conn.commit()
                conn.close()
                return redirect(url_for('createProfile',message = message))
            else:
                htmlStr = 'Username and Password Pair already exists'
                htmlStr = htmlStr + '<br><br><a href=\"/\"><button>Back Home</button></a>'
                return htmlStr

    return render_template('createLogin.html')

@app.route("/createProfile/", methods=('GET', 'POST'))
def createProfile():
    messageTemp = request.args.get("message")
    message = json.loads(messageTemp)
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        username = message['username']
        password = message['password']
        newMessage = json.dumps({"username":username,"password":password})

        if not firstName:
            flash('First Name is required!')
        elif not lastName:
            flash('Last Name is required!')
        elif not email:
            flash('Email is required!')
        else:
            conn = get_db()
            conn.execute("UPDATE AWSusers SET FirstName = ?, LastName = ?, Email = ? WHERE Username = ? AND Password = ?",
                (firstName, lastName, email, username, password))
            conn.commit()
            conn.close()

            return redirect(url_for('showProfile',message = newMessage))

    return render_template('createProfile.html')

@app.route("/showProfile/")
def showProfile():
    messageTemp = request.args.get("message")
    message = json.loads(messageTemp)
    username = message['username']
    password = message['password']
    conn = get_db()
    rows = conn.execute("SELECT FirstName, LastName, Email FROM AWSusers WHERE Username = ? AND Password = ?",
        (username,password)).fetchone()
    conn.close()
    htmlStr = '<br>'.join(str(row) for row in rows)
    htmlStr = htmlStr + '<br><br><a href=\"/\"><button>Back Home</button></a>'
    return htmlStr

@app.route("/findUser/", methods=('GET', 'POST'))
def findUser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        message = json.dumps({"username":username,"password":password})

        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        else:
            return redirect(url_for('findUserResult',message = message))

    return render_template('findUser.html')

@app.route("/findUserResult/")
def findUserResult():
    messageTemp = request.args.get("message")
    message = json.loads(messageTemp)
    username = message['username']
    password = message['password']
    conn = get_db()
    rows = conn.execute("SELECT FirstName, LastName, Email FROM AWSusers WHERE Username = ? AND Password = ?",
        (username,password)).fetchone()
    conn.close()
    if rows is None:
        htmlStr = 'Invalid Username or Password'
    else:
        htmlStr = '<br>'.join(str(row) for row in rows)
    htmlStr = htmlStr + '<br><br><a href=\"/\"><button>Back Home</button></a>'
    return htmlStr

@app.route("/extraCredit/")
def extraCredit():
    wordCount = 0
    with app.open_resource('Limerick.txt') as f:
        data = f.read()
        lines = data.split()
        wordCount += len(lines)
    htmlStr = 'Limerick.txt Word Count: ' + str(wordCount)
    htmlStr = htmlStr + '<br><br><a href=\"/downloadLimerick\"><button>Download Limerick.txt</button></a>'
    htmlStr = htmlStr + '<br><br><a href=\"/\"><button>Back Home</button></a>'
    return htmlStr

@app.route("/downloadLimerick/")
def downloadLimerick():
    return send_file('Limerick.txt', as_attachment=True)

if __name__ == '__main__':
  app.run(debug=True)
