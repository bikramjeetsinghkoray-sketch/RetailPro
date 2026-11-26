USE online_shopping;

SELECT * FROM products;

SELECT name, price FROM products WHERE price < 1000;

SELECT name, price FROM products ORDER BY price DESC;
SELECT p.name AS product, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id;
SELECT o.order_id, c.name AS customer, o.order_date, o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
SELECT o.order_id, c.name AS customer, p.name AS product, oi.quantity, oi.price
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;
SELECT c.category_name, COUNT(p.product_id) AS total_products
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_name;
SELECT c.name, SUM(oi.quantity * oi.price) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.name
ORDER BY total_spent DESC;
SELECT p.name, SUM(oi.quantity) AS total_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.name
ORDER BY total_sold DESC;
SELECT name, price FROM products
WHERE price > (SELECT AVG(price) FROM products);
CREATE VIEW order_summary AS
SELECT o.order_id, c.name AS customer, p.name AS product,
       oi.quantity, (oi.quantity * oi.price) AS item_total, o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;
SELECT * FROM order_summary;
SELECT product_id, name, stock FROM products WHERE product_id = 1;
DELIMITER //
CREATE TRIGGER reduce_stock
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET stock = stock - NEW.quantity
    WHERE product_id = NEW.product_id;
END //
DELIMITER ;
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (3, 1, 2, 599.00);

SELECT product_id, name, stock FROM products WHERE product_id = 1;