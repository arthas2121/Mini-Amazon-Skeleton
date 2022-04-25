\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);
\COPY Category FROM 'Category.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV

\COPY ProductReview FROM 'ProductReview.csv' WITH DELIMITER ',' NULL '' CSV

\COPY SellerReview FROM 'SellerReview.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Code FROM 'Code.csv' WITH DELIMITER ',' NULL '' CSV