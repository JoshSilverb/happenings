"""REST API for posts."""
import flask
import insta485


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_list_posts():
    """Return 10 newest posts, or a spec number or rq a specific page."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    # Connect to database
    cur = insta485.model.get_db()

    # Find accounts followed by user
    followed = insta485.helpers.get_followed(cur,
                                             flask.session["username"])

    # Add logged in user to lit of followed users so their posts show up too
    followed.append({"username2": flask.session["username"]})

    posts = 10
    page = 0
    if "size" in flask.request.args:
        posts = int(flask.request.args["size"])
    if "page" in flask.request.args:
        page = int(flask.request.args["page"])

    # Index in all_posts of first post on this page
    first_post_index = posts * page

    all_posts = []
    for acc in followed:
        acc = acc["username2"]
        cur.execute(
            "SELECT postid FROM posts WHERE owner=%s", (acc,)
        )
        posts_list = cur.fetchall()
        for post in posts_list:
            post["url"] = f"/api/v1/p/{post['postid']}/"
            all_posts.append(post)

    # Sort all_posts by postid
    all_posts = sorted(all_posts, key=lambda k: k['postid'], reverse=True)

    # Check if there's enough posts for a next page
    if (first_post_index + posts) < len(all_posts):
        next_page = f"/api/v1/p/%ssize={posts}&page={page+1}"
    else:
        next_page = ""

    post_array = all_posts[first_post_index: first_post_index + posts]

    context = {
        "next": next_page,
        "results": post_array,
        "url": "/api/v1/p/"
    }

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post(postid_url_slug):
    """Return post on postid."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        return (flask.jsonify(**{"message": "Forbidden", "status_code": 403}),
                403)

    context = {}

    # Connect to database
    cur = insta485.model.get_db()

    # Fetch info about the post
    cur.execute(
        "SELECT filename, owner, created FROM posts WHERE postid=%s",
        (postid_url_slug,)
    )
    [post] = cur.fetchall()

    # Fetch owner picture
    cur.execute(
        "SELECT filename FROM users WHERE username=%s", (post['owner'],)
    )
    [ownder_img_url] = (cur.fetchall())

    context = {
        "img_url": f"/uploads/{post['filename']}",
        "age": post["created"],
        "owner": post["owner"],
        "owner_img_url": f"/uploads/{ownder_img_url['filename']}",
        "owner_show_url": f"/u/{post['owner']}/",
        "post_show_url": f"/p/{postid_url_slug}/",
        "url": f"/api/v1/p/{postid_url_slug}/"
    }

    return flask.jsonify(**context)
