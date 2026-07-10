USE SalesAnalytics_DB;
GO

-- Customers Table
CREATE TABLE Customers
(
    customer_id VARCHAR(50) NOT NULL,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INT NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state CHAR(2) NOT NULL,

    CONSTRAINT PK_Customers
        PRIMARY KEY (customer_id)
);
GO

-- Orders Table
CREATE TABLE Orders
(
    order_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_purchase_timestamp DATETIME2 NOT NULL,
    order_approved_at DATETIME2 NULL,
    order_delivered_carrier_date DATETIME2 NULL,
    order_delivered_customer_date DATETIME2 NULL,
    order_estimated_delivery_date DATETIME2 NOT NULL,

    CONSTRAINT PK_Orders
        PRIMARY KEY (order_id),

    CONSTRAINT FK_Orders_Customers
        FOREIGN KEY (customer_id)
        REFERENCES Customers(customer_id)
);
GO

CREATE TABLE OrderItems
(
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    shipping_limit_date DATETIME2 NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    freight_value DECIMAL(10,2) NOT NULL,

    CONSTRAINT PK_OrderItems
        PRIMARY KEY (order_id, order_item_id),

    CONSTRAINT FK_OrderItems_Orders
        FOREIGN KEY (order_id)
        REFERENCES Orders(order_id)
);
GO

CREATE TABLE Products
(
    product_id VARCHAR(50) NOT NULL,
    product_category_name VARCHAR(100) NULL,
    product_name_length INT NULL,
    product_description_length INT NULL,
    product_photos_qty INT NULL,
    product_weight_g DECIMAL(10,2) NULL,
    product_length_cm DECIMAL(10,2) NULL,
    product_height_cm DECIMAL(10,2) NULL,
    product_width_cm DECIMAL(10,2) NULL,
    
    CONSTRAINT PK_Products
        PRIMARY KEY (product_id)
);
GO

CREATE TABLE Sellers
(
    seller_id VARCHAR(50) NOT NULL,
    seller_zip_code_prefix INT NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state CHAR(2) NOT NULL,

    CONSTRAINT PK_Sellers
        PRIMARY KEY (seller_id)
);
GO

CREATE TABLE Payments
(
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value DECIMAL(10,2) NOT NULL,

    CONSTRAINT PK_Payments
        PRIMARY KEY (order_id, payment_sequential),

    CONSTRAINT FK_Payments_Orders
        FOREIGN KEY (order_id)
        REFERENCES Orders(order_id)
);
GO

CREATE TABLE Reviews
(
    review_key INT IDENTITY(1,1) NOT NULL,

    review_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    review_score TINYINT NOT NULL,
    review_comment_title NVARCHAR(255) NULL,
    review_comment_message NVARCHAR(MAX) NULL,
    review_creation_date DATETIME2 NOT NULL,
    review_answer_timestamp DATETIME2 NOT NULL,

    CONSTRAINT PK_Reviews
        PRIMARY KEY (review_key),

    CONSTRAINT FK_Reviews_Orders
        FOREIGN KEY (order_id)
        REFERENCES Orders(order_id)
);
GO

CREATE TABLE ProductCategoryTranslation
(
    product_category_name VARCHAR(100) NOT NULL,
    product_category_name_english VARCHAR(100) NOT NULL,

    CONSTRAINT PK_ProductCategoryTranslation
      PRIMARY KEY (product_category_name)
);
GO

ALTER TABLE OrderItems
ADD CONSTRAINT FK_OrderItems_Products
FOREIGN KEY (product_id)
REFERENCES Products(product_id);
GO



ALTER TABLE OrderItems
ADD CONSTRAINT FK_OrderItems_Sellers
FOREIGN KEY (seller_id)
REFERENCES Sellers(seller_id);
GO

ALTER TABLE Products
ADD CONSTRAINT FK_Products_CategoryTranslation
FOREIGN KEY (product_category_name)
REFERENCES ProductCategoryTranslation(product_category_name);
GO