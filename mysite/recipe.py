
# A very simple Flask Hello World app for you to get started with...

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    
    return '''
    <a href = '/login'>Log in</a>
    '''


@app.route('/login')
def login():
    return '''

<html>



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
