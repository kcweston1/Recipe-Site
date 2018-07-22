
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template, session, escape, url_for, redirect, flash
import MySQLdb, string, hashlib, secrets, functions

app = Flask(__name__)

# generate random string for the session's secret key
app.secret_key = b"D>',\xf1\xa0\xdf\x16i\x96\xe5y\xe9\x91@\xf7\x95\xad\xd9P\xbb%\xe9\r"


@app.route('/', methods = ['GET', 'POST'])
def home():
    random_recipe = functions.get_random_recipe()
    return render_template('home.html', random_recipe=random_recipe)


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
    flash("Check your email for the confirmation code!")

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
    if 'logged_in' in session.keys():
        if session['logged_in'] == True:
            return render_template('submitrecipe.html')
    flash("You must be logged in to create a recipe")
    return redirect(url_for('login'))


@app.route('/completesubmission', methods=['POST'])
def completesubmission():
    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    new_recipe_id = functions.get_new_id('recipes', conn, cursor)
    cursor.execute('select * from users where username = "%s"' % (session['username']))
    userid = cursor.fetchall()[0]['id']

    #check to see if name is taken
    cursor.execute('select * from recipes where name = "%s"' % (request.form.get('recipeName')))
    if (len(cursor.fetchall()) > 0):
        flash("That recipe name is already in use.")
        return redirect(url_for('submit'))

    #deal with categories (if we predefine categories, we can take this out)
    category = request.form.get("category")
    cursor.execute('select * from categories where name = "%s"' % (category))
    categories = cursor.fetchall()
    if (len(categories) == 0):
        category_id = functions.get_new_id('categories', conn, cursor)
        cursor.execute('''insert categories (id, name)
                          values (%s, "%s")''' % (category_id, category))
    else:
        category_id = categories[0]['id']


    #build record for recipe
    name = request.form.get("recipeName")
    prep_time = request.form.get("prepTime")
    cook_time = request.form.get("cookTime")
    description = request.form.get("description")

    cursor.execute('''insert recipes (id, name, preptime, cooktime,
                      category, creatorid, description)
                      values (%s, "%s", %s, %s, "%s", %s, "%s")
                      ''' % (new_recipe_id, name, prep_time, cook_time, category_id, userid, description))

    #build ingredients tables
    ingredient_counter = request.form.get('ingredientCounter')
    for i in range(0, int(ingredient_counter)):
        #make this a new function
        ingredient = request.form.get("ingredients[" + str(i) + "]")
        cursor.execute('select * from ingredients where name = "%s"' % (ingredient))
        matching_ingredient = cursor.fetchall()
        if (len(matching_ingredient) == 0): #create new ingredient record
            ingredient_id = functions.get_new_id('ingredients', conn, cursor)
            cursor.execute('''insert ingredients (id, name)
                              values (%s, "%s")''' % (ingredient_id, ingredient))
        else: #ingredient already exists
            ingredient_id = matching_ingredient[0]['id']
        cursor.execute('insert recipe_ingredients (recipe, ingredient) values (%s, %s)' % (new_recipe_id, ingredient_id))

    #build instructions table
    instructions_counter = request.form.get('instructionCounter')
    for i in range(0, int(instructions_counter)):
        instruction = request.form.get("instructions[" + str(i) + "]")
        cursor.execute('''insert instructions (recipe, instructionnumber, instruction)
                          values (%s, %s, "%s")''' % (new_recipe_id, i, instruction))


    conn.commit()
    conn.close()

    #eventually route user to the newly created recipe page
    return redirect(url_for('recipes') + "?id=%s" % (new_recipe_id))


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    id = request.args.get('id')
    if functions.recipe_exists(id):
        score = functions.get_score(id)
        recipe = functions.get_recipe_by_id(id)
        creator = functions.get_username(id)
        category = functions.get_category(id)
        ingredients = functions.get_ingredients(id)
        instructions = functions.get_instructions(id)
        comments = functions.get_comments(id)
        user_logged_in = False
        current_user_is_creator = False
        likeexists = False
        dislikeexists = False
        if 'logged_in' in session.keys() and session['logged_in'] == True:
            user_logged_in = True
            current_user_is_creator = (session['username'] == creator)
            likeexists = functions.like_exists(functions.get_id_of_username(session['username']), id)
            dislikeexists = functions.dislike_exists(functions.get_id_of_username(session['username']), id)
        return render_template('recipes.html', score=score, likeexists=likeexists, dislikeexists=dislikeexists, current_user_is_creator=current_user_is_creator, recipe=recipe, creator=creator, category=category, ingredients=ingredients, instructions=instructions, comments=comments, user_logged_in=user_logged_in)
    else:
        flash("Recipe not found.")
        return url_for('recipe_list')


@app.route('/editrecipe', methods=['POST'])
def edit_recipe():
    return "hello"


