import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'pass',
    'database': 'app',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_last_payment_status():
    connection = pymysql.connect(**DB_CONFIG)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT status FROM payment_entity ORDER BY created DESC LIMIT 1;")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    SELECT pe.status 
                    FROM order_entity oe 
                    JOIN payment_entity pe ON oe.payment_id = pe.transaction_id 
                    ORDER BY oe.created DESC LIMIT 1;
                """)
                result = cursor.fetchone()
            return result['status'] if result else None

def get_last_credit_status():
    connection = pymysql.connect(**DB_CONFIG)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT status FROM credit_request_entity ORDER BY created DESC LIMIT 1;")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    SELECT cre.status 
                    FROM order_entity oe 
                    JOIN credit_request_entity cre ON oe.credit_id = cre.bank_id 
                    ORDER BY oe.created DESC LIMIT 1;
                """)
                result = cursor.fetchone()
            return result['status'] if result else None

def clear_db():
    connection = pymysql.connect(**DB_CONFIG)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE order_entity;")
            cursor.execute("TRUNCATE TABLE payment_entity;")
            cursor.execute("TRUNCATE TABLE credit_request_entity;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()