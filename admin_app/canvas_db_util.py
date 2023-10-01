
import psycopg2
import psycopg2.extras
import sys
import os
import getpass

# The minimum ID to grab - anything lower we ignore because it isn't
# in the valid sequence range (e.g. don't propogate initial data like root account
min_id = 90000000000
# Tables to merge
merge_tables = ["users", "accounts"]

# docker exec -it ope-redis redis-cli flushall

def export_table(table, con):
    # Figure out what parts to export for this table

    # Pull list from logged_actions table
    pass


def export_canvas_db(db_name="canvas_production", host="canvas.ed", user="postgres", password="changeme", port=5432):
    global min_id, merge_tables
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

    for table in merge_tables:
        export_table(table, con)

#  select relname from pg_class where relkind='r';
    # relkind - s - ??, t = toast, i = index, r = ??(tables), v = views?
    # Get a list of tables
    sql = """SELECT nspname||'.'||relname AS full_rel_name
  FROM pg_class, pg_namespace
 WHERE relnamespace = pg_namespace.oid
   AND nspname = 'yourschemaname'
   AND relkind = 'r';"""
    sql = """select * from pg_tables where schemaname='public';"""
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select version()")
    ver = cur.fetchone()
    print(ver)

def import_canvas_db():
    pass


if __name__ == "__main__":
    pw = getpass.getpass()
    export_canvas_db()
