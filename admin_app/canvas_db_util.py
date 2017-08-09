
import psycopg2
import psycopg2.extras
import sys
import os
import getpass


def export_canvas_db(db_name="canvas_production", host="canvas.ed", user="postgres", password="changeme", port=5432):
    # Connect and create a dump
    con = psycopg2.connect(database=db_name, user=user, password=password, host=host, port=port)

    # Locate dump folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, "volumes", "canvas", "db_sync")
    try:
        # Ensure the folder exists
        os.makedirs(db_dir)
    except:
        pass

#  select relname from pg_class where relkind='r';
    # relkind - s - ??, t = toast, i = index, r = ??(tables), v = views?
    # Get a list of tables
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select version()")
    ver = cur.fetchone()
    print ver

def import_canvas_db():
    pass


if __name__ == "__main__":
    pw = getpass.getpass()
    export_canvas_db()
