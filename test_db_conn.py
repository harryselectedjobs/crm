
# Step 1 : run this to create the db in AWS - RDS
import mysql.connector
c = mysql.connector.connect(
    host='selectedgroupcrm.cbmo6qu6oqc6.eu-north-1.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='root2000'
)
cursor = c.cursor()
cursor.execute('CREATE DATABASE selectedgroupcrm')
print('Database created successfully!')


