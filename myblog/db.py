import sqlite3


# class Post:
#     def __init__(self,dbname='blog.db', table_name='post'):
#         self.dbname = dbname
#         self.table = table_name
#         self._create_table_if_not_exists()

#     def _create_table_if_not_exists(self):
#         sql = f'CREATE TABLE IF NOT EXISTS {self.table} (subject TEXT, content TEXT, created INTEGER, last_modified INTEGER)'
#         with sqlite3.connect(self.dbname) as db:
#             db.execute(sql)

#     def _connect(self):
#         return sqlite3.connect(self.dbname)
            
#     def put(self,*columns):
#         with self._connect() as db:
#             c = db.execute(f'insert into {self.table} values (?, ?, ?, ?)',columns)
#             db.commit()
#             return c.lastrowid

#     def fetchall(self,where=""):
#         with self._connect() as db:
#             c = db.execute(f"select * from  {self.table}" + where)
#             return c.fetchall()
    
#     def fetchall_ordered(self,  order_by_column, where=""):
#         with self._connect() as db:
#             c = db.execute(f"select rowid, * from  {self.table} order by {order_by_column} desc" + where)
#             return c.fetchall()

#     def fetchmany_ordered(self,  order_by_column, num, where=""):
#         with self._connect() as db:
#             c = db.execute(f"select rowid, * from  {self.table} order by {order_by_column} desc" + where)
#             return c.fetchmany(num)

#     def fetchone(self, where="",params=()):
#         with self._connect() as db:
#             c = db.execute(f"select rowid, * from  {self.table} {where}" , params)
#             return c.fetchone()

#     def fechmany(self, num, where=""):
#         with self._connect() as db:
#             c = db.execute(f"select rowid, * from  {self.table}" + where)
#             return c.fetchmany(num)

    
    # def update(self, row_id, subject=None, blog=None):
    #     import time, datetime
    #     with self._connect() as db:
    #         current_time = int(time.mktime(datetime.now().timetuple()))
    #         set_clause = []
    #         params = []

    #         if subject:
    #             set_clause.append("subject = ?")
    #             params.append(subject)
    #         if blog:
    #             set_clause.append("blog = ?")
    #             params.append(blog)
    #         set_clause.append("last_modified = ?")
    #         params.append(current_time)

    #         params.append(row_id)

    #         sql = f"UPDATE {self.table} SET {', '.join(set_clause)} WHERE rowid = ?"
    #         db.execute(sql, params)
    #         db.commit()
    #         return current_time
        



import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)