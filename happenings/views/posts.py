"""
Insta485 post page view.

URLs include:
/p/<post_id>/
"""
from pathlib import Path
import arrow
import flask
import insta485
from insta485.views.index import fetch_post_comments


@insta485.app.route('/p/<postid>/', methods=['GET'])
def show_postpage(postid):
    """Serve page for post <postid>."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return flask.redirect(flask.url_for("serve_login"))

    # Connect to database
    cur = insta485.model.get_db()

    [post] = cur.execute(
        "SELECT filename, owner, created FROM posts WHERE postid=%s", (postid,)
    ).fetchall()

    url = Path(post["filename"])
    post["filename"] = str("/uploads"/url)

    post["comments"] = fetch_post_comments(cur, postid)

    # Fetch owner picture
    cur.execute(
        "SELECT filename FROM users WHERE username=%s", (post['owner'],)
    )
    [url] = (cur.fetchall())
    url = Path(url["filename"])
    post["owner_img_url"] = str("/uploads"/url)

    # Get likes
    get_likes = cur.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=%s", (postid,)
    ).fetchall()
    post["likes"] = get_likes[0]["count"]

    # Check if user has liked or not
    user_liked = cur.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=%s AND owner=%s",
        (postid, flask.session['username'])
    ).fetchall()[0]["count"]

    post["userliked"] = bool(user_liked)

    # Humanize timestamp
    timestamp = arrow.get(post["created"], 'YYYY-MM-DD HH:mm:ss')
    post["created"] = timestamp.humanize()

    post["logname"] = flask.session["username"]
    post["postid"] = postid

    return flask.render_template("post.html", **post)
