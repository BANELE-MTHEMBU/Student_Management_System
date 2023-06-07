
# first importing the pymongo
from pymongo import MongoClient

#client is going to connect to MongoClient using the link from MongoDB
#client(local host)
client = MongoClient('mongodb://localhost:27017')

# creating / connecting the database 'sms'
db = client['sms']

#creating a collection -> a collection in mongoDB is actually a table
user = db["users"]