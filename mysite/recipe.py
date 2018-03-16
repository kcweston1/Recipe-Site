
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template, session, escape, url_for, redirect, flash
import MySQLdb, string, hashlib, secrets, functions, mail, datetime

app = Flask(__name__)

# generate random string for the session's secret key
app.secret_key = b"D>',\xf1\xa0\xdf\x16i\x96\xe5y\xe9\x91@\xf7\x95\xad\xd9P\xbb%\xe9\r"


@app.route('/', methods = ['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signupstatus', methods=['POST'])
def signup_status():
    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    email = request.form.get('email').lower()
    username = request.form.get('uname')
    password = request.form.get('psw')
    confirm_password = request.form.get('confirmpsw')

    if password != confirm_password:
        flash("Passwords did not match")
        return redirect(url_for('signup'))

    cursor.execute('select * from users')
    users = cursor.fetchall()

    if (len(users) > 0):
        for user in users:
            if (user['email'].lower() == email.lower() or user['username'] == username):
                flash("Email/username already in use.")
                return redirect(url_for('signup'))

    #hash the current password here
    salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))
    salted_pass = password + salt
    hex_dig = hashlib.sha256(salted_pass.encode('utf-8')).hexdigest()

    #insert new user into users table
    confirmation_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))
    sql = "insert unconfirmed_users (email, username, passwordhash, salt, confirmationcode) values ('%s', '%s', '%s', '%s', '%s')" % (email, username, hex_dig, salt, confirmation_code)
    #sql = "insert users (email, username, passwordhash, salt, id) values ('%s', '%s', '%s', '%s', %d)" % (email, username, hex_dig, salt, new_id)
    cursor.execute(sql)
    conn.commit()
    conn.close()

    functions.send_confirmation_email(email, confirmation_code)
    flash("Account creation successful!")

    return redirect(url_for('home'))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/processlogin', methods = ['GET', 'POST'])
def loggedin():
    redirect_to = redirect(url_for('login'))
    if request.method == 'POST':


        conn = functions.db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        username = request.form.get('uname')
        password = request.form.get('psw')
        cursor.execute("select * from users")
        conn.close()
        users = cursor.fetchall()
        for user in users:
            if user['username'] == username:
                if functions.check_password(user, password):
                    session['username'] = escape(request.form.get('uname'))
                    session['logged_in'] = True
                    redirect_to = redirect(url_for('home'))
                else:
                    flash('Invalid password')

    return redirect_to


@app.route('/forgotpassword')
def forgotpassword():
    return render_template('forgotpassword.html')

@app.route('/processpasswordreset', methods = ['POST'])
def process_password_reset():
    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    username = request.form.get('username')
    reset_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))
    email = None

    cursor.execute("select * from users")
    users = cursor.fetchall()

    for user in users:
        if username == user['username']:
            email = user['email']
            sql = 'update users set reset_code = "%s", reset_time = CURRENT_TIMESTAMP where username = "%s"' % (reset_code, username)
            cursor.execute(sql)
            functions.send_password_reset_email(email, reset_code)
            conn.commit()
            conn.close()

            flash("Email sent!")
            return redirect(url_for('home'))

    conn.close()
    flash("Username not found!")
    return redirect(url_for('forgotpassword'))


@app.route('/resetpassword', methods = ['GET'])
def reset_password():
    reset_code = request.args.get('code')

    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from users where reset_code = "%s"' % (reset_code))
    user = cursor.fetchall()
    conn.close()

    username = user[0]['username']
    session['usernameforpwreset'] = username
    session['codeforpwreset'] = reset_code

    return render_template('resetpassword.html')


@app.route('/finalizepasswordreset', methods=['GET', 'POST'])
def finalizepasswordreset():
    password = request.form.get('password')
    confirm_password = request.form.get('confirmpassword')
    username = session['usernameforpwreset']
    code = session['codeforpwreset']
    session.pop('usernameforpwreset', None)
    session.pop('codeforpwreset', None)

    if password == confirm_password:
        conn = functions.db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from users where username = "%s"' % (username))
        user = cursor.fetchall()
        print(user)

        if functions.longer_than_one_day(user[0]['reset_time']):
            flash("Password reset has expired. Try again.")
            cursor.execute('update users set reset_time = NULL, reset_code = NULL where username = "%s"' % (username))
            conn.commit()
            conn.close()
            return redirect(url_for('forgotpassword'))
        elif user[0]['reset_code'] == code:
            flash("Password reset successfully")
            salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))
            hashed_pass = functions.hash_password(password, salt)
            cursor.execute('update users set passwordhash = "%s", salt = "%s", reset_code = NULL, reset_time = NULL where username = "%s"' % (hashed_pass, salt, username))
        else:
            flash("Reset code did not match username")

        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        flash("Passwords do not match.")
        return redirect(url_for('resetpassword'))


@app.route('/logout')
def logout():
#remove the username from the session, if it is there.
    session.pop('username', None)
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route('/submitrecipe')
def submit():
    return '''
    <h1>Submit a new recipe</h1>
    <form action='completeSubmission' method='post'>
        Recipe name<br> <input type='text' name='recipeName'></input>
        Prep time<br> <input type='text' name='prepTime'></input>
        Cook time<br> <input type='text' name='cookTime'></input>
        Ingredients<br> <input type='text' name='ingredients'></input>
        Instructions<br> <textarea rows=4 cols=50 name='instructions'></textarea>
        Ingredients<br> <input type='text' name='ingredients'></input>
        Description<br> <textarea rows=4 cols=50 name='description'></textarea>
        Category<br> <input type='text' name='category'></input>
        <input type='submit' name='submit'></input>
    </form>
    '''


@app.route('/confirm', methods=['GET'])
def confirm():
    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('select * from unconfirmed_users')
    users = cursor.fetchall()

    for user in users:
        if user["confirmationcode"] == request.args.get('code'):
            new_id = functions.get_new_id("users", conn, cursor)

            sql = "insert users (email, username, passwordhash, salt, id) values ('%s', '%s', '%s', '%s', %d)" % (user["email"], user["username"], user["passwordhash"], user["salt"], new_id)
            cursor.execute(sql)
            sql = "delete from unconfirmed_users where email = \"%s\"" % (user["email"])
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return '''
            success
            '''
    return '''
    failed for some reason
    '''







