import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import CommentList from './commentlist';
import CommentForm from './commentform';
import LikeButton from './likebutton';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      age: 0,
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerUrl: '',
      postUrl: '',
      comments: [],
    };
    this.addComment = this.addComment.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's basic information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => this.handleImageData(data))
      .catch((error) => console.log(error));

    // Call REST API to get comments
    fetch(`${url}comments`, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: data.comments.slice(),
        });
      })
      .catch((error) => console.log(error));
  }

  handleImageData(data) {
    this.setState({
      age: data.age,
      imgUrl: data.img_url,
      owner: data.owner,
      ownerImgUrl: data.owner_img_url,
      ownerUrl: data.owner_show_url,
      postUrl: data.post_show_url,
    });
  }

  addComment(newComment) {
    const { comments } = this.state;
    const added = comments.concat(newComment);
    this.setState({ comments: added });
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { url } = this.props;
    const {
      ownerUrl, ownerImgUrl, owner, postUrl, age, imgUrl, comments,
    } = this.state;

    // Render number of post image and post owner
    return (
      <div className="post">
        <p>
          <a href={ownerUrl}>
            <img src={ownerImgUrl} width="25" alt="" />
            <b>{owner}</b>
          </a>
          <b> - </b>
          <a href={postUrl}>{moment(age, 'YYYY-MM-DD hh:mm:ss').fromNow()}</a>
        </p>
        <div>
          <LikeButton postUrl={url} imgUrl={imgUrl} />
        </div>
        <div>
          <CommentList comments={comments} />
        </div>
        <div>
          <CommentForm addComment={this.addComment} url={url} comments={comments} />
        </div>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string,
};

Post.defaultProps = {
  url: null,
};

// export default PostList;
export default Post;
