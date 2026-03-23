-- ─────────────────────────────────────────────────────────────────
-- Personalized Daily Routine Tracker – Database Schema
-- Run this once to initialise the database.
-- ─────────────────────────────────────────────────────────────────

CREATE DATABASE IF NOT EXISTS routine_tracker
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE routine_tracker;

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id         INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username   VARCHAR(50)  NOT NULL UNIQUE,
  password   VARCHAR(64)  NOT NULL,            -- SHA-256 hex digest
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Daily logs (one row per user per day)
CREATE TABLE IF NOT EXISTS daily_logs (
  id                INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id           INT          NOT NULL,
  log_date          DATE         NOT NULL,
  tasks_completed   TINYINT      NOT NULL DEFAULT 0,
  discipline_score  SMALLINT     NOT NULL DEFAULT 0,
  reflection        TEXT,
  created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_user_date (user_id, log_date),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Completed task ids per log entry
CREATE TABLE IF NOT EXISTS completed_tasks (
  id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  log_id   INT          NOT NULL,
  task_id  VARCHAR(50)  NOT NULL,
  FOREIGN KEY (log_id) REFERENCES daily_logs(id) ON DELETE CASCADE
);
