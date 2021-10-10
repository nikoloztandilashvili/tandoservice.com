import sqlite3


def create_tables(connection):
    connection.execute('''
        CREATE TABLE IF NOT EXISTS food (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR NOT NULL,
            image_link VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            price INTEGER NOT NULL
        )''')

    connection.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR NOT NULL,
            password VARCHAR NOT NULL
        )''')

    connection.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER NOT NULL PRIMARY KEY,
            food_id INTEGER REFERENCES food,
            fullname VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            address VARCHAR NOT NULL,
            payment_method VARCHAR NOT NULL
        )''')


def create_admin(email, password, connection):
    connection.execute('''
        INSERT INTO admins (email, password)
        VALUES (?, ?)
    ''', (email, password))

    connection.commit()

def main():
    connection = sqlite3.connect('foodservice.db')

    create_tables(connection)
    create_admin('test@email.com', 'password', connection)

    connection.close()

if __name__ == '__main__':
    main()
