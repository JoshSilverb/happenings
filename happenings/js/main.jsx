import React from 'react';
import ReactDOM from 'react-dom';
import PostList from './postlist';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <PostList />,
  document.getElementById('reactEntry'),
);
