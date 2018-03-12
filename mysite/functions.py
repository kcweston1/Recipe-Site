import MySQLdb, hashlib, mail

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
    link = 'http://recipe0.pythonanywhere.com/confirm'
    text = "Thank you for creating an account on Recipe Site.\nYour confirmation code is %s\nClick the following link to confirm your account:\n%s" % (confirmation_code, link)
    mail.mail(to=email, subject="[Recipe Site] Confirm Account Creation", text=text)