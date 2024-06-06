-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema e_wallet
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema e_wallet
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `e_wallet` DEFAULT CHARACTER SET latin1 ;
USE `e_wallet` ;

-- -----------------------------------------------------
-- Table `e_wallet`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(20) NOT NULL,
  `password` TEXT NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `balance` FLOAT NOT NULL DEFAULT 0,
  `phone_number` VARCHAR(10) NOT NULL,
  `is_admin` TINYINT(4) NULL DEFAULT 0,
  `create_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP(),
  `status` ENUM('pending', 'activated', 'blocked') NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  UNIQUE INDEX `phone_number_UNIQUE` (`phone_number` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 13
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `e_wallet`.`cards`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`cards` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `card_number` VARCHAR(16) NOT NULL,
  `cvv` VARCHAR(3) NOT NULL,
  `card_holder` VARCHAR(30) NOT NULL,
  `expiration_date` DATE NOT NULL,
  `card_status` ENUM('active', 'not active') NULL DEFAULT 'active',
  `user_id` INT(11) NOT NULL,
  `balance` FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_cards_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_cards_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 14
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `e_wallet`.`categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`categories` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `e_wallet`.`contacts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`contacts` (
  `users_id` INT(11) NOT NULL,
  `contact_user_id` INT(11) NOT NULL,
  INDEX `fk_contacts_users1_idx` (`users_id` ASC) VISIBLE,
  INDEX `fk_contacts_users2_idx` (`contact_user_id` ASC) VISIBLE,
  CONSTRAINT `fk_contacts_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contacts_users2`
    FOREIGN KEY (`contact_user_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `e_wallet`.`recurring_transactions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`recurring_transactions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `recurring_transaction_date` DATETIME NULL DEFAULT CURRENT_TIMESTAMP(),
  `next_payment` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `status` ENUM('pending', 'confirmed', 'declined') NULL DEFAULT 'pending',
  `condition` ENUM('edited', 'sent', 'cancelled') NULL DEFAULT 'edited',
  `amount` FLOAT NOT NULL,
  `sender_id` INT(11) NOT NULL,
  `receiver_id` INT(11) NOT NULL,
  `categories_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_recurring_transactions_users1_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_recurring_transactions_categories1_idx` (`categories_id` ASC) VISIBLE,
  INDEX `fk_recurring_transactions_users2_idx` (`receiver_id` ASC) VISIBLE,
  CONSTRAINT `fk_recurring_transactions_categories1`
    FOREIGN KEY (`categories_id`)
    REFERENCES `e_wallet`.`categories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_recurring_transactions_users1`
    FOREIGN KEY (`sender_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_recurring_transactions_users2`
    FOREIGN KEY (`receiver_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `e_wallet`.`transactions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`transactions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `status` ENUM('pending', 'confirmed', 'declined') NOT NULL DEFAULT 'pending',
  `condition` ENUM('edited', 'sent', 'cancelled') NOT NULL DEFAULT 'edited',
  `transaction_date` DATETIME NULL DEFAULT CURRENT_TIMESTAMP(),
  `amount` FLOAT NOT NULL,
  `category_name` VARCHAR(45) NOT NULL DEFAULT 'no category',
  `sender_id` INT(11) NOT NULL,
  `receiver_id` INT(11) NOT NULL,
  `cards_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_transactions_users1_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_transactions_users2_idx` (`receiver_id` ASC) VISIBLE,
  INDEX `fk_transactions_cards1_idx` (`cards_id` ASC) VISIBLE,
  CONSTRAINT `fk_transactions_cards1`
    FOREIGN KEY (`cards_id`)
    REFERENCES `e_wallet`.`cards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transactions_users1`
    FOREIGN KEY (`sender_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transactions_users2`
    FOREIGN KEY (`receiver_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 31
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `e_wallet`.`users_has_categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e_wallet`.`users_has_categories` (
  `users_id` INT(11) NOT NULL,
  `categories_id` INT(11) NOT NULL,
  PRIMARY KEY (`users_id`, `categories_id`),
  INDEX `fk_users_has_categories_categories1_idx` (`categories_id` ASC) VISIBLE,
  INDEX `fk_users_has_categories_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_categories_categories1`
    FOREIGN KEY (`categories_id`)
    REFERENCES `e_wallet`.`categories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_categories_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `e_wallet`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
