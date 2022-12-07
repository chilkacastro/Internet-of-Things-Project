import pymysql
import pymysql.cursors

#after installing mariadb and setting password to 'root' (we can change this if you want):
#maybe install pymysql as well
# to navigate the db directly from terminal: run in terminal: mariadb -u root -p and enter password (root)

#create the database: just write: CREATE DATABASE IOT;



# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             database='IOT',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

#CREATE THE TABLE (UNCOMMENT THIS FOR FIRST TIME CREATION)
# 
# with connection.cursor() as cursor:
#     # Read a single record
#     sql = """CREATE TABLE USER ( 
#          id VARCHAR(25) NOT NULL, 
#          temp_threshold  DECIMAL,
#          light_threshold DECIMAL,
#          picture VARCHAR(100),
#          CONSTRAINT iot_pk PRIMARY KEY (id)) """
#     # To execute the SQL query
#     cursor.execute(sql)   
# 
#     # To commit the changes
#     connection.commit()         
#     connection.close()


#

# INSERT YOUR CARD INFO
with connection.cursor() as cursor:
    # Create a new record
   # sql = "INSERT INTO `USER` (`id`, `temp_threshold`, `light_threshold`, `picture`) VALUES ('f37d2813', '23.5', '500.0', 'assets/dory.jpg')"
    sql = "INSERT INTO `USER` (`id`, `temp_threshold`, `light_threshold`, `picture`) VALUES ('33a168d', '17', '500.0', 'assets/stitch.jpg')"
    #sql = "DELETE FROM USER WHERE id='33a168d'"
    cursor.execute(sql)

# connection is not autocommit by default. So you must commit to save
# your changes.
    connection.commit()

