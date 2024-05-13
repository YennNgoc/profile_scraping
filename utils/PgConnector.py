import psycopg2
from psycopg2 import Error

def get_connection():
    """
    init connection
    """
    connection = psycopg2.connect(user="da",
                                  password="da123",
                                  host="localhost",
                                  port="5432",
                                  database="da")
    return connection

def close_connection(connection):
    """
    close connection
    """
    if connection:
        connection.close()

def insert_data(data):
    """
    dynamic schema insert query with data binding posgreSQL
    """
    print('insert', data)
    try:
        pg_conn = get_connection()
        cursor = pg_conn.cursor()

        columns = ','.join([k for k in data[0]])
        place_holers = ','.join(['%s' for _ in range(len(data[0]))])

        sql_query = f"INSERT INTO candidate_profile({columns}) VALUES ({place_holers})"
        print(sql_query)

        # Execute the query with the data to insert
        data = [tuple(item.values()) for item in data]
        cursor.executemany(sql_query, data)
        # Commit the transaction
        pg_conn.commit()

        print("Data inserted successfully")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        # Close the database connection
        if pg_conn:
            cursor.close()
            close_connection(pg_conn)
            print("PostgreSQL connection is closed")

# get_connection()