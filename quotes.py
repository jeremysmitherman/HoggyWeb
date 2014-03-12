from sqlalchemy import Column, Integer, String
from base import Base, Session

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    body = Column(String(200))

    @classmethod
    def get(cls, id):
        return Session.query.get(id)