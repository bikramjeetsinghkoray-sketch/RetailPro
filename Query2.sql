USE online_shopping;

INSERT INTO categories (category_name) VALUES
('Electronics'), ('Clothing'), ('Books'), ('Home & Kitchen');

INSERT INTO customers (name, email, phone, address) VALUES
('Amit Sharma', 'amit@gmail.com', '9876543210', 'Ludhiana'),
('Priya Singh', 'priya@gmail.com', '9876501234', 'Chandigarh'),
('Rahul Verma', 'rahul@gmail.com', '9812345678', 'Amritsar'),
('Neha Gupta', 'neha@gmail.com', '9898989898', 'Jalandhar');

INSERT INTO products (name, price, stock, category_id) VALUES
('Wireless Mouse', 599.00, 50, 1),
('Bluetooth Headphones', 1999.00, 30, 1),
('Cotton T-Shirt', 499.00, 100, 2),
('Jeans', 1299.00, 60, 2),
('SQL Basics Book', 350.00, 40, 3),
('Mixer Grinder', 2499.00, 20, 4);

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2026-11-01', 'Delivered'),
(2, '2026-11-05', 'Shipped'),
(1, '2026-11-10', 'Pending'),
(3, '2026-11-12', 'Delivered');

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 599.00),
(1, 5, 2, 350.00),
(2, 3, 3, 499.00),
(3, 2, 1, 1999.00),
(4, 6, 1, 2499.00);

INSERT INTO payments (order_id, amount, method, payment_date) VALUES
(1, 1299.00, 'UPI', '2026-11-01'),
(2, 1497.00, 'Card', '2026-11-05'),
(4, 2499.00, 'Cash on Delivery', '2026-11-12');

INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES
(1, 1, 5, 'Great mouse'),
(5, 1, 4, 'Helpful for beginners'),
(6, 3, 5, 'Works well');
SELECT * FROM products;
SELECT * FROM orders;