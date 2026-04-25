CREATE DATABASE IF NOT EXISTS accounts_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE accounts_app;

CREATE TABLE IF NOT EXISTS account (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS category (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    kind VARCHAR(20) NOT NULL,
    parent_id BIGINT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_category_parent FOREIGN KEY (parent_id) REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS transaction_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    occurred_at DATETIME NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category_id BIGINT NOT NULL,
    from_account_id BIGINT NULL,
    to_account_id BIGINT NULL,
    note VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction_category FOREIGN KEY (category_id) REFERENCES category(id),
    CONSTRAINT fk_transaction_from_account FOREIGN KEY (from_account_id) REFERENCES account(id),
    CONSTRAINT fk_transaction_to_account FOREIGN KEY (to_account_id) REFERENCES account(id)
);

