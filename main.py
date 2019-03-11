from urllib.parse import urlparse
import os, sqlite3, requests, hashlib, datetime, json
from user import User
from admin import Admin
from flask import Flask, jsonify, session, request, render_template, redirect, url_for, Response

app = Flask(__name__)

questions = []
data = []
score = 0

@app.route('/')
def main():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))

    username = session.get('username')
    user = User.find_by_username(username)

    return render_template("index.html", user=user), 200

@app.route('/test', methods=['GET', 'POST'])
def test():
    global score, data  #   get global variables

    # Check if user is logged in
    if not session.get('loggedIn'):
        return redirect(url_for('login'))

    # Check if post data was submitted, compare option chosen to the answer and increment score if true
    if request.method == "POST":
        choice = request.form['options']
        answer = request.form['answer']
        username = session.get('username')
        user = User.find_by_username(username)
        if choice == answer:
            score += 1

    # populate the data list if empty with the questions from file
    if not data:
        if open("questions.txt", "r"):
            for question in open("questions.txt", "r"):
                data.append(json.loads(question))

    id = request.args.get('id', type=int)   # get the id parameter for question index

    if id >= len(data) + 1: # check for end of questions in the data list
        return redirect(url_for('results'))
    else:
        q = data[id-1]
        sn = id
        id += 1

    return render_template('quiz.html', q=q, id=id, sn=sn), 200


@app.route('/results')
def results():
    global score
    if not session.get('loggedIn'):
        return redirect(url_for('login'))

    try:
        username = session.get("username")
        status = 1
        score = score
        percentage = (score/len(data)) * 100
        user = User()
        user.update(username, status, percentage)
        student = user.find_by_username(username)
        return render_template("results.html", user=student, percentage=int(percentage))
    except:
        return redirect(url_for('main'))

@app.route('/admin/view')
def viewQuestions():
    global data
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    if not data:
        for question in open("questions.txt", "r"):
            data.append(json.loads(question))

    return render_template("view_questions.html", questions=data)

@app.route('/admin/students')
def viewStudents():
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    data = User.find_all()
    return render_template("view_students.html", data=data)

@app.route('/admin/post', methods=['GET','POST'])
def postQuestion():
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    if request.method == 'POST':
        text = request.form['question']
        ans_a = request.form['ans_a']
        ans_b = request.form['ans_b']
        ans_c = request.form['ans_c']
        ans_d = request.form['ans_d']
        answer = request.form['answer']

        data = {
            "text": text,
            "options": [ans_a, ans_b, ans_c, ans_d],
            "answer": answer
        }

        questions.append(data)
        with open("questions.txt", "a") as qfile:
            qfile.write(json.dumps(data) + '\n')

        return render_template('add_question.html'), 201
    else:
        return render_template('add_question.html'), 200

@app.route('/logout')
def logout():
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    session['loggedIn'] = False
    return redirect(url_for('login', loggedout = "true"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('loggedIn'):
        return redirect(url_for('main')) # redirect to the blockchain page if already logged in

    messages = ""
    if request.method == "GET":
        if request.args.get('loggedout'):
            messages = "You have been logged out!"
        elif request.args.get('loginerror'):
            messages = "Email & Password combination is incorrect, try again!"
    elif request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        _password = hashlib.sha256(_password.encode()).hexdigest()

        user = User()
        response = user.login(username=_username, password=_password)
        if response:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=5)
            session['loggedIn'] = True
            session['username'] = _username
            return redirect(url_for("main"))
        else:
            return redirect(url_for("login", loginerror=True))

    return render_template('login.html', data = messages), 200


@app.route('/register', methods=['GET', 'POST'])
def signup():
    if session.get('loggedIn'):
        return redirect(url_for('main')) # redirect to the blockchain page if already logged in

    if (request.method == 'POST'):
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()

        user = User()
        response = user.register(firstname, lastname, email, username, password)

        return render_template('register.html', data=response), 201

    return render_template('register.html'), 200


@app.route('/admin')
def admin_page():
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    return render_template("admin_index.html"), 200

@app.route('/admin/login', methods=['GET', 'POST'])
def adminLogin():
    if session.get('loggedIn'):
        return redirect(url_for('main')) # redirect to the blockchain page if already logged in

    messages = ""
    if request.method == "GET":
        if request.args.get('loggedout'):
            messages = "You have been logged out!"
        elif request.args.get('loginerror'):
            messages = "Username & Password combination is incorrect, try again!"
    elif request.method == "POST":
        admin_username = request.form['username']
        admin_password = request.form['password']
        admin_password = hashlib.sha256(admin_password.encode()).hexdigest()

        admin = Admin()
        response = admin.login_admin(username=admin_username, password=admin_password)
        if response:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=5)
            session['adminLogin'] = True
            session['adminUsername'] = admin_username
            return redirect(url_for('admin_page', username=admin_username))
        else:
            return redirect(url_for("adminLogin", loginerror=True))

    return render_template('admin_login.html', data = messages), 200


@app.route('/admin/register', methods = ['GET','POST'])
def adminRegistration():
    if session.get('adminLogin'):
        return redirect(url_for('admin_page')) # redirect to the blockchain page if already logged in

    if (request.method == 'POST'):
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()

        admin = Admin()
        response = admin.register_admin(firstname, lastname, email, username, password)

        return render_template('admin_register.html', data=response), 201

    return render_template('admin_register.html'), 200



if __name__ == '__main__':
    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    app.run(port=5000, debug=True)
