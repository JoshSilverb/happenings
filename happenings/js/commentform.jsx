import React from 'react';
import PropTypes from 'prop-types';

class CommentForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      comment: '',
    };
  }

  handleChange(event) {
    this.setState({ comment: event.target.value });
  }

  handleSubmitComment(event) {
    event.preventDefault();
    const { url, addComment } = this.props;
    const { comment } = this.state;

    fetch(`${url}comments/`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: comment,
      }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response);
        console.log('posting comment');
        return response.json();
      })
      .then((data) => {
        console.log('Success posting comment: ', data);

        addComment(data);
      })
      .catch((error) => console.log(error));
    this.setState({ comment: '' });
  }

  render() {
    const { comment } = this.state;
    return (
      <form className="comment-form" onSubmit={this.handleSubmitComment.bind(this)}>
        <input type="text" value={comment} onChange={(event) => { this.handleChange(event); }} />
      </form>
    );
  }
}

CommentForm.propTypes = {
  url: PropTypes.string,
  addComment: PropTypes.func,
};

CommentForm.defaultProps = {
  url: null,
  addComment: null,
};

export default CommentForm;
