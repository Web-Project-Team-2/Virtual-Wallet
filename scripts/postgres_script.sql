-- PostgreSQL schema creation

-- Create schema
CREATE SCHEMA IF NOT EXISTS e_wallet;

-- Use schema
SET search_path TO e_wallet;

-- Table `users`
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(20) NOT NULL UNIQUE,
  password TEXT NOT NULL,
  email VARCHAR(45) NOT NULL UNIQUE,
  balance FLOAT NOT NULL DEFAULT 0,
  phone_number VARCHAR(10) NOT NULL UNIQUE,
  is_admin BOOLEAN NULL DEFAULT FALSE,
  create_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  status TEXT CHECK (status IN ('pending', 'activated', 'blocked')) NULL DEFAULT 'pending'
);

-- Table `cards`
CREATE TABLE IF NOT EXISTS cards (
  id SERIAL PRIMARY KEY,
  card_number VARCHAR(16) NOT NULL UNIQUE,
  cvv VARCHAR(3) NOT NULL,
  card_holder VARCHAR(30) NOT NULL,
  expiration_date DATE NOT NULL,
  card_status TEXT CHECK (card_status IN ('active', 'not active')) NULL DEFAULT 'active',
  user_id INT NOT NULL,
  balance FLOAT NOT NULL DEFAULT 0,
  CONSTRAINT fk_cards_users FOREIGN KEY (user_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- Table `categories`
CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(45) NOT NULL UNIQUE
);

-- Table `contacts`
CREATE TABLE IF NOT EXISTS contacts (
  users_id INT NOT NULL,
  contact_user_id INT NOT NULL,
  PRIMARY KEY (users_id, contact_user_id),
  CONSTRAINT fk_contacts_users1 FOREIGN KEY (users_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_contacts_users2 FOREIGN KEY (contact_user_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- Table `recurring_transactions`
CREATE TABLE IF NOT EXISTS recurring_transactions (
  id SERIAL PRIMARY KEY,
  recurring_transaction_date TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  next_payment TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status TEXT CHECK (status IN ('pending', 'confirmed', 'declined')) NULL DEFAULT 'pending',
  condition TEXT CHECK (condition IN ('edited', 'sent', 'cancelled')) NULL DEFAULT 'edited',
  amount FLOAT NOT NULL,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  categories_id INT NOT NULL,
  CONSTRAINT fk_recurring_transactions_categories1 FOREIGN KEY (categories_id)
    REFERENCES categories (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_recurring_transactions_users1 FOREIGN KEY (sender_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_recurring_transactions_users2 FOREIGN KEY (receiver_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- Table `transactions`
CREATE TABLE IF NOT EXISTS transactions (
  id SERIAL PRIMARY KEY,
  status TEXT CHECK (status IN ('pending', 'confirmed', 'declined')) NOT NULL DEFAULT 'pending',
  condition TEXT CHECK (condition IN ('edited', 'sent', 'cancelled')) NOT NULL DEFAULT 'edited',
  transaction_date TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  amount FLOAT NOT NULL,
  category_name VARCHAR(45) NOT NULL DEFAULT 'no category',
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  cards_id INT NOT NULL,
  CONSTRAINT fk_transactions_cards1 FOREIGN KEY (cards_id)
    REFERENCES cards (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_transactions_users1 FOREIGN KEY (sender_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_transactions_users2 FOREIGN KEY (receiver_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- Table `users_has_categories`
CREATE TABLE IF NOT EXISTS users_has_categories (
  users_id INT NOT NULL,
  categories_id INT NOT NULL,
  PRIMARY KEY (users_id, categories_id),
  CONSTRAINT fk_users_has_categories_categories1 FOREIGN KEY (categories_id)
    REFERENCES categories (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_users_has_categories_users1 FOREIGN KEY (users_id)
    REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);
