"""
Functions for endpoints for the buttons.

URLs include:
/like/
/unlike/
/comments/
"""
from pathlib import Path
import uuid
import os
import flask
import insta485


@insta485.app.route('/likes/', methods=['POST'])
def change_likes():
    """Add or remove a like for this post to the database."""
    # Connect to database
    cur = insta485.model.get_db()

    # Check whether the user has liked this yet
    liked = cur.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=%s AND owner=%s",
        (flask.request.form['postid'], flask.session['username'])
    ).fetchall()[0]["count"]

    if flask.request.form["operation"] == "like":
        # Check whether the user has liked this yet
        if liked != 0:
            flask.abort(409)

        # If they haven't liked it yet, add a like from user to the database
        cur.execute(
            "INSERT INTO likes(owner, postid) VALUES (%s, %s)",
            (flask.session['username'], flask.request.form['postid'])
        )

    elif flask.request.form["operation"] == "unlike":
        # Check whether the user has liked this yet
        if liked != 1:
            flask.abort(409)
        # Remove user's like from database
        cur.execute(
            "DELETE FROM likes WHERE owner=%s", (flask.session['username'],)
        )

    if "target" in flask.request.args:
        return flask.redirect(flask.request.args.get("target"))
    return flask.redirect(flask.url_for("show_index"))


@insta485.app.route('/comments/', methods=['POST'])
def change_comments():
    """Add or remove a comment for this post from the database."""
    # Connect to database
    cur = insta485.model.get_db()

    if flask.request.form["operation"] == "delete":
        # Make sure the user posted the comment
        owner = cur.execute(
            "SELECT owner FROM comments WHERE commentid=%s",
            (flask.request.form['commentid'],)
        ).fetchall()[0]["owner"]
        if owner != flask.session["username"]:
            flask.abort(403)
        cur.execute(
            "DELETE FROM comments \
                WHERE commentid=%s", (flask.request.form['commentid'],)
        )

    elif flask.request.form["operation"] == "create":
        if len(flask.request.form["text"]) == 0:
            flask.abort(400)

        insta485.helpers.insert_comment(flask.session['username'],
                                        flask.request.form.get('postid'),
                                        flask.request.form.get('text'),
                                        cur)

    if "target" in flask.request.args:
        return flask.redirect(flask.request.args.get("target"))
    return flask.redirect(flask.url_for("show_index"))


@insta485.app.route('/following/', methods=['POST'])
def change_following():
    """Add or remove a follow connection between users to the database."""
    # Connect to database
    cur = insta485.model.get_db()
    # Check whether the user is following yet
    following = cur.execute(
            "SELECT COUNT(*) FROM following WHERE username2=%s AND username1=%s",
            (flask.request.form['username'], flask.session['username'])
        ).fetchall()[0]["count"]

    if flask.request.form["operation"] == "follow":
        if following != 0:
            flask.abort(409)
        # Add connection between users to the database
        cur.execute(
            "INSERT INTO following(username1, username2) VALUES (%s, %s)",
            (flask.session['username'], flask.request.form['username'])
        )
    elif flask.request.form["operation"] == "unfollow":
        if following == 0:
            flask.abort(409)
        # Remove connection between users from database
        cur.execute(
            "DELETE FROM following WHERE username1=%s AND username2=%s",
            (flask.session['username'], flask.request.form['username'])
        )
    if "target" in flask.request.args:
        return flask.redirect(flask.request.args.get("target"))
    return flask.redirect(flask.url_for("show_index"))


@insta485.app.route('/posts/', methods=['POST'])
def change_post():
    """Add or remove a post to the database."""
    # Connect to database
    cur = insta485.model.get_db()

    if flask.request.form["operation"] == "create":
        if not flask.request.files["file"]:
            flask.abort(400)
        # Save file and put the filename into the database
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        # Compute base name (filename without directory).  We use a UUID
        # to avoid clashes with existing files, and ensure that the
        # name is compatible with the filesystem.
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=Path(filename).suffix
        )

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        # Add stuff to database
        cur.execute(
            "INSERT INTO posts(filename, owner) VALUES (%s, %s)",
            (uuid_basename, flask.session['username'])
        )

    elif flask.request.form["operation"] == "delete":
        # Make sure the user posted the post
        post = cur.execute(
            "SELECT owner, filename FROM posts WHERE postid=%s",
            (flask.request.form['postid'],)
        ).fetchall()[0]
        if post["owner"] != flask.session["username"]:
            flask.abort(403)
        cur.execute(
            "DELETE FROM posts WHERE postid=%s",
            (flask.request.form['postid'],)
        )
        os.remove(insta485.app.config["UPLOAD_FOLDER"]/post["filename"])

    if "target" in flask.request.args:
        return flask.redirect(flask.request.args.get("target"))
    return flask.redirect(flask.url_for("show_userpage",
                                        username=flask.session["username"]))
