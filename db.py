from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, CheckConstraint, select, Float, Text, insert
from datetime import datetime
import os

metadata = MetaData()

engine = create_engine(f"sqlite:///{os.path.abspath('data.db')}")

# items model
items = Table('items', metadata,
    Column('id', Integer(), primary_key=True),
    Column('link', String(200), nullable=True),
    Column('title', String(200), nullable=True),
    Column('description', Text(), nullable=True),
    Column('price', Float(), nullable=True),
    Column('img', String(200), nullable=True),
    Column('tag', String(200), nullable=True),
    Column('section', String(200), nullable=True),
    Column('donor', String(200), nullable=True),
    Column('created_on', DateTime(), default=datetime.now)
)

#create table
metadata.create_all(engine)

def add_item(data):
    ins = insert(items).values(
        link = data['link'],
        title = data['title'],
        description = data['description'],
        price = data['price'],
        img = data['img'],
        tag = data['tag'],
        section = data['section'],
        donor = data['donor']
    )
    conn = engine.connect()
    conn.execute(ins)
    
    
def get_item(link):
    query = select([items]).where(items.c.link == link)
    return engine.connect().execute(query).first()