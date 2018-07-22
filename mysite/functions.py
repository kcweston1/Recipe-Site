import MySQLdb, hashlib, mail, datetime, random
from operator import itemgetter

def check_password(user, password):
    hashed_pass = hash_password(password, user['salt'])
    return (hashed_pass == user['passwordhash'])


def hash_password(password, salt):
    salted_pass = password + salt
    hex_dig = hashlib.sha256(salted_pass.encode('utf-8')).hexdigest()
    return hex_dig


def db_connect():
    return MySQLdb.connect(host='recipe0.mysql.pythonanywhere-services.com',
                               user='recipe0',
                               passwd='database01',
                               db='recipe0$default')


#get_new_id returns the id (primary key) of the next row to be inserted
#into the given table
def get_new_id(table, conn, cursor):
    sql = "select * from %s" % (table)
    cursor.execute(sql)
    if (len(cursor.fetchall()) == 0):
        new_id = 0
    else:
        sql = "select MAX(id) from %s" % (table)
        cursor.execute(sql)
        max_id = cursor.fetchall()
        new_id = max_id[0]['MAX(id)'] + 1
    return new_id


def send_confirmation_email(email, confirmation_code):
    link = 'http://recipe0.pythonanywhere.com/confirm?code=%s' % (confirmation_code)
    text = '''Thank you for creating an account on Recipe Site.\n
              Click the following link to confirm your account:\n%s''' % (link)
    mail.mail(to=email, subject="[Recipe Site] Confirm Account Creation", text=text)


def send_password_reset_email(email, reset_code):
    link = 'http://recipe0.pythonanywhere.com/resetpassword?code=%s' % (reset_code)
    text = '''Use this link to reset your password.\n
              It will expire in 24 hours.\n %s''' % (link)
    mail.mail(to=email, subject="[Recipe Site] Reset Password", text=text)


def longer_than_one_day(reset_time):
    expire_time = reset_time + datetime.timedelta(days=1)
    return datetime.datetime.now() > expire_time

