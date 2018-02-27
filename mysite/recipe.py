
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



</html>

    '''
