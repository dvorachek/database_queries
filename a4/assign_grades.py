# assign_grades.py
# CSC 370 - Spring 2018 - Starter code for Assignment 4
#
# Dylan Dvorachek
# V00863468
#
#
# B. Bird - 02/26/2018

import sys, csv, psycopg2

if len(sys.argv) < 2:
    print("Usage: %s <input file>",file=sys.stderr)
    sys.exit(0)
    
input_filename = sys.argv[1]

# Open your DB connection here
psql_user = 'dvorache'  # when I started at uvic the maximum character lenght was 8..
psql_db = 'dvorache'
psql_password = 'pineapple'
psql_server = 'studdb2.csc.uvic.ca'
psql_port = 5432

conn = psycopg2.connect(dbname=psql_db, user=psql_user, password=psql_password, host=psql_server, port=psql_port)

cursor = conn.cursor()

def e(func, conn):  # wrapper for error handling
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except psycopg2.ProgrammingError as err:
            #ProgrammingError is thrown when the database error is related to the format of the query (e.g. syntax error)
            print("Caught a ProgrammingError:",file=sys.stderr)
            print(err,file=sys.stderr)
            conn.rollback()
            conn.close()
            sys.exit(1)
        except psycopg2.IntegrityError as err: 
            #IntegrityError occurs when a constraint (primary key, foreign key, check constraint or trigger constraint) is violated.
            print("Caught an IntegrityError:",file=sys.stderr)
            print(err,file=sys.stderr)
            conn.rollback()
            conn.close()
            sys.exit(1)
        except psycopg2.InternalError as err:  
            #InternalError generally represents a legitimate connection error, but may occur in conjunction with user defined functions.
            #In particular, InternalError occurs if you attempt to continue using a cursor object after the transaction has been aborted.
            #(To reset the connection, run conn.rollback() and conn.reset(), then make a new cursor)
            print("Caught an IntegrityError:",file=sys.stderr)
            print(err,file=sys.stderr)
            conn.rollback()
            conn.close()
            sys.exit(1)

with open(input_filename) as f:
    for row in csv.reader(f):
        if len(row) == 0:
            continue #Ignore blank rows
        if len(row) != 4:
            print("Error: Invalid input line \"%s\""%(','.join(row)), file=sys.stderr)
            #Maybe abort the active transaction and roll back at this point?
            break
        course_code,term,student_id,grade = row
        
        #Do something with the data here
        #Make sure to catch any exceptions that occur and roll back the transaction if a database error occurs.
        e(cursor.execute("insert into grades values( %s, %s, %s, %s ) on conflict (student_id, course_code, term_code) do update set grade = %s;", (student_id, course_code, term, grade, grade)), conn)

conn.commit()
cursor.close()
conn.close()
