from flask import Flask, redirect, url_for, render_template, request, session
from SQL_queries import *


app = Flask(__name__)
app.secret_key = "JW8WJ62WKAL09JASM"

# login page 
@app.route("/", methods = ["POST", "GET"])
def login():
    # check if the page was routed to with a post call AKA they pressed submit
    if request.method == "POST":
        email, passw = request.form['email'], request.form['pas']
    
        # See if username nad password are valid
        check_user = get_user(email)

        if check_user is None:
            return redirect(url_for("login"))
        else:
            if passw != check_user[0]:
                return redirect(url_for("login"))
        
        # if the user is valid then create their session data 
        session["user"] = email
        session["password"] = passw
        session['id'] = check_user[1]

        return redirect(url_for("user"))
    else:
        # if already logged in then redirect to home page

        if "user" in session:
            return redirect(url_for("user"))
        
        # if not then they haven't logged and need to do so
        return render_template("login.html")

# route responsible for validating user data before showing main page
@app.route("/user")
def user():
    # if the user has logged in then continue 
    if "user" in session:
        user = session["user"]
        password = session["password"]
        id = session["id"]

        # if the user's session data has already been fully initialzied then user that else update it 
        try:
            n_list = session["names"]
        except:
            session["names"] = n_list = password_list(id) 

        if n_list is None:
            session["names"] = n_list = password_list(id) 

        # render the home template
        return render_template("home.html", user = user, password = password, id = id, n_list = n_list)
    else:
        return render_template(url_for("login"))

# logout route that will clear session data and return the user to the login page
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("password", None)
    return redirect(url_for("login"))

# route responsible for deleting a password from the databse 
@app.route('/delete/<name>/', methods=['GET', 'POST']) 
def delete_pass(name): 
    if request.method == "POST":
        id = session["id"]

        delete_password(session["id"], name)

        # updates the session data with the new password list
        session["names"] = password_list(id) 

        return redirect(url_for("user"))
    
# route that shows the pass but requires getting acess to the private key to decrypt the password
@app.route('/show/<name>/', methods=['GET', 'POST']) 
def show_pass(name): 
    if request.method == "POST":
        id = session["id"]
        password = session["password"]
        decrypted_password = get_password(id, name, password)

        # get password and update it into the session data
        n_list = session["names"]

        index = getnameindex(n_list, name)

        L = list(n_list[index])

        try:
            del L[1]
        except:
            L.append(decrypted_password)
        
        ((session["names"])[index]) = tuple(L)
        session.modified = True
    

        return redirect(url_for("user")) 

# route responsible for adding passwords to the database
@app.route('/add', methods=['GET', 'POST']) 
def add_pass(): 
    if request.method == "POST":
        id = session["id"]
        
        name, password = request.form['new_name'], request.form['new_pass']

        add_password(id, name, password)

        session["names"] = password_list(id) 
        session.modified = True

        return redirect(url_for("user"))
    
# route responsible for ordering the password based on the required type
@app.route('/order/<type>/') 
def order_pass(type): 
    id = session["id"]

    ordered = order_passwords(id, type)

    # orders the data based on the index order
    for x in range(len(ordered)):
        for y in range(len(session['names'])):
            if ordered[x][0] == session['names'][y][0]:
                ordered[x] = (session['names'])[y]
    

    session['names'] = ordered
    session.modified = True

    return redirect(url_for("user"))

    
if __name__ == "__main__":
    app.run(debug = True)