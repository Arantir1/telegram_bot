# import psycopg2
import datetime
import config
from sqlalchemy import create_engine, exc
class Mydb():

    __engine = None

    def __init__(self):
        self.__engine = create_engine("postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s",
            {
                'user':config.user,
                'password':config.password,
                'host':config.host,
                'port':config.port,
                'database':config.database
            }
        ) 

    def create_db_table(self):
        try:
            connection = self.__engine.connect()
            res = connection.execute("SELECT * FROM dictionary;")
            print("Res is: ",res)
            print("Table already exist!")
        except exc.NoSuchTableError:
            create_table_sql = "CREATE TABLE dictionary (word VARCHAR, cid VARCHAR, last_repeat TIMESTAMP, iteration INTEGER, next_repeat TIMESTAMP);"
            connection.execute(create_table_sql)
            print("Table has created!")
        connection.close()

    def insert_word(self, message):
        connection = self.__engine.connect()
        last_dt = datetime.datetime.now()
        new_dt = last_dt + datetime.timedelta(days=1)
        connection.execute("INSERT INTO dictionary VALUES (:word, \
                                                    :cid, \
                                                    :last_repeat, \
                                                    :iteration, \
                                                    :next_repeat);",
        word=message.text, cid=message.chat.id, last_repeat=last_dt, iteration=1, next_repeat=new_dt)
        connection.close()

    def get_words_by_cid(self, cid):
        connection = self.__engine.connect()
        result = connection.execute("SELECT word from dictionary WHERE cid = :cid;", cid=cid)
        words = []
        word = result.fetchone()
        while word is not None:
            words.append(word[0])
            word = result.fetchone()
        connection.close()
        return words

    def get_words(self):
        connection = self.__engine.connect()
        res = {}
        cids = []
        result = connection.execute("SELECT DISTINCT cid FROM dictionary;")
        row = result.fetchone()
        while row is not None:
            cids.append(row[0])
            row = result.fetchone()
        for cid in cids:
            res.update({cid: self.get_words_by_cid(cid)})
        connection.close()
        return res

