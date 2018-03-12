
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template, session
import MySQLdb, string, hashlib, secrets, functions, mail

app = Flask(__name__)

# generate random string for the session's secret key
app.secret_key = 'randomstring'


@app.route('/', methods = ['GET', 'POST'])
def home():
    usernametext = ''
    loginout = ''
    if 'username' in session:
        sessionusername = session['username']
        usernametext = 'Logged in as ' + sessionusername + '.'
        loginout = "<a href = '/logout'>Log out</a></br>"
    else:
        usernametext = 'Not logged in'
        loginout = "<a href = '/login'>Log in</a></br>"

    #check if email is in db
    #if yes, check to see that password + user.salt = hashedpassword
    #  by running password + user.salt through hash
    #if no, flash message for invalid login.

    return '''
    <html>
		<title>recipe0 home page</title>
		<body>
            <p>%s</p>
			<h1>Welcome to recipe0!</h1>

			<p>This is the home page.</p>
            %s
            <a href = '/submitrecipe'>Submit a recipe</a></br>
            <a href='/signup'>Sign up</a></br>
		</body>
	</html>
    ''' % (usernametext, loginout)


@app.route('/signup')
def signup():
    return '''
<html>
    <title>recipe0 account creator</title>
    <body>
        <h1>Create an account on recipe0</h1>
        <form action = '/signupstatus' method='post'>
            Email <input type='text' name='email' required/>
            Username <input type='text' name='uname' required />
            Password <input type='password' name='psw' required />
            <button type='submit' name='signup'>Create account</button>
        </form>
    </body>
</html>
    '''

@app.route('/signupstatus', methods=['POST'])
def signup_status():
    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    email = request.form.get('email').lower()
    username = request.form.get('uname')
    password = request.form.get('psw')
    cursor.execute('select * from users')
    users = cursor.fetchall()

    if (len(users) > 0):
        for user in users:
            if (user['email'].lower() == email.lower() or user['username'] == username):
                return '''
                <html>
                    Email/username already in use!
                    <a href='/signup'>Return to signup</a>
                </html>
                '''
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

    return '''
    <html>
        Account creation successful!
        <a href='/login'>Click here to log in</a>
    </html>
    '''


@app.route('/login')
def login():
    return '''

<html>
	<title>recipe0 login page</title>
	<body>
		<h1>Login to recipe0!</h1>

		<p>This is the login page.</p>

		<form action="/loggedin" method="post">
			<label for="uname"><b>Username</b></label>
			<input type="text" placeholder="Enter Username" name="uname" required />

			<label for="psw"><b>Password</b></label>
			<input type="password" placeholder="Enter Password" name="psw" required />

			<button type="submit" name='login'>Login</button>
		</form>
	</body>



</html>

    '''

@app.route('/loggedin', methods = ['GET', 'POST'])
def loggedin():
    login_status = ''
    if request.method == 'POST':
        session['username'] = request.form.get('uname')

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
                    login_status = "login successful!"
                else:
                    login_status = "login failed!"

    usernametext = ''
    if 'username' in session:
        sessionusername = session['username']
        usernametext = 'Logged in as ' + sessionusername + '.'
    else:
        usernametext = 'Not logged in'

    return '''
    <html>
		<title>recipe0 home page</title>
		<body>

		    <p>%s</p>
            <p>%s</p>
			<h1>You landed on the post-login page!</h1>

			<a href = '/'>Go to home page</a></br>
            <a href = '/submitrecipe'>Submit a recipe</a></br>
		</body>
	</html>
    ''' % (login_status, usernametext)

@app.route('/logout')
def logout():
#remove the username from the session, if it is there.
    session.pop('username', None)
    return '''
    <html>
        <title>Logout</title>
        <body>
            <h2>Logged out.</h2>
            <a href = '/'>Go to home page</a></br>
            <a href = '/login'>Log in</a></br>
        </body>
    </html>
    '''

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

@app.route('/confirm', methods=["GET", "POST"])
def confirm():
    if request.method == "POST":
        conn = functions.db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        email = request.form.get('email').lower()
        confirmation = request.form.get('confirmation')
        cursor.execute('select * from unconfirmed_users')
        users = cursor.fetchall()

        for user in users:
            if user["email"] == email:
                if user["confirmationcode"] == confirmation:
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

    else:
        return '''
<html>
    <h1>Confirm your account</h1>
    <form action='confirm' method='post'>
        email <input type='text' name='email' required />
        Confirmation Code <input type='text' name='confirmation' required />
        <button type='submit' name='submit'></button>
    </form>
</html>
'''


#@app.route('/testconfirm', methods=['GET'])
#    conn = functions.db_connect()
#    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

#    cursor.execute('select * from unconfirmed_users')
#        users = cursor.fetchall()









