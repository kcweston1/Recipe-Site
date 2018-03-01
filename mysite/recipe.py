
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
    	<a href = '/login'>Log in</a>
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

		<form action="/" method="post">
			<div class="container">
				<label for="uname"><b>Username</b></label>
				<input type="text" placeholder="Enter Username" name="uname" required>

				<label for="psw"><b>Password</b></label>
				<input type="password" placeholder="Enter Password" name="psw" required>

				<button type="submit">Login</button>
			</div>
		</form>
	</body>



</html>

    '''

@app.route('/submitRecipe')
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
