import mysql.connector
from Crypto.PublicKey import RSA
from Crypto.Cipher import  PKCS1_OAEP
from datetime import datetime

# connecting to local host 
db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = 'satyam17',
    database = 'ProjectOne'
)


mycursor = db.cursor()

# intial setup + quick changes

#Q1 = "CREATE TABLE users (user_id int PRIMARY KEY AUTO_INCREMENT, first_name VARCHAR(50), last_name VARCHAR(50), password VARCHAR(50), public_key VARCHAR(50))"
#Q2 = "CREATE TABLE private (user_id int PRIMARY KEY, FOREIGN KEY(user_ID) REFERENCES users(user_id), private_key VARCHAR(50))"
#Q3 = "CREATE TABLE passwords (pass_id int PRIMARY KEY AUTO_INCREMENT, user_id int, name VARCHAR(50), encrpyted_password VARCHAR(50))"
#mycursor.execute("ALTER TABLE passwords CHANGE date date DATETIME")  

#mycursor.execute("ALTER TABLE private ADD CONSTRAINT private_foreign FOREIGN KEY(user_ID) REFERENCES users(user_id) ON DELETE CASCADE")       #changing the size can return error if the size is smaller then currently used

#mycursor.execute(Q3)

'''
Tables Setup:

Users:
______________________________________________________
Primary Key: user_id int (AI)
first_name VARCHAR(50)
last_name VARCHAR(50)
password VARCHAR(50)
public_key VARCHAR(50)

Private:
______________________________________________________
Primary Key + Foreign Key: user_id int
private_key VARCHAR(1050)


Passwords:
______________________________________________________
Primary Key: pass_id int (AI)
Foreign Key: user_id int
name VARCHAR(50)
encrpyted_password VARBINARY(500)


'''


def create_user (first, last, email, password):
    # create the queries responsible for setting up the insert into the tables
    Q1 = "INSERT INTO users(first_name, last_name, email, password, public_key) VALUES (%s, %s, %s, %s, %s)"
    Q2 = "INSERT INTO private(user_id, private_key) VALUES (%s, %s)"

    # generate the key
    key = RSA.generate(1024)
    privatekey = key.export_key()
    publicKey = key.publickey().export_key()

    # execute the INSERT query and pass the appropriate paramaters
    mycursor.execute(Q1, (first, last, email, password, publicKey))
    last_id = mycursor.lastrowid
    mycursor.execute(Q2, (last_id, privatekey))

    # commit changes to table(s)
    db.commit()

def add_password(id, name, password):
    # create the query responsible for setting up the insert into the tables
    Q1 = "INSERT INTO passwords(user_id, name, encrpyted_password, date) VALUES (%s, %s, %s, %s)"

    # create the query responsible for setting up the insert into the tables
    Q2 = "UPDATE passwords SET encrpyted_password = %s, date = %s WHERE user_id = %s AND name = %s"
    
    # query to check if a password for the user and site/app name already exsits
    Q3 = "SELECT count(*) FROM passwords WHERE user_id = %s AND name = %s"

    # get the public key to encrpy the password 

    Q4 = "SELECT public_key FROM users WHERE user_id = %s"
    mycursor.execute(Q4, (id,))
    public_key = RSA.import_key(mycursor.fetchone()[0])

    encryptor = PKCS1_OAEP.new(public_key)

    encrpyted_password = encryptor.encrypt(password.encode("utf-8"))

    # get the date of when the password was added

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

    # check to see if any entires of given id and site/app name already exsists
    mycursor.execute(Q3, (id, name))
    data = mycursor.fetchone()[0]

    if data == 0:
        # if it doesn't add the new entry
        mycursor.execute(Q1, (id, name, encrpyted_password, formatted_date))
    else:
        # if it does then update the password
        mycursor.execute(Q2, (encrpyted_password, formatted_date, id, name))
    
    db.commit()


def get_user(email):
    # check to see if the email exsists
    Q1 = "SELECT password,user_id FROM users WHERE email = %s"
    mycursor.execute(Q1, (email,))
    email_check = mycursor.fetchone()
    
    # return the email_check if its None or a tuple with the passowrd and if of the current user
    return email_check

# get the list of all the sites/apps the user has a password saved in
def password_list(id):
    Q1 = "SELECT name FROM passwords WHERE user_id = %s"
    mycursor.execute(Q1, (id,))
    password_list = mycursor.fetchall()
    return password_list


# checks to see if the password entered is valid and if it is returns the decrypted password for given site/app else returns NULL
def get_password(id, name, password):

    # get the actual password
    Q1 = "SELECT password FROM users WHERE user_id = %s"
    mycursor.execute(Q1, (id,))
    actual_password = mycursor.fetchone()[0]
    
    # check to see if the password matches 
    if actual_password != password:
        return None

    # get the encrypted password from database
    Q2 = "SELECT encrpyted_password FROM passwords WHERE user_id = %s AND name = %s"
    mycursor.execute(Q2, (id,name))
    encrpyted_password = mycursor.fetchone()[0]

    if encrpyted_password is None:
        return None

    # get the private key from database
    Q3 = "SELECT private_key FROM private WHERE user_id = %s"
    mycursor.execute(Q3, (id,))
    private_key = RSA.import_key(mycursor.fetchone()[0])

    #decrypt password and return it
    decryptor = PKCS1_OAEP.new(private_key)
    decrypted_password = decryptor.decrypt(encrpyted_password)

    return decrypted_password.decode("utf-8")

# deletes a given password
def delete_password(id, name):

    #get correct password and delete it from the database
    Q = "DELETE FROM passwords WHERE user_id = %s AND name = %s"
    mycursor.execute(Q, (id,name))
    db.commit()



def delete_account(id):
    
    # deletes the user and cascades the delete to other tables
    Q = "DELETE FROM users WHERE user_id = %s"

    mycursor.execute(Q, (id,))
    db.commit()

def order_passwords(id, type):
    # chooses the right query based on the type paramater
    if type == "date_o_n":
        Q = "SELECT name FROM passwords WHERE user_id = %s ORDER BY date ASC"
    elif type == "date_n_o":
        Q = "SELECT name FROM passwords WHERE user_id = %s ORDER BY date DESC"
    else:
        Q = "SELECT name FROM passwords WHERE user_id = %s ORDER BY name ASC"
    
    # executes order paramater and returns the results
    mycursor.execute(Q, (id,))
    password_list = mycursor.fetchall()
    return password_list

def getnameindex(n_list, name):

    # responsible for getting the index of a name from session data that is fromated as an array of tuples
    for i in range(len(n_list)):
        if (n_list[i])[0] == name:
            return i


# Test queries

#create_user("Azis", "Boychev", "azis123@gmail.com", "stoyboy75")
#get_user("azis123@gmail.com")
#add_password(3, "Facebook", "test")

#get_password(2, "Amazon", "stoyboy75")
#mycursor.execute("DELETE FROM passwords WHERE user_id = 2")
#db.commit()

#delete_account(4)
#mycursor.execute("SELECT * FROM passwords")
#mycursor.execute("DESCRIBE passwords")
# showing output from cursor
#for x in mycursor:
   #print(x)