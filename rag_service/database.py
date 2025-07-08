import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
        except Error as e:
            print(f"Error connecting to MySQL Database: {e}")
            raise

    def get_all_data(self) -> List[Dict[str, Any]]:
        """
        Extracts all relevant data from the database for embedding
        Returns a list of dictionaries containing the data
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()

        cursor = self.connection.cursor(dictionary=True)
        data = []

        try:
            # Products
            cursor.execute("""
                SELECT p.*, c.CNAME as category_name, s.COMPANY_NAME as supplier_name 
                FROM product p 
                LEFT JOIN category c ON p.CATEGORY_ID = c.CATEGORY_ID 
                LEFT JOIN supplier s ON p.SUPPLIER_ID = s.SUPPLIER_ID
            """)
            products = cursor.fetchall()
            for product in products:
                data.append(
                    {
                        "type": "product",
                        "id": product["PRODUCT_ID"],
                        "content": f"Product {product['NAME']} (ID: {product['PRODUCT_ID']}) "
                        f"is a {product['category_name']} item supplied by {product['supplier_name']}. "
                        f"Description: {product['DESCRIPTION']}. "
                        f"Current stock: {product['QTY_STOCK']}, Price: ${product['PRICE']}",
                    }
                )

            # Customers
            cursor.execute("SELECT * FROM customer")
            customers = cursor.fetchall()
            for customer in customers:
                data.append(
                    {
                        "type": "customer",
                        "id": customer["CUST_ID"],
                        "content": f"Customer {customer['FIRST_NAME']} {customer['LAST_NAME']} "
                        f"(ID: {customer['CUST_ID']}) "
                        f"Contact: {customer['PHONE_NUMBER']}",
                    }
                )

            # Suppliers
            cursor.execute("""
                SELECT s.*, l.PROVINCE, l.CITY 
                FROM supplier s 
                LEFT JOIN location l ON s.LOCATION_ID = l.LOCATION_ID
            """)
            suppliers = cursor.fetchall()
            for supplier in suppliers:
                data.append(
                    {
                        "type": "supplier",
                        "id": supplier["SUPPLIER_ID"],
                        "content": f"Supplier {supplier['COMPANY_NAME']} "
                        f"(ID: {supplier['SUPPLIER_ID']}) "
                        f"is located in {supplier['CITY']}, {supplier['PROVINCE']}. "
                        f"Contact: {supplier['PHONE_NUMBER']}",
                    }
                )

            # Transactions with details
            cursor.execute("""
                SELECT 
                    t.TRANS_ID,
                    t.DATE,
                    t.GRANDTOTAL,
                    td.PRODUCTS,
                    td.QTY,
                    td.PRICE as ITEM_PRICE,
                    td.EMPLOYEE,
                    td.ROLE,
                    c.FIRST_NAME,
                    c.LAST_NAME
                FROM transaction t
                JOIN transaction_details td ON t.TRANS_D_ID = td.TRANS_D_ID
                JOIN customer c ON t.CUST_ID = c.CUST_ID
                ORDER BY t.TRANS_ID DESC
                LIMIT 1000
            """)
            transactions = cursor.fetchall()
            for transaction in transactions:
                data.append(
                    {
                        "type": "transaction",
                        "id": transaction["TRANS_ID"],
                        "content": f"Transaction (ID: {transaction['TRANS_ID']}) "
                        f"by customer {transaction['FIRST_NAME']} {transaction['LAST_NAME']} "
                        f"for product {transaction['PRODUCTS']} "
                        f"quantity: {transaction['QTY']}, "
                        f"price: ${transaction['ITEM_PRICE']}, "
                        f"total: ${transaction['GRANDTOTAL']}, "
                        f"date: {transaction['DATE']}, "
                        f"processed by {transaction['EMPLOYEE']} ({transaction['ROLE']})",
                    }
                )

        except Error as e:
            print(f"Error extracting data from database: {e}")
            raise
        finally:
            cursor.close()

        return data

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
