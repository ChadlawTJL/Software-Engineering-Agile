import sqlite3



#connection to SQLite Database - check same thread is false as it was bringing back an error
connection=sqlite3.connect('Assignment App.db', check_same_thread=False)
#allow retrevial of records
cur=connection.cursor()


#Unit testing for connection
#sql = 'select * From Users'

#cur.execute(sql)

#print(cur.fetchall())

#if we just want to pick out the name etc

#Results=cur.fetchall()
#for result in Results:
    #print(result[1])



