"""
Insta485 login page.

URLs include:
/accounts/create/
/accounts/login/
/accounts/logout/
/accounts/
"""
import uuid
import pathlib
import hashlib
import os
import flask
import insta485


@insta485.app.route('/accounts/create/', methods=['GET'])
def serve_create():
    """Show login page with error msg or redirect to index if logged in."""
    # Check if user is logged in (non-empty username in cookie)
    if 'username' in flask.session:
        if flask.session['username'] != "":
            return flask.redirect(flask.url_for("show_edit"))
    return flask.render_template("createUser.html", **{})


@insta485.app.route('/accounts/login/', methods=['GET'])
def serve_login():
    """Show login page with error msg or redirect to index if logged in."""
    # Check if user is logged in (non-empty username in cookie)
    if 'username' in flask.session:
        if flask.session['username'] != "":
            return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("login.html", **{})


def handle_login(form, args):
    """Validate login credentials or redirect back to login page."""
    # Connect to database
    cur = insta485.model.get_db()

    # Get password hash from database from username
    cur.execute(
        "SELECT password FROM users WHERE username=%s", (form['username'],)
    )
    dbhash = cur.fetchall()

    # Username doesn't exist
    if len(dbhash) == 0:
        # set cookie that username/password is wrong
        flask.abort(403)
        return flask.redirect(flask.url_for("serve_login"))

    # Unpack password from database and check against entered password
    dbhash = dbhash[0]["password"]
    salt = dbhash[7:39]

    prehash = salt + form["password"]

    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(prehash.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_hashed_string = "$".join([algorithm, salt, password_hash])

    if dbhash == password_hashed_string:
        flask.session["username"] = form["username"]
        if "target" in args:
            return flask.redirect(args.get("target"))
        return flask.redirect(flask.url_for("show_index"))

    flask.abort(403)
    return flask.redirect(flask.url_for("show_index"))


def handle_create(form, args, files):
    """Create a new user, log them in, and redirect to url."""
    # Connect to database
    cur = insta485.model.get_db()

    # if any field is blank, return error
    if not (form['username']
            and form['password']
            and form['fullname']
            and form['email']
            ):
        flask.abort(400)

    # make sure username isn't already in the database
    uname_count = cur.execute(
        "SELECT COUNT(*) FROM users WHERE username=%s", (form['username'],)
    ).fetchall()[0]["count"]

    # Username already exists - return error
    if uname_count != 0:
        flask.abort(409)
        return flask.redirect(flask.url_for("serve_login"))

    # Generate salt and hash password
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    hash_obj.update((salt + form["password"]).encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # Save newfile and put the filename into the database
    # Unpack flask object
    fileobj = files["file"]
    filename = fileobj.filename

    # Compute base name (filename without directory). We use a UUID
    # to avoid clashes with existing files, and ensure that the name
    # is compatible with the filesystem.
    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(filename).suffix
    )

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    # Add stuff to database
    data = form
    cur.execute(
        # Add session name to this instead of awdeorio
        "INSERT INTO users(username, fullname, email, filename, password)\
            VALUES (%s, %s, %s, %s, %s);",
        (data['username'], data['fullname'], data['email'],
            uuid_basename, password_db_string)
    )

    # Log user in
    flask.session["username"] = data["username"]

    if "target" in args:
        return flask.redirect(args.get("target"))
    return flask.redirect(flask.url_for("show_index"))


def handle_delete(args):
    """Delete a user, log them out, and redirect to url."""
    # Connect to database
    cur = insta485.model.get_db()

    # Error if not logged in
    if "username" not in flask.session or not flask.session["username"]:
        flask.abort(403)

    # Delete files associated with the user (posts, profile pic)
    post_files = cur.execute(
        "SELECT filename FROM posts WHERE owner=%s",
        (flask.session['username'],)
    ).fetchall()
    for post in post_files:
        filename = post["filename"]
        os.remove(insta485.app.config["UPLOAD_FOLDER"]/filename)
    user_pic = cur.execute(
        "SELECT filename FROM users WHERE username=%s",
        (flask.session['username'],)
    ).fetchall()[0]["filename"]
    os.remove(insta485.app.config["UPLOAD_FOLDER"]/user_pic)

    # Delete user's entry into user table,
    # causing everything else associated with them to delete in cascade
    cur.execute(
        "DELETE FROM users WHERE username=%s", (flask.session['username'],)
    )

    # Remove the user's username from session
    flask.session["username"] = ""
    if "target" in args:
        return flask.redirect(args.get("target"))
    return flask.redirect(flask.url_for("show_index"))


def handle_edit(form, args, files):
    """Edit a user's db entry and redirect to url."""
    # Connect to database
    cur = insta485.model.get_db()

    # Error if not logged in
    if "username" not in flask.session or not flask.session["username"]:
        flask.abort(403)

    # Just change text stuff
    cur.execute(
        "UPDATE users SET fullname=%s, email=%s WHERE username=%s",
        (form['fullname'], form['email'], flask.session['username'])
    )
    # Also change the photo
    if files["file"]:
        filename = cur.execute(
            "SELECT filename FROM users WHERE username=%s",
            (flask.session['username'],)
        ).fetchall()[0]["filename"]
        # Delete old photo
        if os.path.exists(insta485.app.config["UPLOAD_FOLDER"]/filename):
            os.remove(insta485.app.config["UPLOAD_FOLDER"]/filename)

        # Save newfile and put the filename into the database
        # Unpack flask object
        fileobj = files["file"]
        filename = fileobj.filename

        # Compute base name (filename without directory). We use a UUID
        # to avoid clashes with existing files, and ensure that the name
        # is compatible with the filesystem.
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        # update just filename in database since other stuff is already set
        cur.execute(
            "UPDATE users SET filename=%s WHERE username=%s",
            (uuid_basename, flask.session['username'])
        )

    if "target" in args:
        return flask.redirect(args.get("target"))
    return flask.redirect(flask.url_for("show_index"))


def handle_pchange(form, args):
    """Change a user's password and redirect to url."""
    # Connect to database
    cur = insta485.model.get_db()

    # Error if not logged in
    if "username" not in flask.session or not flask.session["username"]:
        flask.abort(403)
    # Error if any empty fields submitted
    if not(form["password"] and
            form["new_password1"] and
            form["new_password2"]):
        flask.abort(400)

    # Unpack password from database and check against entered password
    dbhash = cur.execute(
        "SELECT password FROM users WHERE username=%s",
        (flask.session['username'],)
    ).fetchall()[0]["password"]
    salt = dbhash[7:39]

    prehash = salt + form["password"]

    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(prehash.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_hashed_string = "$".join([algorithm, salt, password_hash])

    # If entered pwd hash matches db pwd hash allow it to be changed
    if dbhash == password_hashed_string:
        # Error if new passwords don't match
        pwd_1 = form["new_password1"]
        pwd_2 = form["new_password2"]
        if pwd_1 != pwd_2:
            flask.abort(401)

        # If they match, generate salt and hash new password
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        hash_obj.update((salt + form["new_password1"]).encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        # Update password in database
        cur.execute(
            "UPDATE users SET password=%s WHERE username=%s",
            (password_db_string, flask.session['username'])
        )

        if "target" in args:
            return flask.redirect(args.get("target"))
        flask.redirect(flask.url_for("show_index"))
    else:
        flask.abort(403)
    return flask.redirect(flask.url_for("show_index"))


@insta485.app.route('/accounts/', methods=['POST'])
def acc_post_requests():
    """Handle post requests to the /accounts/ endpoint."""
    if flask.request.form["operation"] == "login":
        return handle_login(flask.request.form, flask.request.args)

    if flask.request.form["operation"] == "create":
        return handle_create(flask.request.form,
                             flask.request.args,
                             flask.request.files)

    if flask.request.form["operation"] == "delete":
        return handle_delete(flask.request.args)

    if flask.request.form["operation"] == "edit_account":
        return handle_edit(flask.request.form,
                           flask.request.args,
                           flask.request.files)

    if flask.request.form["operation"] == "update_password":
        return handle_pchange(flask.request.form, flask.request.args)

    flask.abort(404)
    return flask.redirect(flask.url_for("show_index"))


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Log user out by setting username cookie to blank string."""
    flask.session["username"] = ""
    return flask.redirect(flask.url_for("serve_login"))