@app.route('/recipe_list', methods=['GET', 'POST'])
def recipe_list():
    sort_by = 'alpha'
    if request.method == "POST":
        sort_by = request.form.get("sortBy")
    recipes = functions.get_all_recipes(sort_by);
    for recipe in recipes:
        recipe['category_name'] = functions.get_category_name_by_id(recipe['category'])
        recipe['score'] = functions.get_score(recipe['id'])
    return render_template('recipe_list.html', recipes=recipes, sort_by=sort_by)

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == "POST":
        search_term = request.form.get('term')
        option = request.form.get('option')
        results = functions.get_search_results(search_term, option)
        if len(results) == 0:
            flash("No results found!")
    return render_template('search.html', results=results)

@app.route('/process_like', methods=['GET', 'POST'])
def process_like():
    if 'logged_in' in session.keys() and session['logged_in'] == True:
        recipe_id = request.args.get('id')
        user_id = functions.get_id_of_username(session['username'])
        if (functions.recipe_exists(recipe_id)) and (not functions.like_exists(user_id, recipe_id)):
            functions.insert_like(user_id, recipe_id)
            flash("Liked!")
        else:
            flash("Recipe not found or user already liked this recipe")
    else:
        flash("Not logged in!")

    return redirect(url_for('recipes') + "?id=%s" % (recipe_id))

@app.route('/process_dislike', methods=['GET', 'POST'])
def process_dislike():
    if 'logged_in' in session.keys() and session['logged_in'] == True:
        recipe_id = request.args.get('id')
        user_id = functions.get_id_of_username(session['username'])
        if (functions.recipe_exists(recipe_id)) and (not functions.dislike_exists(user_id, recipe_id)):
            functions.insert_dislike(user_id, recipe_id)
            flash("Disliked!")
        else:
            flash("Recipe not found or user already disliked this recipe")
    else:
        flash("Not logged in!")

    return redirect(url_for('recipes') + "?id=%s" % (recipe_id))

@app.route('/delete_like', methods=['GET', 'POST'])
def delete_like():
    if 'logged_in' in session.keys() and session['logged_in'] == True:
        recipe_id = request.args.get('id')
        user_id = functions.get_id_of_username(session['username'])
        if functions.recipe_exists(recipe_id):
            functions.delete_like(user_id, recipe_id)
            flash("Opinion obliterated!")
        else:
            flash("Recipe not found or user did not like this recipe")
    else:
        flash("Not logged in!")

    return redirect(url_for('recipes') + "?id=%s" % (recipe_id))


@app.route('/process_comment', methods=['GET', 'POST'])
def process_comment():
    if request.method == 'POST':
        recipe_id = request.args.get('id')
        user_id = functions.get_id_of_username(session['username'])
        comment_text = request.form.get('commentfield')
        functions.save_comment(recipe_id, user_id, comment_text)
        flash("Comment successful!")
        return redirect(url_for('recipes') + "?id=%s" % (recipe_id) + "#comments" )
    else:
        flash("How did you get here?")
        return redirect(url_for('recipe_list'))

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
            flash("Account confirmed successfully!")
            return redirect(url_for('home'))
    conn.close()
    flash("Something went wrong with your account confirmation.")
    return redirect(url_for('home'))

@app.route('/editpicture', methods=['POST'])
def edit_picture():
    recipe_id = request.form.get('recipeID')
    url = request.form.get('pictureURL')
    print(recipe_id)
    print(url)
    conn = functions.db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('update recipes set picture = "%s" where id = %s' % (url, recipe_id))
    conn.commit()
    conn.close()
    return redirect(url_for('recipes') + "?id=" + recipe_id)




@app.route('/user', methods=['GET', 'POST'])
def user():
    uname = request.args.get('uname')

    if not functions.username_exists(uname):
        flash('User not found!')
        return redirect(url_for('home'))

    user_id = functions.get_id_of_username(uname)

    recipes = functions.get_recipes_of_user(user_id)
    for recipe in recipes:
        recipe['category_name'] = functions.get_category_name_by_id(recipe['category'])
        recipe['score'] = functions.get_score(recipe['id'])

    # TODO: add sorting
    '''
    sort_by = 'alpha'
    if request.method == "POST":
        sort_by = request.form.get("sortBy")
    recipes = functions.get_all_recipes(sort_by);
    '''

    likedrecipes = functions.get_likes_of_user(user_id)
    for recipe in likedrecipes:
        recipe['category_name'] = functions.get_category_name_by_id(recipe['category'])
        recipe['score'] = functions.get_score(recipe['id'])




    if 'logged_in' in session.keys() and session['logged_in'] == True:
        if (session['username'] == uname):
            0
    return render_template('user.html', uname=uname, recipes=recipes, likedrecipes=likedrecipes)


@app.route('/delete_recipe', methods=['GET', 'POST'])
def delete_recipe():
    if 'logged_in' in session.keys() and session['logged_in'] == True:
        recipe_id = request.args.get('id')
        if (functions.get_username(recipe_id) == session['username']):
            if functions.recipe_exists(recipe_id):
                functions.delete_recipe(recipe_id)
                flash("Recipe deleted!")
            else:
                flash("Recipe not found!")
        else:
            flash("Username does not match!")
    else:
        flash("Not logged in!")

    return redirect(url_for('recipe_list'))
