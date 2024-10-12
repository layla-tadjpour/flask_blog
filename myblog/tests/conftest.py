import pytest
import os
from myblog import create_app, db


# Use a separate test database
TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL') or 'postgresql://layla@localhost/test_blog_db'


@pytest.fixture(scope='session')
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URL,
    })
    return app

@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        db.create_all()
    yield db
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def db_session(app, _db):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        db_session = _db._make_scoped_session(options={"bind": connection, "binds": {}})
        _db.session = db_session
        yield db_session
        transaction.rollback()
        connection.close()
        db_session.remove()
        # Clear all tables after each test
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()



class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def register(self, username='testuser', password='password123'):
        return self._client.post('/auth/register', data={
            'username': username,
            'password': password,
            'confirm': password,
        })

    def login(self, username='testuser', password='password123'):
        return self._client.post('/auth/login', data={
            'username': username,
            'password': password
        })

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
