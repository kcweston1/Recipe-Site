
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template
import MySQLdb, string, hashlib, secrets, functions, mail

app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def home():
    login_status = ''
    if request.method == 'POST':
        conn = MySQLdb.connect(host='recipe0.mysql.pythonanywhere-services.com',
                       user='recipe0',
                       passwd='database01',
                       db='recipe0$default')
        cursor = conn.cursor()

        username = request.form.get('uname')
        password = request.form.get('psw')
        cursor.execute("select * from users")
        conn.close()
        users = cursor.fetchall()
        for user in users:
            for data in user:
                if data == username: #email is in db
                    if functions.check_password(user, password):
                        login_status = "login successful!"
                    else:
                        login_status = "login failed!"

    #check if email is in db
    #if yes, check to see that password + user.salt = hashedpassword
    #  by running password + user.salt through hash
    #if no, flash message for invalid login.

    return '''
    <html>
		<title>recipe0 home page</title>
		<body>
		    %s
			<h1>Welcome to recipe0!</h1>

			<p>This is the home page.</p>
			<a href = '/login'>Log in</a></br>
            <a href = '/submitrecipe'>Submit a recipe</a></br>
            <a href='/signup'>Sign up</a></br>
		</body>
	</html>
    ''' % (login_status)


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
    conn = MySQLdb.connect(host='recipe0.mysql.pythonanywhere-services.com',
                       user='recipe0',
                       passwd='database01',
                       db='recipe0$default')
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)  #use dictionary cursor

    email = request.form.get('email').lower()
    username = request.form.get('uname')
    password = request.form.get('psw')
    cursor.execute('select * from users')
    users = cursor.fetchall() #users is currently empty

    print(users)
    for user in users:
        if (user['email'] == email or user['username'].lower() == username.lower()):
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

    #compute the current max userid
    cursor.execute("select MAX(id) from users")
    max_id = cursor.fetchall()
    new_id = max_id[0]['MAX(id)'] + 1

    #insert new user into users table
    sql = "insert users (id, email, username, passwordhash, salt) values (%d, '%s', '%s', '%s', '%s')" % (new_id, email, username, hex_dig, salt)
    cursor.execute(sql)
    conn.commit()
    conn.close()
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

		<form action="/" method="post">
			<label for="uname"><b>Username</b></label>
			<input type="text" placeholder="Enter Username" name="uname" required />

			<label for="psw"><b>Password</b></label>
			<input type="password" placeholder="Enter Password" name="psw" required />

			<button type="submit" name='login'>Login</button>
		</form>
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

@app.route('/testmail', methods=['GET'])
def testmail():
    if request.method == 'GET':
        mail.mail(to='kcweston1@cougars.ccis.edu', subject='test')
    return '''
    <form action='/testmail' method='get'>
        <input type='submit' name='submit'>test mail</input>
    </form>
    '''

