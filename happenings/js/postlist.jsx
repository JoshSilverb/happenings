import React from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class PostList extends React.Component {
  /* Displays all of the posts, comments, likes, buttons, etc */
  constructor(props) {
    super(props);
    this.state = {
      next: '/api/v1/p/',
      posts: Array(0).fill(null),
    };
  }

  componentDidMount() {
    // Make initial fetch request to have enough posts to scroll thru
    fetch('/api/v1/p/', { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          posts: data.results.slice(),
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // Put a bunch of Post objects into the thing
    const items = this.state;
    return (
      <div>
        <InfiniteScroll
          dataLength={items.posts.length}
          next={() => {
            fetch(items.next, { credentials: 'same-origin' })
              .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
              })
              .then((data) => {
                const oldPosts = items.posts;
                this.setState({
                  posts: oldPosts.concat(data.results.slice()),
                  next: data.next,
                });
              })
              .catch((error) => console.log(error));
          }}
          hasMore={!(items.next === '')}
          loader={<h4>Loading...</h4>}
        >
          {items.posts.map((tuple) => (
            <div key={tuple.postid}>
              <Post url={tuple.url} key={tuple.postid} />
            </div>
          ))}
        </InfiniteScroll>
      </div>
    );
  }
}

export default PostList;
