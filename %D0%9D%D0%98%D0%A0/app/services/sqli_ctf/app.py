import argparse
from flask import Flask, render_template, request
import os
import sqlite3
import base64

app = Flask(__name__)
DB_FILE = "local.db"  # SQLite файл

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/iusdyfuhu")
def initial():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    );
    ''')

    conn.commit()
    cur.close()
    conn.close()
    return "Table created successfully!!"

@app.route("/register", methods=["POST"])
def register():
    user = request.form.get('user')
    pwd = request.form.get('pass')

    if user == 'admin':
        return render_template("index.html", data="You can't register with admin username")

    if '/static/flag.png' in user:
        user = user.replace("flag.png", "flag2.png")

    user = user.replace("=", "").replace("/", "").replace(";", "")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
    conn.commit()
    cur.close()
    conn.close()

    return render_template("index.html", data="Registered successfully !")

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user")
    pwd = request.form.get("pass")

    if '/static/flag.png' in user:
        user = user.replace("flag.png", "flag2.png")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        t = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

        if t:
            t = t[0]
            if str(t[1]) == 'admin':
                return '''
<center>
<h1> WELCOME ADMIN </h1>
<br><br>
<h3>
You know Admin has higher privileges ! so in this application, admin is given access to the remote sql editor !
<br><br>
!! CLICK THE BELOW BUTTON !!
</h3>
<br><br>
<a href="/sqleditor"><button>SQL EDITOR</button></a>
</center>
'''
            else:
                return "Hello " + str(t[1])
        else:
            return render_template("index.html", data="Invalid Login/Password !!")

    except Exception as e:
        return render_template("index.html", data="Invalid Login/Password !!")

@app.route("/static/flag.png")
def forbide():
    return '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
'''

@app.route("/sqleditor")
def editor():
    return '''
<center>
<h1>SQL Editor</h1>
<br><br>
<form action="output" method="post">
<textarea name="sql" rows="15" cols="60">
Enter query here
</textarea>
<br><br><br>
<input type=submit value="Execute">
</form>
</center>
'''

@app.route("/output", methods=["POST"])
def creator():
    code = request.form.get('sql')
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    res = ''

    try:
        if any(op in code.lower() for op in ['insert', 'delete', 'update']):
            cur.execute(code)
            conn.commit()
            cur.close()
            conn.close()
            return "Insertion/Deletion/Updation of data successful !!"
        else:
            cur.execute(code)
            t = cur.fetchall()
    except Exception as e:
        return "Some Error occurred in your SQL code : " + str(e)

    for row in t:
        res += str(row) + "<br>"

    conn.commit()
    cur.close()
    conn.close()
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9002)
    args = parser.parse_args()
    app.run(port=args.port)
