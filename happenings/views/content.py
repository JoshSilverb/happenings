"""
Insta485 serving images and content in /var/.

URLs include:
/uploads/
"""
import flask
import insta485


@insta485.app.route('/uploads/<filename>', methods=['GET'])
def serve_image(filename):
    """Serve images from /var/uploads/."""
    # If user isn't logged in, redirect to login
    if "username" not in flask.session or not flask.session["username"]:
        flask.abort(403)
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], filename)
