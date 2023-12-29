
CREATE TABLE users(
  username VARCHAR(20) PRIMARY KEY,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL,
  filename VARCHAR(128) NOT NULL,
  password VARCHAR(256) NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts(
  postid SERIAL PRIMARY KEY,
  filename VARCHAR(128) NOT NULL,
  owner VARCHAR(20) NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner) REFERENCES users (username) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
);

CREATE TABLE following(
  username1 VARCHAR(20) NOT NULL,
  username2 VARCHAR(20) NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (username1, username2),
  FOREIGN KEY (username1) REFERENCES users (username) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE,
  FOREIGN KEY (username2) REFERENCES users (username) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
);

CREATE TABLE comments(
  commentid SERIAL PRIMARY KEY,
  owner VARCHAR(20) NOT NULL,
  postid SERIAL NOT NULL,
  text VARCHAR(1024) NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner) REFERENCES users (username) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE,
  FOREIGN KEY (postid) REFERENCES posts (postid) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
);

CREATE TABLE likes(
  owner VARCHAR(20) NOT NULL,
  postid SERIAL NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (owner, postid),
  FOREIGN KEY (owner) REFERENCES users (username) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE,
  FOREIGN KEY (postid) REFERENCES posts (postid) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
)
