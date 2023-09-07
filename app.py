from flask import Flask, render_template, request, redirect, url_for
from argon2 import PasswordHasher, exceptions
from client import users, secretes
from datetime import timedelta
from bson.objectid import ObjectId
from random import random
from mail import sendFancyEmail
from uuid import uuid4


"""
-> http://localhost:1234


                    [login] -------
                    |               |
student | admin --->                ----> [HOME]
                    |               |
                    [register]------

* LOGIN (email, password)
    * is the user logged in
        * redirect to home
    * else
        * look for the person's email in the database
        * compare plain password and hashed
        * store the userId as the value of the cookie


* REGISTER (email, password)
    * is the user logged in
        * redirect to home
    * else
        * look for the person's email in the database
        * create new user email and password (hashed)
        * store the userId as the value of the cookie

* HOME {key: value}
    * if we have a cookie {'userId': 'ajaoopapa'}
        * if the userId has the user in the database
            * you are logged in
        * else:
            * we have a fake cookie (login)
    * else
        * you are not logged in (login)
* LOGOUT
    * delete/clear the cookie (login)

* RESETTING PASSWORD
    * send a request link to the user using an email in this link we will have a secrete token
    * compare the token with the one stored in the database
        * in the event that they matches we change the password

* DELETE USERS
    * delete the user and reload users


* EDIT USER PROFILE BY ADMIN
    * they can change (gender, avatar, email, gender)
    * we need a route that allows us to edit user by id
"""


COOKIE_NAME = "userId"
hasher = PasswordHasher()
app = Flask(__name__)


@app.route("/user/delete/<string:id>")
def delete_user(id):
    users.delete_one({"_id": (ObjectId(id))})
    res = redirect(url_for("home"))
    return res, 302


@app.route("/profile/edit/<string:id>", methods=["POST", "GET"])
def edit_user_profile(id):
    ctx = {"error": "", "user": None}
    res = render_template("app/edit_user_profile.html", ctx=ctx)
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            res = redirect(url_for("login"))
            res.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return res, 302
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        user = users.find_one({"_id": (ObjectId(id))})
        if me is None:
            res = redirect(url_for("login"))
            res.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return res, 302
        if me["role"] != "ADMIN" or user is None:
            return redirect(url_for("home"))

        ctx["user"] = user
        return render_template("app/edit_user_profile.html", ctx=ctx)
    else:
        cookies = request.cookies
        data = request.form
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        user = users.find_one({"_id": (ObjectId(id))})
        email = data["email"].lower().strip()
        firstName = data["firstName"].strip().capitalize()
        lastName = data["lastName"].strip().capitalize()
        gender = data["gender"]
        avatar = data["avatar"] if "avatar" in data else False
        avatar = bool(avatar)
        url = (
            f"https://avatars.dicebear.com/api/human/{str(random())[2:]}.png"
            if avatar
            else None
        )
        role = data["role"] if "role" in data else me["role"]
        if not email:
            ctx["error"] = "The email address is required."
            return render_template("app/edit_user_profile.html", ctx=ctx)
        if len(firstName) < 3:
            ctx["error"] = "Your name must have at least 3 characters."
            return render_template("app/edit_user_profile.html", ctx=ctx)
        if len(lastName) < 3:
            ctx["error"] = "Your surname must have at least 3 characters."
            return render_template("app/edit_user_profile.html", ctx=ctx)

        new = (
            {
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "gender": gender,
                "role": role,
            }
            if url is None
            else {
                "avatar": url,
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "gender": gender,
                "role": role,
            }
        )
        if user["email"] != email:
            exists = users.find_one({"email": email})
            if exists is not None:
                ctx["error"] = "The email address is already taken by someone else"
                return render_template("app/edit_user_profile.html", ctx=ctx)

        users.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": new},
        )
        response = redirect(url_for("home"))
        response.set_cookie(
            COOKIE_NAME,
            str(me["_id"]),
            timedelta(days=7),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )
        return response, 302


