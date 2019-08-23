import config
from sqlalchemy import create_engine, exc


class Mydb():

    __engine = None

    def __init__(self):
        self.__engine = create_engine("postgresql://%s:%s@%s:%s/%s" %
                                      (config.user,
                                       config.password,
                                       config.host,
                                       config.port,
                                       config.database))

    def create_db_table(self):
        try:
            connection = self.__engine.connect()
            res = connection.execute("SELECT * FROM dictionary;")
            print("Res is: ", res)
            print("Table already exist!")
        except exc.NoSuchTableError:
            create_table_sql = "CREATE TABLE dictionary(word VARCHAR,\
                                                       cid VARCHAR,\
                                                       last_repeat TIMESTAMP,\
                                                       iteration INTEGER,\
                                                       next_repeat TIMESTAMP);"
            connection.execute(create_table_sql)
            print("Table has created!")
        connection.close()

    def insert_word(self, message):
        connection = self.__engine.connect()
        connection.execute("INSERT INTO dictionary VALUES (%(word)s, \
                                                %(cid)s, \
                                                now(), \
                                                %(iteration)s, \
                                                'tomorrow'::TIMESTAMP);",
                           {'word': message.text,
                            'cid': message.chat.id,
                            'iteration': 1})
        connection.close()

    def get_words_by_cid(self, cid):
        connection = self.__engine.connect()
        result = connection.execute("SELECT word from dictionary \
                                     WHERE cid=%(cid)s;",
                                    {'cid': str(cid)})
        words = result.fetchall()
        connection.close()
        return words

    def get_words_to_learn(self, cid):
        connection = self.__engine.connect()
        result = connection.execute("SELECT * FROM dictionary \
                                    WHERE date(next_repeat) <= current_date;")
        lines = result.fetchall()
        print('Lines: ', lines)
        connection.close()
        return lines

    def get_words(self):
        connection = self.__engine.connect()
        res = {}
        result = connection.execute("SELECT DISTINCT cid FROM dictionary;")
        cids = list(result.fetchall())
        for cid in cids:
            res.update({cid: self.get_words_by_cid(cid)})
        connection.close()
        connection = self.__engine.connect()
        return res

    def delete_word_by_cid(self, word, cid):
        connection = self.__engine.connect()
        connection.execute("DELETE FROM dictionary \
                            WHERE cid=%(cid)s AND word=%(word)s;",
                           {'cid': str(cid), 'word': word})
        connection.close()

    def is_word_exist(self, word, cid):
        connection = self.__engine.connect()
        result = connection.execute("SELECT FROM dictionary \
                                     WHERE cid=%(cid)s AND word=%(word)s;",
                                    {'cid': str(cid), 'word': word})
        row = result.fetchone()
        connection.close()
        if row is None:
            return False
        else:
            return True
