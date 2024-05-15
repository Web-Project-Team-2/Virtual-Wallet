INSERT INTO `e_wallet`.`users` 
(`username`, `password`, `email`, `phone_number`, `is_admin`, `create_at`, `status`) VALUES
('john_doe', 'Pass@word1', 'john.doe@example.com', '1234567890', 0, '2024-05-01 12:00:00', 'activated'),
('jane_smith', 'Strong*Pass2', 'jane.smith@example.com', '0987654321', 0, '2024-05-02 12:00:00', 'activated'),
('admin_user', 'Admin$1234', 'admin@example.com', '1122334455', 1, '2024-05-03 12:00:00', 'activated'),
('bob_brown', 'Secure@123', 'bob.brown@example.com', '2233445566', 0, '2024-05-04 12:00:00', 'pending'),
('alice_white', 'Pass+4567', 'alice.white@example.com', '3344556677', 0, '2024-05-05 12:00:00', 'blocked'),
('charlie_black', 'P@ssw0rd789', 'charlie.black@example.com', '4455667788', 0, '2024-05-06 12:00:00', 'activated'),
('dave_green', 'Gr3at*Pass', 'dave.green@example.com', '5566778899', 0, '2024-05-07 12:00:00', 'pending'),
('eve_red', 'MyP@ssword!', 'eve.red@example.com', '6677889900', 0, '2024-05-08 12:00:00', 'activated'),
('frank_blue', 'Blue$P@ss', 'frank.blue@example.com', '7788990011', 0, '2024-05-09 12:00:00', 'blocked'),
('grace_yellow', 'Y3ll0wP@ss', 'grace.yellow@example.com', '8899001122', 0, '2024-05-10 12:00:00', 'pending');
 
 
INSERT INTO `e_wallet`.`cards` 
(`card_number`, `cvv`, `card_holder`, `expiration_date`, `card_status`, `user_id`) VALUES
('1234567890123456', '123', 'John Doe', '2025-06-01', 'active', 1),
('2345678901234567', '234', 'Jane Smith', '2024-12-01', 'active', 2),
('3456789012345678', '345', 'Admin User', '2026-01-01', 'active', 3),
('4567890123456789', '456', 'Bob Brown', '2025-05-01', 'not active', 4),
('5678901234567890', '567', 'Alice White', '2024-11-01', 'active', 5),
('6789012345678901', '678', 'Charlie Black', '2026-03-01', 'active', 6),
('7890123456789012', '789', 'Dave Green', '2025-07-01', 'not active', 7),
('8901234567890123', '890', 'Eve Red', '2024-10-01', 'active', 8),
('9012345678901234', '901', 'Frank Blue', '2026-02-01', 'not active', 9),
('0123456789012345', '012', 'Grace Yellow', '2025-08-01', 'active', 10);
 
 
INSERT INTO `e_wallet`.`categories` (`name`) VALUES
('Rent'),
('Utilities'),
('Eating Out'),
('Groceries'),
('Entertainment'),
('Transportation'),
('Healthcare'),
('Education'),
('Gifts'),
('Savings');
 
INSERT INTO `e_wallet`.`contacts` (`users_id`, `contact_user_id`) VALUES
(1, 2),
(1, 3),
(2, 4),
(2, 5),
(3, 6),
(3, 7),
(4, 8),
(4, 9),
(5, 10),
(6, 1);
 
 
INSERT INTO `e_wallet`.`transactions` 
(`status`, `transaction_date`, `amount`, `next_payment`, `categories_id`, `sender_id`, `receiver_id`, `cards_id`) VALUES
('confirmed', '2024-05-01 12:00:00', 150.00, '2024-06-01 12:00:00', 1, 1, 2, 1),
('pending', '2024-05-02 13:00:00', 75.50, '2024-06-02 13:00:00', 2, 2, 3, 2),
('declined', '2024-05-03 14:00:00', 200.75, '2024-06-03 14:00:00', 3, 3, 4, 3),
('confirmed', '2024-05-04 15:00:00', 300.00, '2024-06-04 15:00:00', 4, 4, 5, 4),
('pending', '2024-05-05 16:00:00', 50.25, '2024-06-05 16:00:00', 5, 5, 6, 5),
('confirmed', '2024-05-06 17:00:00', 100.00, '2024-06-06 17:00:00', 6, 6, 7, 6),
('declined', '2024-05-07 18:00:00', 400.50, '2024-06-07 18:00:00', 7, 7, 8, 7),
('confirmed', '2024-05-08 19:00:00', 250.75, '2024-06-08 19:00:00', 8, 8, 9, 8),
('pending', '2024-05-09 20:00:00', 125.00, '2024-06-09 20:00:00', 9, 9, 10, 9),
('confirmed', '2024-05-10 21:00:00', 175.25, '2024-06-10 21:00:00', 10, 10, 1, 10);
 
 
INSERT INTO `e_wallet`.`users_has_categories` (`users_id`, `categories_id`) VALUES
(1, 1),
(1, 2),
(2, 3),
(2, 4),
(3, 5),
(3, 6),
(4, 7),
(4, 8),
(5, 9),
(5, 10);