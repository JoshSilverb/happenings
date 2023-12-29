"""
Insta485 user page view.

URLs include:
/u/<username>/
"""
import flask
import insta485


@insta485.app.route('/u/<username>/', methods=['GET'])
def show_userpage(username):
    """Query db and serve user page template for /u/... urls."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    # Connect to database
    cur = insta485.model.get_db()

    # Make sure the username is in the databse
    name_in_db = cur.execute(
        "SELECT COUNT(*) FROM users WHERE username=%s", (username,)
    ).fetchall()[0]["count"]
    if name_in_db == 0:
        flask.abort(404)

    # Start building up context dictionary
    context = {"username": username}
    # Get number of follwers
    context["followers"] = cur.execute(
        "SELECT COUNT(*) FROM following WHERE username2=%s", (username,)
    ).fetchall()[0]["count"]
    # Get number of people user is following
    context["following"] = cur.execute(
        "SELECT COUNT(*) FROM following WHERE username1=%s", (username,)
    ).fetchall()[0]["count"]
    # Get user's full name
    context["fullname"] = cur.execute(
        "SELECT fullname FROM users WHERE username=%s", (username,)
    ).fetchall()[0]["fullname"]

    # Get user's posts and sort them newest to oldest by postid
    pre_posts = cur.execute(
        "SELECT postid, filename FROM posts WHERE owner=%s", (username,)
    ).fetchall()
    pre_posts = sorted(pre_posts, key=lambda k: k['postid'], reverse=True)
    # fix filenames and get number of posts
    context["posts"] = []
    for post in pre_posts:
        context["posts"].append({
            "postid": post["postid"],
            "filename": str("/uploads/"+post["filename"])})
    context["total_posts"] = len(context["posts"])

    # Get misc user info
    context["logname"] = flask.session["username"]
    prof_pic = cur.execute(
        "SELECT filename FROM users WHERE username=%s", (username,)
    ).fetchall()[0]["filename"]
    context["profPic"] = str("/uploads/"+prof_pic)
    following = cur.execute(
        "SELECT COUNT(*) FROM following WHERE username1=%s AND username2=%s",
        (flask.session['username'], username)
    ).fetchall()
    context["logname_follows_username"] = following[0]["count"]

    return flask.render_template("user.html", **context)


@insta485.app.route('/u/<username>/followers/', methods=['GET'])
def show_followers(username):
    """Display page with users following <username>."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    # Connect to database
    cur = insta485.model.get_db()

    # Make sure the username is in the databse
    name_in_db = cur.execute(
        "SELECT COUNT(*) FROM users WHERE username=%s", (username,)
    ).fetchall()[0]["count"]
    if name_in_db == 0:
        flask.abort(404)

    context = {"logname": flask.session["username"]}

    followers = cur.execute(
        "SELECT username1 FROM following WHERE username2=%s", (username,)
    ).fetchall()

    context["username"] = username
    context["followers"] = []

    for name in followers:
        name = name["username1"]
        user_img_url = cur.execute(
            "SELECT filename FROM users WHERE username=%s", (name,)
        ).fetchall()[0]["filename"]
        following = cur.execute(
            "SELECT COUNT(*) FROM following WHERE username2=%s AND username1=%s",
            (name, flask.session['username'])
        ).fetchall()[0]["count"]
        following = bool(following)

        follower = {
            "username": name,
            "user_img_url": "/uploads/"+user_img_url,
            "logname_follows_username": following
        }

        context["followers"].append(follower)

    return flask.render_template("followers.html", **context)


@insta485.app.route('/u/<username>/following/', methods=['GET'])
def show_following(username):
    """Display page with users followed by <username>."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    # Connect to database
    cur = insta485.model.get_db()

    # Make sure the username is in the databse
    name_in_db = cur.execute(
        "SELECT COUNT(*) FROM users WHERE username=%s", (username,)
    ).fetchall()[0]["count"]
    if name_in_db == 0:
        flask.abort(404)

    context = {"logname": flask.session["username"]}

    following = cur.execute(
        "SELECT username2 FROM following WHERE username1=%s", (username,)
    ).fetchall()

    context["username"] = username
    context["following"] = []

    for name in following:
        name = name["username2"]
        user_img_url = cur.execute(
            "SELECT filename FROM users WHERE username=%s", (name,)
        ).fetchall()[0]["filename"]
        following = cur.execute(
            "SELECT COUNT(*) FROM following WHERE username2=%s AND username1=%s",
            (name, flask.session['username'])
        ).fetchall()[0]["count"]
        following = bool(following)

        follower = {
            "username": name,
            "user_img_url": "/uploads/"+user_img_url,
            "logname_follows_username": following
        }

        context["following"].append(follower)

    return flask.render_template("following.html", **context)


@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display account edit page."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    # Connect to database
    cur = insta485.model.get_db()

    context = cur.execute(
        "SELECT username, filename, fullname, email FROM users \
            WHERE username=%s", (flask.session['username'],)
    ).fetchall()[0]

    context["filename"] = "/uploads/" + context["filename"]

    context["logname"] = flask.session["username"]

    return flask.render_template("editUser.html", **context)


@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Display account delete confirmation page."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    context = {"logname": flask.session["username"]}

    return flask.render_template("deleteUser.html", **context)


@insta485.app.route('/accounts/password/', methods=['GET'])
def show_pword_change():
    """Display passowrd change page."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    return flask.render_template("password.html",
                                 **{"logname": flask.session["username"]})
