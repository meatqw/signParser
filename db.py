from email.policy import default
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, CheckConstraint, select, Float, Text, insert, JSON, update, delete, BOOLEAN
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
    Column('tag', JSON(), nullable=True),
    Column('section', JSON(), nullable=True),
    Column('donor', String(200), nullable=True),
    Column('status', BOOLEAN(), default=False),
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
        donor = data['donor'],
        status = data['status'],
    )
    conn = engine.connect()
    conn.execute(ins)
    
    
def get_item(title):
    query = select([items]).where(items.c.title == title)
    return engine.connect().execute(query).first()

def get_all(donor_name):
    query = select([items]).where(items.c.donor == donor_name, items.c.status == False)
    return engine.connect().execute(query).all()

def update_section(item, section):
    arr = item[-4]
    for i in section:
        if i not in arr:
            arr.append(i)
            
    query = update(items).where(items.c.id == item[0]).values(section=arr)
    engine.execute(query)

def update_status(id):
    query = update(items).where(items.c.id == id).values(status=True)
    engine.execute(query)
    
def update_tag(item, tag):
    arr = item[-5]
    for i in tag:
        if i not in arr:
            arr.append(i)
            
    query = update(items).where(items.c.id == item[0]).values(tag=arr)
    engine.execute(query)

def delet():
    query = select([items]).where(items.c.section == ['Магистральные'])
    for i in engine.execute(query).all():
        print(i[0])
        q = items.delete().where(items.c.id == i[0])
        engine.execute(q)
        print(i[0])
        
