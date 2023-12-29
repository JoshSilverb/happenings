import React from 'react';
import PropTypes from 'prop-types';

class CommentList extends React.PureComponent {
  render() {
    const { comments } = this.props;
    const commentList = comments.map((post) => (
      <div key={post.commentid}>
        <b><a href={post.owner_show_url}>{post.owner}</a></b>
        {` ${post.text}`}
      </div>
    ));
    return (<div>{commentList}</div>);
  }
}

CommentList.propTypes = {
  comments: PropTypes.arrayOf(PropTypes.object),
};

CommentList.defaultProps = {
  comments: null,
};

export default CommentList;
