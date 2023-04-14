import mysql.connector
from mysql.connector import errorcode
import pymongo
import redis

def mysql_select():
    try:
        cnx = mysql.connector.connect(user='root', password='password', host='idasm101.unamurcs.be', port='33060', database='reldata')
        cursor = cnx.cursor()

        query = ("SELECT LastName, FirstName, Country FROM Employees WHERE Country in (%s, %s)")

        first_country = 'USA'
        second_country = 'UK'

        cursor.execute(query, (first_country, second_country))

        for (LastName, FirstName, Country) in cursor:
            print(f'Employee: {LastName} {FirstName} lives in {Country}')

        cursor.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()


def mongodb_select():
    client = pymongo.MongoClient('idasm101.unamurcs.be', 27010)
    db = client['myMongoDB']
    collection = db["Customers"]
    pipeline = [{"$sample": {"size": 5}}]
    result = collection.aggregate(pipeline)
    for doc in result :
        customer_id = doc['CustomerID']
        print(f'Customer ID: {customer_id}')

        
def redis_select():
    r = redis.Redis(host='idasm101.unamurcs.be', port=63790, db=0)
    order_customer = r.hget('ORDER:10746', 'CustomerRef')
    print(f'Order customer ID: {order_customer}')
        
mysql_select()
mongodb_select()
redis_select()