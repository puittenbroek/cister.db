from cister import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import column_property
from sqlalchemy.sql import join
from datetime import datetime

class News(BaseModel):
    __tablename__ = 'cister_news'
    news_id = Column(Integer, primary_key=True,autoincrement=True)
    title = Column(Unicode(200))
    body = Column(Text)
    created = Column(TIMESTAMP,default='CURRENT_TIMESTAMP')
    lastchanged = Column(TIMESTAMP,default='CURRENT_TIMESTAMP')
    

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.created = datetime.now()
        self.lastchange = datetime.now()
