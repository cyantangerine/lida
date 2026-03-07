-- SQLite 数据库建表脚本
-- Database: lida.db

-- 表结构：t_chat
DROP TABLE IF EXISTS t_chat;
CREATE TABLE t_chat (
  id INTEGER PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  name TEXT NOT NULL,
  data_filename TEXT DEFAULT NULL,
  dataset_name TEXT DEFAULT NULL,
  dataset_description TEXT DEFAULT NULL,
  field_names TEXT DEFAULT NULL,
  fields TEXT DEFAULT NULL,
  extra_hint_interest TEXT DEFAULT NULL,
  create_time DATETIME DEFAULT NULL,
  update_time DATETIME DEFAULT NULL
);

-- 表结构：t_edit
DROP TABLE IF EXISTS t_edit;
CREATE TABLE t_edit (
  id INTEGER PRIMARY KEY,
  goal_id INTEGER DEFAULT NULL,
  index INTEGER DEFAULT NULL,
  edit TEXT DEFAULT NULL,
  create_time DATETIME DEFAULT NULL,
  update_time DATETIME DEFAULT NULL
);

-- 表结构：t_evaluate
DROP TABLE IF EXISTS t_evaluate;
CREATE TABLE t_evaluate (
  id INTEGER PRIMARY KEY,
  goal_id INTEGER DEFAULT NULL,
  evaluate TEXT DEFAULT NULL,
  create_time DATETIME DEFAULT NULL,
  update_time DATETIME DEFAULT NULL
);

-- 表结构：t_explain
DROP TABLE IF EXISTS t_explain;
CREATE TABLE t_explain (
  id INTEGER PRIMARY KEY,
  goal_id INTEGER DEFAULT NULL,
  explanation TEXT DEFAULT NULL,
  create_time DATETIME DEFAULT NULL,
  update_time DATETIME DEFAULT NULL
);

-- 表结构：t_goal
DROP TABLE IF EXISTS t_goal;
CREATE TABLE t_goal (
  id INTEGER PRIMARY KEY,
  chat_id INTEGER NOT NULL,
  index INTEGER DEFAULT NULL,
  question TEXT DEFAULT NULL,
  visualization TEXT DEFAULT NULL,
  rationale TEXT DEFAULT NULL,
  is_auto INTEGER DEFAULT NULL,
  library TEXT DEFAULT NULL,
  code TEXT,
  explanation TEXT DEFAULT NULL,
  create_time DATETIME DEFAULT NULL,
  update_time DATETIME DEFAULT NULL
);

-- 表结构：users
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  create_time DATETIME NOT NULL,
  update_time DATETIME DEFAULT NULL
);

-- 创建索引
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_id ON users(id);
