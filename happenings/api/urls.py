"""REST API to return resource URLs."""
import flask
import insta485


@insta485.app.route('/api/v1/', methods=["GET"])
def get_urls():
    """Return urls for  on postid."""
    context = {
        "posts": "/api/v1/p/",
        "url": "/api/v1/"
    }

    return flask.jsonify(**context)
