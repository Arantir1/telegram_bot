import psycopg2
import datetime
import config

def create_db_table():
    connection = psycopg2.connect(host=config.Database.host, user=config.Database.user,
                                 password=config.Database.password, database=config.Database.database)
    # cursor = connection.cursor(buffered=True)
    cursor = connection.cursor()
    try:
        select_sql = "SELECT * FROM dictionary;"
        cursor.execute(select_sql)
        res = cursor.fetchone()
        print("Res is: ",res)
        print("Table already exist!")
    except psycopg2.ProgrammingError:
        connection.rollback()
        create_table_sql = "CREATE TABLE dictionary (word VARCHAR(50), cid VARCHAR(10), last_repeat DATETIME, iteration INTEGER, next_repeat DATETIME);"
        cursor.execute(create_table_sql)
        connection.commit()
        print("Table has created!")
    connection.close()


def insert_word(message):
    connection = psycopg2.connect(host=config.Database.host, user=config.Database.user,
                                 password=config.Database.password, database=config.Database.database)
    cursor = connection.cursor(buffered=True)
    last_dt = datetime.datetime.now()
    new_dt = last_dt + datetime.timedelta(days=1)
    cursor.execute("INSERT INTO dictionary VALUES (%(word)s, \
                                                %(cid)s, \
                                                %(last_repeat)s, \
                                                %(iteration)s, \
                                                %(next_repeat)s);",
    {'word': message.text, 'cid': message.chat.id, 'last_repeat': last_dt, 'iteration': 1, 'next_repeat': new_dt})
    connection.commit()
    connection.close()

def get_words_by_cid(cid):
    connection = psycopg2.connect(host=config.Database.host, user=config.Database.user,
                                 password=config.Database.password, database=config.Database.database)
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT word from dictionary WHERE cid = %(cid)s;", {'cid': cid})
    words = []
    word = cursor.fetchone()
    while word is not None:
        words.append(word[0])
        word = cursor.fetchone()
    connection.close()
    return words

def get_words():
    connection = psycopg2.connect(host=config.Database.host, user=config.Database.user,
                                 password=config.Database.password, database=config.Database.database)
    cursor = connection.cursor(buffered=True)
    res = {}
    cids = []
    cursor.execute("SELECT DISTINCT cid FROM dictionary;")
    row = cursor.fetchone()
    # print(row)
    while row is not None:
        cids.append(row[0])
        row = cursor.fetchone()
    # print (cids)
    for cid in cids:
        res.update({cid: get_words_by_cid(cid)})
    connection.close()
    return res