#returns bool
def recipe_exists(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from recipes where id = %s" % (recipe_id))
    recipe = cursor.fetchall()
    conn.close()
    return (len(recipe) == 1)


def get_random_recipe():
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from recipes")
    recipes = cursor.fetchall()
    random_recipe = random.choice(recipes)
    return random_recipe


#returns a list of recipe dictionaries
def get_all_recipes(sort_by):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    recipes = []
    order_by = "name"
    if sort_by == "date":
        order_by = "id"

    cursor.execute("select * from recipes order by %s" % (order_by))
    recipes = cursor.fetchall()
    conn.close()
    if sort_by == "score":
        recipes = sort_recipes_by_score(recipes)
    return recipes


def sort_recipes_by_likes(recipes): #THIS IS TRAAAAAAAAAAASHHHHHHHHHHHHH!!!!!!!!!!!!!!!!!!!!!!!! USE JOOOOOOOOOOOOOOOOOOOOIIIIIIIINNNNNNNNNNNSSSSSSSSSSSSSSSS
    for recipe in recipes:
        recipe['likes'] = get_num_likes(recipe['id'])
    sorted_recipes = sorted(recipes, key=itemgetter('likes', 'id'), reverse=True)
    return sorted_recipes

def sort_recipes_by_score(recipes): #THIS IS TRAAAAAAAAAAASHHHHHHHHHHHHH!!!!!!!!!!!!!!!!!!!!!!!! USE JOOOOOOOOOOOOOOOOOOOOIIIIIIIINNNNNNNNNNNSSSSSSSSSSSSSSSS
    for recipe in recipes:
        recipe['score'] = get_score(recipe['id'])
    sorted_recipes = sorted(recipes, key=itemgetter('score', 'id'), reverse=True)
    return sorted_recipes



#returns a recipe dictionary
def get_recipe_by_id(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    sql = "select * from recipes where id = %s" % (recipe_id)
    cursor.execute(sql)
    recipe = cursor.fetchall()[0]
    conn.close()
    return recipe


#returns a list of comment dictionaries
def get_comments(recipe_id): #UNTESTED !!!!!!!!!!!
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from comments where recipe = %s" % (recipe_id))
    comments = cursor.fetchall()
    for comment in comments:
        cursor.execute("select username from users where id = %s" % (comment['user']))
        comment['username'] = cursor.fetchall()[0]['username']
    conn.close()
    return comments


#returns a string
def get_username(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select creatorid from recipes where id = %s" % (recipe_id))
    uid = cursor.fetchall()[0]['creatorid']
    cursor.execute("select username from users where id = %s" % (uid))
    username = cursor.fetchall()[0]['username']
    conn.close()
    return username


def get_username_by_id(user_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select username from users where id = %s" % (user_id))
    username = cursor.fetchall()[0]['username']
    conn.close()
    return username

#returns a list of strings
def get_ingredients(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select ingredient from recipe_ingredients where recipe = %s" % (recipe_id))
    ingredient_ids = cursor.fetchall()
    ingredient_list = []
    for id in ingredient_ids:
        cursor.execute("select name from ingredients where id = %s" % (id['ingredient']))
        ingredient_list.append(cursor.fetchall()[0]['name'])
    conn.close()
    return ingredient_list


#returns a list of instruction dictionaries
def get_instructions(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from instructions where recipe = %s order by instructionnumber" % (recipe_id))
    instructions = cursor.fetchall()
    conn.close()
    return instructions

#returns a string
def get_category(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select category from recipes where id = %s" % (recipe_id))
    cid = cursor.fetchall()[0]['category']
    cursor.execute("select name from categories where id = %s" % (cid))
    category_name = cursor.fetchall()[0]['name']
    conn.close()
    return category_name


def get_category_name_by_id(category_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select name from categories where id = %s" % (category_id))
    category = cursor.fetchall()
    name = None
    if len(category) > 0:
        name = category[0]['name']
    return name


def get_id_of_username(username):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from users where username = "%s"' % (username))
    userid = cursor.fetchall()[0]['id']
    conn.close()
    return userid

def insert_like(user_id, recipe_id):
    if dislike_exists(user_id, recipe_id):
        conn = db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE likes SET islike = %s WHERE user = %s and recipe = %s" % (1, user_id, recipe_id))
        conn.commit()
        conn.close()
    else:
        conn = db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO likes (user, recipe, islike) VALUES (%s, %s, %s)" % (user_id, recipe_id, 1))
        conn.commit()
        conn.close()

def insert_dislike(user_id, recipe_id):
    if like_exists(user_id, recipe_id):
        conn = db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE likes SET islike = %s WHERE user = %s and recipe = %s" % (0, user_id, recipe_id))
        conn.commit()
        conn.close()
    else:
        conn = db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO likes (user, recipe, islike) VALUES (%s, %s, %s)" % (user_id, recipe_id, 0))
        conn.commit()
        conn.close()

def delete_like(user_id, recipe_id):
    if like_exists(user_id, recipe_id) or dislike_exists(user_id, recipe_id):
        conn = db_connect()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM likes WHERE user = %s and recipe = %s" % (user_id, recipe_id))
        conn.commit()
        conn.close()

def like_exists(user_id, recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from likes where user = %s and recipe = %s and islike = %s" % (user_id, recipe_id, 1))
    like = cursor.fetchall()
    conn.close()
    return (len(like) >= 1)

def dislike_exists(user_id, recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from likes where user = %s and recipe = %s and islike = %s" % (user_id, recipe_id, 0))
    like = cursor.fetchall()
    conn.close()
    return (len(like) >= 1)

def get_num_likes(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) FROM likes WHERE recipe = %s" % (recipe_id))
    num_likes = cursor.fetchall()
    conn.close()
    if len(num_likes) > 0:
        return (num_likes[0]['COUNT(*)'])
    return 0

def get_score(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) FROM likes WHERE recipe = %s and islike = 1" % (recipe_id))
    num_likes = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE recipe = %s and islike = 0" % (recipe_id))
    num_dislikes = cursor.fetchall()

    if len(num_likes) > 0:
        num_likes = num_likes[0]['COUNT(*)']
    else:
        num_likes = 0

    if len(num_dislikes) > 0:
        num_dislikes = num_dislikes[0]['COUNT(*)']
    else:
        num_dislikes = 0

    conn.close()
    return num_likes - num_dislikes

def get_search_results(search_term, option):
    if option == "recipes":
        results = search_by_recipe_name(search_term)
    elif option == "categories":
        results = search_by_category(search_term)
    else:
        results = search_by_ingredient(search_term)
    return results


def search_by_recipe_name(search_term):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from recipes where name LIKE "%s" order by name' % ('%' + search_term + '%'))
    results = cursor.fetchall()
    conn.close()
    return results


def search_by_category(search_term):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from categories where name LIKE "%s"' % ('%' + search_term + '%'))
    results = cursor.fetchall()
    if (len(results) == 1):
        category_id = results[0]['id']
        cursor.execute('select * from recipes where category = %s order by name' % (category_id))
        results = cursor.fetchall()
    conn.close()
    return results


def search_by_ingredient(search_term):
    recipe_list = []
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select * from ingredients where name = "%s"' % (search_term))
    results = cursor.fetchall()
    if (len(results) == 1):
        ingredient_id = results[0]['id']
        cursor.execute('select recipe from recipe_ingredients where ingredient = %s' % (ingredient_id))
        recipe_ids = cursor.fetchall()
        print(recipe_ids)
        for recipe in recipe_ids:
            recipe_list.append(get_recipe_by_id(recipe['recipe']))
    return recipe_list


#returns a list of recipe dictionaries I think?
def get_recipes_of_user(user_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    sql = "select * from recipes where creatorid = %s" % (user_id)
    cursor.execute(sql)
    recipes = cursor.fetchall()
    conn.close()
    return recipes

#pass in string to check if the string is already in use
#returns true if such a record exists, false otherwise
def username_exists(username):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from users where username = '%s'" % (username))
    uname = cursor.fetchall()
    conn.close()
    return (len(uname) >= 1)

def get_likes_of_user(user_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    sql = "SELECT recipes.id, recipes.name, recipes.category, recipes.description, likes.user, likes.recipe, likes.islike " + \
            "FROM recipes INNER JOIN likes ON recipes.id=likes.recipe " + \
            "WHERE user = %s and islike = 1" % (user_id)

    cursor.execute(sql)

    recipes = cursor.fetchall()
    conn.close()
    return recipes


def save_comment(recipe_id, user_id, comment_text):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    new_id = get_new_id("comments", conn, cursor)
    sanitized_comment = sanitize(comment_text)
    cursor.execute('insert comments (id, user, recipe, comment) values (%s, %s, %s, "%s")' % (new_id, user_id, recipe_id, sanitized_comment))
    conn.commit()
    conn.close()

def sanitize(input_string):
    output_string = ''
    for i in input_string:
        if i == '"':
            output_string += '\\'
        output_string += i
    return output_string

def delete_recipe(recipe_id):
    conn = db_connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    #delete likes
    cursor.execute("DELETE FROM likes WHERE recipe = %s" % (recipe_id))

    #delete comments
    cursor.execute("DELETE FROM comments WHERE recipe = %s" % (recipe_id))

    #delete instructions
    cursor.execute("DELETE FROM instructions WHERE recipe = %s" % (recipe_id))

    #handle category

    #handle ingredients
    cursor.execute("DELETE FROM recipe_ingredients WHERE recipe = %s" % (recipe_id))


    #delete recipe
    cursor.execute("DELETE FROM recipes WHERE id = %s" % (recipe_id))


    conn.commit()
    conn.close()