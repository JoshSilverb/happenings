"""Rest API for comments.

Covers /api/v1/p/<postid>/comments/
"""

import flask
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["GET"])
def get_comments(postid_url_slug):
    """Fetch comments and sort newest to oldest."""
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    # Connect to database
    cur = insta485.model.get_db()

    cur.execute(
        "SELECT commentid, owner, postid, text FROM comments WHERE postid=%s",
        (postid_url_slug,)
    )
    comments = cur.fetchall()
    comments = sorted(comments,
                      key=lambda k: k['commentid'],
                      reverse=True)
    for comment in comments:

        comment["owner_show_url"] = f"/u/{comment['owner']}/"

    # Sort comments by commentid
    comments = sorted(comments, key=lambda k: k['commentid'], reverse=False)

    context = {
        "comments": comments,
        "url": f"/api/v1/p/{postid_url_slug}/comments/"
    }

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["POST"])
def post_comment(postid_url_slug):
    """Post a comment."""
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    # Connect to database
    cur = insta485.model.get_db()
    text = flask.request.get_json()["text"]

    if len(text) == 0:
        flask.abort(400)

    insta485.helpers.insert_comment(flask.session['username'],
                                    postid_url_slug,
                                    text,
                                    cur)

    cur.execute(
        "SELECT COUNT(*) FROM comments WHERE postid=%s", (postid_url_slug,)
    )
    comment_id = cur.fetchall()[0]["count"]

    response = {
        "commentid": comment_id,
        "owner": flask.session['username'],
        "owner_show_url": f"/u/{flask.session['username']}/",
        "postid": postid_url_slug,
        "text": text
    }

    return flask.jsonify(**response), 201
