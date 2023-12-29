"""
Insta485 index (main) view.

URLs include:
/
"""
from pathlib import Path
import arrow
import flask
import insta485


@insta485.app.route('/', methods=['GET'])
def show_index():
    """Serve home page filled with database data."""
    if "username" not in flask.session or flask.session["username"] == "":
        return flask.redirect(flask.url_for("serve_login"))
    # Connect to database
    cur = insta485.model.get_db()

    # Find accounts followed by user
    followed = insta485.helpers.get_followed(cur,
                                             flask.session["username"])

    # Add logged in user to lit of followed users so their posts show up too
    followed.append({"username2": flask.session["username"]})

    # Add posts from followed accounts and add to all_posts list
    all_posts = []
    for acc in followed:
        acc = acc["username2"]
        cur.execute(
            "SELECT * FROM posts WHERE owner=%s", (acc,)
        )
        posts = cur.fetchall()
        for post in posts:
            url = Path(post["filename"])
            post["filename"] = str("/uploads"/url)

            post["comments"] = fetch_post_comments(cur, post['postid'])

            # Fetch owner picture
            cur.execute(
                "SELECT filename FROM users WHERE username=%s", (post['owner'],)
            )

            # Get likes
            cur.execute(
                "SELECT COUNT(*) FROM likes WHERE postid=%s", (post['postid'],)
            )
            get_likes = cur.fetchall()
            post["likes"] = get_likes[0]["count"]

            # Unpack owner picture
            cur.execute(
                "SELECT filename FROM users WHERE username=%s", (flask.session['username'],)
            )
            [url] = (cur.fetchall())
            url = Path(url["filename"])
            post["owner_img_url"] = str("/uploads"/url)

            # Check if user has liked or not
            cur.execute(
                "SELECT COUNT(*) FROM likes WHERE postid=%s AND owner=%s",
                (post['postid'], flask.session['username'])
            )
            user_liked = cur.fetchall()[0]["count"]

            post["userliked"] = bool(user_liked)

            # Humanize timestamp
            timestamp = arrow.get(post["created"])
            print("Timestamp:",timestamp)
            post["created"] = timestamp.humanize()
            all_posts.append(post)
    # Sort all_posts by postid
    all_posts = sorted(all_posts, key=lambda k: k['postid'], reverse=True)

    # Add database info to context
    context = {"posts": all_posts, "logname": flask.session["username"]}
    return flask.render_template("index.html", **context)


def fetch_post_comments(cur, postid):
    """Fetch comments and sort newest to oldest."""
    cur.execute(
        "SELECT commentid, owner, postid, text FROM comments WHERE postid=%s",
        (postid,)
    )
    comments = cur.fetchall()
    comments = sorted(comments,
                      key=lambda k: k['commentid'],
                      reverse=True)
    return comments