@app.route("/profile/edit", methods=["POST", "GET"])
def edit_profile():
    ctx = {"error": "", "me": None}
    res = render_template("app/edit_profile.html", ctx=ctx)
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            res = redirect(url_for("login"))
            res.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return res, 302
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        if me is None:
            res = redirect(url_for("login"))
            res.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return res, 302
        ctx["me"] = me
        return render_template("app/edit_profile.html", ctx=ctx)
    else:
        cookies = request.cookies
        data = request.form
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        email = data["email"].lower().strip()
        firstName = data["firstName"].strip().capitalize()
        lastName = data["lastName"].strip().capitalize()
        bio = data["bio"].strip()
        gender = data["gender"]
        avatar = data["avatar"] if "avatar" in data else False
        avatar = bool(avatar)
        url = (
            f"https://avatars.dicebear.com/api/human/{str(random())[2:]}.png"
            if avatar
            else None
        )
        role = data["role"] if "role" in data else me["role"]
        if not email:
            ctx["error"] = "The email address is required."
            return render_template("app/edit_profile.html", ctx=ctx)
        if len(firstName) < 3:
            ctx["error"] = "Your name must have at least 3 characters."
            return render_template("app/edit_profile.html", ctx=ctx)
        if len(lastName) < 3:
            ctx["error"] = "Your surname must have at least 3 characters."
            return render_template("app/edit_profile.html", ctx=ctx)

        new = (
            {
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "gender": gender,
                "role": role,
                "bio": bio,
            }
            if url is None
            else {
                "avatar": url,
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "gender": gender,
                "role": role,
                "bio": bio,
            }
        )
        if me["email"] != email:
            exists = users.find_one({"email": email})
            if exists is not None:
                ctx["error"] = "The email address is already taken by someone else"
                return render_template("app/edit_profile.html", ctx=ctx)

        users.update_one(
            {"_id": ObjectId(me["_id"])},
            {"$set": new},
        )
        response = redirect(url_for("home"))
        response.set_cookie(
            COOKIE_NAME,
            str(me["_id"]),
            timedelta(days=7),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )
        return response, 302


