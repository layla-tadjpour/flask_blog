import click
from flask.cli import with_appcontext


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)

def init_db():
    from myblog import db
    db.create_all()
    click.echo('Initialized the database tables.')

def reset_db():
    from myblog import db
    db.drop_all()
    db.create_all()
    click.echo('Reset the database.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create new tables if they don't exist."""
    init_db()

@click.command('reset-db')
@click.confirmation_option(prompt='Are you sure you want to reset the database? This will delete all data.')
@with_appcontext
def reset_db_command():
    """Clear existing data and create new tables."""
    reset_db()