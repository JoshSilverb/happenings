"""Rest API for likes.

Covers /api/v1/p/<postid>/likes/
"""

import flask
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["GET"])
def get_likes(postid_url_slug):
    """Fetch number of likes and whether user liked this post."""
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    # Connect to database
    cur = insta485.model.get_db()

    cur.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=%s",
        (postid_url_slug,)
    )
    num_likes = cur.fetchall()[0]["count"]

    cur.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=%s AND owner=%s",
        (postid_url_slug, flask.session['username'])
    )
    user_liked = cur.fetchall()[0]["count"]

    context = {
        "logname_likes_this": user_liked,
        "likes_count": num_likes,
        "postid": postid_url_slug,
        "url": f"/api/v1/p/{postid_url_slug}/likes/"
    }

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["DELETE"])
def remove_like(postid_url_slug):
    """Remove a like from this post."""
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    # Connect to database
    cur = insta485.model.get_db()

    cur.execute(
        "DELETE FROM likes WHERE owner=%s AND postid=%s",
        (flask.session['username'],
            postid_url_slug)
    )
    return '', 204


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["POST"])
def post_like(postid_url_slug):
    """Add a like to this post."""
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    # Connect to database
    cur = insta485.model.get_db()

    # Check if user already liked this post
    cur.execute(
        "SELECT COUNT(*) FROM likes WHERE postid=%s AND owner=%s",
        (postid_url_slug, flask.session['username'])
    )
    user_liked = cur.fetchall()[0]["count"]

    # If user liked it, return some data with a 409 error
    if user_liked:
        context = {
            "logname": flask.session['username'],
            "message": "Conflict",
            "postid": postid_url_slug,
            "status_code": 409
        }
        return flask.jsonify(context), 409

    # If user didn't like it, insert like, and return some data
    cur.execute(
        "INSERT INTO likes(owner, postid) \
        VALUES (%s, %s)",
        (flask.session['username'],
            postid_url_slug)
    )

    response = {
        "logname": flask.session['username'],
        "postid": postid_url_slug,
    }

    return flask.jsonify(**response), 201
