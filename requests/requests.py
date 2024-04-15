import mysql.connector
from mysql.connector import errorcode
import pymongo
import redis
import time


def mysql_select():
    try:
        cnx = mysql.connector.connect(
            user="root",
            password="password",
            host="idasm101prj.unamurcs.be",
            port="33060",
            database="reldata",
        )
        cursor = cnx.cursor()

        query = "SELECT LastName, FirstName, Country FROM Employees WHERE Country in (%s, %s)"

        first_country = "USA"
        second_country = "UK"

        cursor.execute(query, (first_country, second_country))

        for LastName, FirstName, Country in cursor:
            print(f"Employee: {LastName} {FirstName} lives in {Country}")

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
    client = pymongo.MongoClient("idasm101prj.unamurcs.be", 27010)
    db = client["myMongoDB"]
    collection = db["Customers"]
    pipeline = [{"$sample": {"size": 5}}]
    result = collection.aggregate(pipeline)
    for doc in result:
        customer_id = doc["CustomerID"]
        print(f"Customer ID: {customer_id}")


def redis_select():
    r = redis.Redis(host="idasm101prj.unamurcs.be", port=63790, db=0)
    order_customer = r.hget("ORDER:10746", "CustomerRef")
    print(f"Order customer ID: {order_customer}")


# mysql_select()
# mongodb_select()
# redis_select()

# ========================================================================================================
#                                    Code for the second part
# ========================================================================================================


def mongo_conn():
    client = pymongo.MongoClient("idasm101prj.unamurcs.be", 27010)
    db = client["myMongoDB"]
    return db


def mysql_conn():
    try:
        cnx = mysql.connector.connect(
            user="root",
            password="password",
            host="idasm101prj.unamurcs.be",
            port="33060",
            database="reldata",
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    return cnx


def redis_conn():
    r = redis.Redis(host="idasm101prj.unamurcs.be", port=63790, db=0)
    return r


def get_suppliers_infos():
    start_time = time.time()
    mongo_DB = mongo_conn()
    suppliers = mongo_DB["Suppliers"]
    researched_suppliers = suppliers.find(
        {"$or": [{"City": "London"}, {"Country": "France"}]}
    )

    print("--- Suppliers info : %s seconds ---" % (time.time() - start_time))

    return researched_suppliers


def get_suppliers_infos_snail():
    start_time = time.time()
    cnx = mysql_conn()
    cursor = cnx.cursor()
    query = (
        "SELECT SupplierRef FROM Products WHERE ProductName = 'Escargots de Bourgogne';"
    )
    cursor.execute(query)
    supplier_ref = cursor.fetchone()
    cursor.close()

    mongo_DB = mongo_conn()
    suppliers = mongo_DB["Suppliers"]
    researched_suppliers = suppliers.find({"SupplierID": {"$in": supplier_ref}})
    print("--- Suppliers info for snail : %s seconds ---" % (time.time() - start_time))

    return researched_suppliers


def display_suppliers_infos(suppliers):
    print("Suppliers :")
    for supplier in suppliers:
        print(
            f"Supplier: {supplier['SupplierID']} - {supplier['CompanyName']} - {supplier['City']} - {supplier['Country']}"
        )


def get_shippers_infos():
    start_time = time.time()
    redis_DB = redis_conn()
    shipper_company_name = redis_DB.get("SHIPPERS:3:COMPANYNAME").decode("utf-8")
    shipper_phone = redis_DB.get("SHIPPERS:3:PHONE").decode("utf-8")
    print("--- Shippers info : %s seconds ---" % (time.time() - start_time))

    return shipper_company_name, shipper_phone


def display_shipper_infos(shipper_company_name, shipper_phone):
    print(f"Shipper: {shipper_company_name} - {shipper_phone}")


def get_customers_for_margaret():
    start_time = time.time()
    # Connexion à MongoDB
    mongo_db = mongo_conn()
    customers_collection = mongo_db["Customers"]

    # Connexion à Redis
    redis_client = redis_conn()

    # Connexion à SQL
    cnx = mysql_conn()
    cursor = cnx.cursor()
    query = "SELECT EmployeeID FROM Employees WHERE FirstName = 'Margaret'"
    cursor.execute(query)
    employee_ids = cursor.fetchall()
    cursor.close()

    # Redis pour obtenir les ID de commande pour ces employés
    for employee_id in employee_ids:
        valid_orders = []
        for order_id in redis_client.keys("ORDER:*"):
            order_info = redis_client.hgetall(order_id)
            if int(order_info[b"EmployeeRef"].decode("utf-8")) == employee_id[0]:
                valid_orders.append(order_info[b"CustomerRef"].decode("utf-8"))

    # MongoDB pour obtenir les informations des clients ayant passé ces commandes
    customer_details = []
    for customer_id in set(valid_orders):
        customer = customers_collection.find_one({"CustomerID": customer_id})
        if customer:
            customer_details.append(customer)

    # Fermeture des connexions
    cnx.close()

    print("--- Customers for Margaret : %s seconds ---" % (time.time() - start_time))
    # Affichage des informations des clients

    return customer_details


def display_customers_infos(customers):
    for customer in customers:
        print(
            f"Customer: {customer['CustomerID']} - {customer['CompanyName']} - {customer['City']} - {customer['Country']}"
        )


def main():
    # Requête 1 (MONGO)
    researched_suppliers = get_suppliers_infos()
    display_suppliers_infos(researched_suppliers)

    # Requête 2 (MONGO + MYSQL)
    researched_suppliers = get_suppliers_infos_snail()
    display_suppliers_infos(researched_suppliers)

    # Requête 3 (REDIS)
    shipper_company_name, shipper_phone = get_shippers_infos()
    display_shipper_infos(shipper_company_name, shipper_phone)

    # Requête 4 (MONGO + MYSQL + REDIS)
    customers = get_customers_for_margaret()
    display_customers_infos(customers)


if __name__ == "__main__":
    main()
