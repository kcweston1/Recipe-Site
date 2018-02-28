
# A very simple Flask Hello World app for you to get started with...

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''

<html>
	<title>recipe0 home page</title>
	<body>
		<h1>Welcome to recipe0!</h1>

		<p>This is the home page.</p>
	</body>
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

		<form action="/">

		<div class="container">
			<label for="uname"><b>Username</b></label>
			<input type="text" placeholder="Enter Username" name="uname" required>

			<label for="psw"><b>Password</b></label>
			<input type="password" placeholder="Enter Password" name="psw" required>

			<button type="submit">Login</button>
		  </div>

		  <div class="container" style="background-color:#f1f1f1">
			<button type="button" class="cancelbtn">Cancel</button>
			<span class="psw">Forgot <a href="#">password?</a></span>
		  </div>
		</form>
	</body>



</html>

    '''
