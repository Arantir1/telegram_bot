from sqlalchemy import Date, cast
from datetime import date, datetime, timedelta

from basic import session_factory
from word import Word
from task import Task


class Mydb():

    __session = None
    __engine = None

    def get_words(self):
        session = session_factory()
        all_words = session.query(Word)
        session.close()
        return all_words.all()

    def get_words_by_cid(self, cid):
        session = session_factory()
        words_of_cid = session.query(Word).filter(Word.cid == cid)
        session.close()
        return words_of_cid.all()

    def insert_word(self, word, cid):
        session = session_factory()
        new_word = Word(word, cid)
        session.add(new_word)
        session.commit()
        session.close()

    def get_words_to_learn(self, cid):
        session = session_factory()
        words_to_learn = session.query(Word)\
            .filter(cast(Word.next_repeat, Date) <= date.today(),
                    Word.cid == cid)
        session.close()
        return words_to_learn.all()

    def is_word_exist(self, cid, word):
        session = session_factory()
        exist = session.query(Word)\
            .filter(Word.word == word, Word.cid == cid).scalar() is not None
        session.close()
        return exist

    def delete_word(self, cid, word):
        session = session_factory()
        word_to_delete = session.query(Word)\
            .filter(Word.cid == cid, Word.word == word).one()
        session.delete(word_to_delete)
        session.close()

    def increment_iteration(self, word, cid):
        session = session_factory()
        modified_word = session.query(Word)\
            .filter(Word.word == word, Word.cid == cid).one()
        now = datetime.now()
        modified_word.last_repeat = now
        modified_word.iteration += 1
        if 1 <= modified_word.iteration <= 3:
            modified_word.interval = now + timedelta(days=1)
            print("Iteration is: ", modified_word.iteration)
        elif 4 <= modified_word.iteration <= 5:
            modified_word.interval = now + timedelta(days=3)
            print("Iteration is: ", modified_word.iteration)
        elif modified_word.iteration == 6:
            modified_word.interval = now + timedelta(days=5)
            print("Iteration is: ", modified_word.iteration)
        elif modified_word.iteration > 6:
            print("Iteration is: ", modified_word.iteration)
            print("Need to delete word")
            session.delete(modified_word)
        session.commit()
        session.close()

    def decrement_iteration(self, cid, word):
        session = session_factory()
        modified_word = session.query(Word)\
            .filter(Word.word == word, Word.cid == cid).one()
        now = datetime.now()
        modified_word.last_repeat = now
        if modified_word.iteration > 1:
            modified_word.iteration -= 1
        if 1 <= modified_word.iteration <= 3:
            modified_word.interval = now + timedelta(days=1)
            print("Iteration is: ", modified_word.iteration)
        elif 4 <= modified_word.iteration <= 5:
            modified_word.interval = now + timedelta(days=3)
            print("Iteration is: ", modified_word.iteration)
        session.commit()
        session.close()