@app.route("/auth/change-password/<string:token>", methods=["POST", "GET"])
def change_password(token):
    ctx = {"error": "", "message": ""}
    res = render_template("auth/change-password.html", ctx=ctx)
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            return res, 200
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        if me is None:
            return res, 200
        else:
            ctx["error"] = ""
            response = redirect(url_for("home"))
            response.set_cookie(
                COOKIE_NAME,
                str(me["_id"]),
                timedelta(days=7),
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return response, 302
    else:
        data = request.form
        password = data["password"]
        confirm = data["confirmPassword"]
        doc = secretes.find_one({"token": token})
        if doc is None:
            ctx["error"] = "Invalid reset password token."
            return render_template("auth/register.html", ctx=ctx)

        if len(password) < 5:
            ctx["error"] = "The password must have at least 5 characters"
            return render_template("auth/register.html", ctx=ctx)

        if password != confirm:
            ctx["error"] = "The two password must match."
            return render_template("auth/register.html", ctx=ctx)

        hashedPassword = hasher.hash(password)
        users.update_one(
            {"_id": ObjectId(doc["id"])},
            {"$set": {"password": hashedPassword}},
        )
        secretes.delete_one({"_id": doc["_id"]})
        ctx["message"] = f"Your password has been reset successively."
        return render_template("auth/change-password.html", ctx=ctx)


@app.route("/auth/forgot-password", methods=["POST", "GET"])
def forgot_password():
    ctx = {"error": "", "message": ""}
    res = render_template("auth/forgot-password.html", ctx=ctx)
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            return res, 200
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        if me is None:
            return res, 200
        else:
            ctx["error"] = ""
            response = redirect(url_for("home"))
            response.set_cookie(
                COOKIE_NAME,
                str(me["_id"]),
                timedelta(days=7),
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return response, 302
    else:
        data = request.form
        email = data["email"].lower().strip()
        me = users.find_one({"email": email})
        if me is None:
            ctx["error"] = "The email address does not have an account."
            return render_template("auth/forgot-password.html", ctx=ctx)
        else:
            # notify the user that the email has been sent
            token = str(uuid4())
            url = f"http://localhost:1234/auth/change-password/{token}"
            secretes.insert_one({"token": token, "id": me["_id"]})
            html = f"""
            <html>
            <body>
                <h6>Hi {me['firstName']} {me['lastName']}, </h6>
                <p>We have received a reset password request on your SMS account, please click the following
                link if you want to reset your password. If you do not intent to reset the password
                you can ignore this email.</p>
                <br/>
                {url}
                <br/><br/>
                <p>Regards</p>
                <br/>
                <b>SMS Team</b>
            </body>
            </html>
            """

            sendFancyEmail(email, html, "Reset SMS Account Password")
            ctx["message"] = f"The reset password link has been sent to {email}."

            return render_template("auth/forgot-password.html", ctx=ctx)


@app.route("/auth/logout", methods=["POST", "GET"])
def logout():
    if request.method == "POST" or request.method == "GET":
        response = redirect("/auth/login")
        response.delete_cookie(
            COOKIE_NAME,
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )
        return response, 302
    return "logout", 302


@app.route("/", methods=["GET"])
def home():
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            res = redirect(url_for("login"))
            res.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return res, 302
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        people = users.find({})
        if me is None:
            res = redirect(url_for("login"))
            res.delete_cookie(
                COOKIE_NAME,
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return res, 302
        ctx = {"me": me, "users": people}
        return render_template("index.html", ctx=ctx)


@app.route("/auth/register", methods=["GET", "POST"])
def register():
    ctx = {"error": ""}
    res = render_template("auth/register.html", ctx=ctx)
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            return res, 200
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        if me is None:
            return res, 200
        else:
            ctx["error"] = ""
            response = redirect(url_for("home"))
            response.set_cookie(
                COOKIE_NAME,
                str(me["_id"]),
                timedelta(days=7),
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return response, 302
    else:
        data = request.form
        email = data["email"].lower().strip()
        firstName = data["firstName"].strip().capitalize()
        lastName = data["lastName"].strip().capitalize()
        password = data["password"]
        confirm = data["confirmPassword"]
        role = data["role"]
        gender = data["gender"]

        if not email:
            ctx["error"] = "The email address is required."
            return render_template("auth/register.html", ctx=ctx)

        exists = users.find_one({"email": email})
        if exists is not None:
            ctx["error"] = "The email address is already taken by someone else"
            return render_template("auth/register.html", ctx=ctx)

        if len(password) < 5:
            ctx["error"] = "The password must have at least 5 characters"
            return render_template("auth/register.html", ctx=ctx)

        if len(firstName) < 3:
            ctx["error"] = "Your name must have at least 3 characters."
            return render_template("auth/register.html", ctx=ctx)
        if len(lastName) < 3:
            ctx["error"] = "Your surname must have at least 3 characters."
            return render_template("auth/register.html", ctx=ctx)
        if password != confirm:
            ctx["error"] = "The two password must match."
            return render_template("auth/register.html", ctx=ctx)

        hashedPassword = hasher.hash(password)
        user = {
            "password": hashedPassword,
            "email": email,
            "role": role,
            "firstName": firstName,
            "lastName": lastName,
            "gender": gender,
        }
        cursor = users.insert_one(user)
        ctx["error"] = ""
        response = redirect(url_for("home"))
        response.set_cookie(
            COOKIE_NAME,
            str(cursor.inserted_id),
            timedelta(days=7),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )
        return response, 302


@app.route("/auth/login", methods=["GET", "POST"])
def login():
    ctx = {"error": ""}
    res = render_template("auth/login.html", ctx=ctx)
    if request.method == "GET":
        cookies = request.cookies
        if COOKIE_NAME not in cookies:
            return res, 200
        _id = request.cookies[COOKIE_NAME]
        me = users.find_one({"_id": (ObjectId(_id))})
        if me is None:
            return res, 200
        else:
            ctx["error"] = ""
            response = redirect(url_for("home"))
            response.set_cookie(
                COOKIE_NAME,
                str(me["_id"]),
                timedelta(days=7),
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return response, 302
    else:
        data = request.form
        email = data["email"].lower().strip()
        password = data["password"]
        me = users.find_one({"email": email})
        if me is None:
            ctx["error"] = "The email address does not have an account."
            return render_template("auth/login.html", ctx=ctx)
        try:
            hasher.verify(me["password"], password)
            ctx["error"] = ""
            response = redirect(url_for("home"))
            response.set_cookie(
                COOKIE_NAME,
                str(me["_id"]),
                timedelta(days=7),
                path="/",
                secure=False,
                httponly=True,
                samesite="lax",
            )
            return response, 302
        except exceptions.VerifyMismatchError:
            ctx["error"] = "The password is invalid"
            return render_template("auth/login.html", ctx=ctx)


if __name__ == "__main__":
    app.run(host="localhost", port=1234, debug=True)
