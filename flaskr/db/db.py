import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import pymysql.cursors


# def get_db_1():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row
#     return g.db
def parse_sql(filename):
    data = current_app.open_resource(filename, 'r').readlines()
    stmts = []
    DELIMITER = ';'
    stmt = ''

    for lineno, line in enumerate(data):
        if not line.strip():
            continue

        if line.startswith('--'):
            continue

        if 'DELIMITER' in line:
            DELIMITER = line.split()[1]
            continue

        if (DELIMITER not in line):
            stmt += line.replace(DELIMITER, ';')
            continue

        if stmt:
            stmt += line
            stmts.append(stmt.strip())
            stmt = ''
        else:
            stmts.append(line.strip())
    return stmts


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(host=current_app.config['HOST'],
                               port=current_app.config['PORT'],
                               user=current_app.config['USER'],
                               password=current_app.config['PASSWORD'],
                               db=current_app.config['DB'],
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# def init_db():
#     db = get_db()
#
#     with current_app.open_resource('db/schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))


def init_db():
    db = get_db()
    stmts = parse_sql('db/schema.sql')
    with db.cursor() as cursor:
        for stmt in stmts:
            cursor.execute(stmt)
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
