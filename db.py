from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, CheckConstraint, select, Float, Text, insert, JSON, update, delete
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
    Column('fields', JSON(), nullable=True),
    Column('price', Float(), nullable=True),
    Column('img', JSON(), nullable=True),
    Column('tag', String(200), nullable=True),
    Column('section', JSON(), nullable=True),
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
        fields = data['fields'],
        price = data['price'],
        img = data['img'],
        tag = data['tag'],
        section = data['section'],
        donor = data['donor']
    )
    conn = engine.connect()
    conn.execute(ins)
    
    
def get_item(title):
    query = select([items]).where(items.c.title == title)
    return engine.connect().execute(query).first()

def get_all():
    query = select([items])
    return engine.connect().execute(query).all()

def delet():
    query = select([items]).where(items.c.section == ['Магистральные'])
    for i in engine.execute(query).all():
        print(i[0])
        q = items.delete().where(items.c.id == i[0])
        engine.execute(q)
        print(i[0])
