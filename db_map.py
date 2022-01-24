from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# sqlalchemy База для взаємодії бота з БД як з Обєктом
# Тут описано що і для чого
# https://surik00.gitbooks.io/aiogram-lessons/content/chapter2.html
class UsersIds(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_bot = Column(String(255))
    language_code = Column(String(255))