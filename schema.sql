-- Active: 1758872841607@@127.0.0.1@3306@stock_db
-- SQLINES DEMO FOR mysql
-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `hashed_password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `stock_info`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `stock_info` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `symbol` VARCHAR(10) NOT NULL,
  `company_name` VARCHAR(255) NULL DEFAULT '',
  `exchange` VARCHAR(50) NULL DEFAULT '',
  `sector` VARCHAR(100) NULL DEFAULT '',
  `industry` VARCHAR(100) NULL DEFAULT '',
  `description` TEXT NULL,
  `ipo_date` DATE NULL,
  `last_updated` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uq_symbol` (`symbol` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `stock_daily_data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `stock_daily_data` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stock_id` BIGINT UNSIGNED NOT NULL,
  `trade_date` DATE NOT NULL,
  `open_price` DECIMAL(12, 4) NOT NULL,
  `high_price` DECIMAL(12, 4) NOT NULL,
  `low_price` DECIMAL(12, 4) NOT NULL,
  `close_price` DECIMAL(12, 4) NOT NULL,
  `volume` BIGINT UNSIGNED NOT NULL,
  `amount` BIGINT UNSIGNED NULL,
  `creation_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_trade_date` (`trade_date` ASC) VISIBLE,
  UNIQUE INDEX `uq_stock_date` (`stock_id` ASC, `trade_date` ASC) VISIBLE,
  CONSTRAINT `fk_stock_daily_data_stock_info`
    FOREIGN KEY (`stock_id`)
    REFERENCES `stock_info` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `user_watchlist`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `user_watchlist` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `stock_id` BIGINT UNSIGNED NOT NULL,
  `added_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uq_user_stock` (`user_id` ASC, `stock_id` ASC) VISIBLE,
  INDEX `fk_user_watchlist_stock_info_idx` (`stock_id` ASC) VISIBLE,
  CONSTRAINT `fk_user_watchlist_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_watchlist_stock_info`
    FOREIGN KEY (`stock_id`)
    REFERENCES `stock_info` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
