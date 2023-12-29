import React from 'react';
import PropTypes from 'prop-types';

class LikeButton extends React.Component {
  /* Displays like button and number of likes */
  constructor(props) {
    super(props);
    this.state = {
      numLikes: 0,
      userLiked: 0,
      buttonText: '',
      likeText: '',
    };

    // I think I need these for some reason? maybe to access props??
    this.updateText = this.updateText.bind(this);
    this.handleOnClick = this.handleOnClick.bind(this);
    this.handleLike = this.handleLike.bind(this);
    this.handleUnlike = this.handleUnlike.bind(this);
  }

  componentDidMount() {
    // Call REST API to get likes info
    const { postUrl } = this.props;
    fetch(`${postUrl}likes/`, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // Set state and initial like button text from fetch data
        this.setState({
          numLikes: data.likes_count,
          userLiked: data.logname_likes_this,
        });
        this.updateText();
      })
      .catch((error) => console.log(error));
  }

  handleOnClick() {
    // button click handler
    const { userLiked } = this.state;
    if (userLiked === 1) {
      this.handleUnlike();
    } else {
      this.handleLike();
    }
  }

  handleLike() {
    // Call REST API to like
    const { userLiked } = this.state;

    if (userLiked === 0) {
      const { postUrl } = this.props;
      const { numLikes } = this.state;
      fetch(`${postUrl}likes/`, {
        credentials: 'same-origin',
        method: 'POST',
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          // update state and text
          console.log('updating state to reflect like');
          this.setState({
            numLikes: numLikes + 1,
            userLiked: 1,
          });
          this.updateText();
        })
        .catch((error) => console.log(error));
    }
  }

  handleUnlike() {
    // Call REST API to delete like
    const { postUrl } = this.props;
    const { numLikes } = this.state;
    fetch(`${postUrl}likes/`, { credentials: 'same-origin', method: 'DELETE' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // update state and text
        console.log('updating state to reflect unlike');
        this.setState({
          numLikes: numLikes - 1,
          userLiked: 0,
        });
        this.updateText();
      })
      .catch((error) => console.log(error));
  }

  updateText() {
    // update both the likes text and the text that appears on the button
    const { userLiked, numLikes } = this.state;
    if (userLiked === 1) {
      this.setState({ buttonText: 'unlike' });
    } else {
      this.setState({ buttonText: 'like' });
    }
    // Like "proper English" processing
    let text = '';
    if (numLikes === 1) {
      text = '1 like';
    } else {
      text = `${numLikes} likes`;
    }
    this.setState({ likeText: text });
  }

  render() {
    const { imgUrl } = this.props;
    const { buttonText, likeText } = this.state;
    return (
      <div>
        <p><img src={imgUrl} style={{ marginLeft: 'auto', marginRight: 'auto', width: '50%' }} alt="" onDoubleClick={this.handleLike} /></p>
        <p><button type="button" className="like-unlike-button" onClick={this.handleOnClick}>{buttonText}</button></p>
        <p>{likeText}</p>
      </div>
    );
  }
}

LikeButton.propTypes = {
  postUrl: PropTypes.string,
  imgUrl: PropTypes.string,
};

LikeButton.defaultProps = {
  postUrl: null,
  imgUrl: null,
};

export default LikeButton;
