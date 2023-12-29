"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/explore/', methods=['GET'])
def show_explore():
    """Query db and serve explore page template."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    # Connect to database
    users = insta485.model.get_db()

    # Get list of usernames that aren't being followed by user
    users = users.execute(
        "SELECT username FROM users WHERE username \
            NOT IN (SELECT username2 FROM following WHERE username1=%s)\
             AND NOT username=%s",
        (flask.session['username'], flask.session['username'])
    ).fetchall()

    context = {
        "logname": flask.session["username"],
        "not_following": []
        }
    for user in users:
        img_url = insta485.model.get_db().execute(
            "SELECT filename FROM users WHERE username=%s", (user['username'],)
        ).fetchall()[0]["filename"]
        context["not_following"].append({
            "username": user["username"],
            "user_img_url": "/uploads/"+img_url
            })

    return flask.render_template("explore.html", **context)
