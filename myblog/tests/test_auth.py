import pytest
from flask import session
from myblog.model import User

# Registration test case
def test_register(client, app):
    # Test valid registration
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'password123',
        'confirm': 'password123'
    })
    assert response.status_code == 302  # should redirect after successful registration

    with app.app_context():
        user = User.get_user_by_username('testuser')
        assert user is not None
        assert user.check_password('password123')  # Check if password was set correctly


def test_can_register_admin_limit(client, app):
    # Register the first admin user successfully
    response = client.post('/auth/register', data={
        'username': 'admin1',
        'password': 'password123',
        'confirm': 'password123'
    })
    assert response.status_code == 302  # should redirect after successful registration

    response = client.post('/auth/register', data={
        'username': 'admin2',
        'password': 'password123',
        'confirm': 'password123'
    }, follow_redirects=False)
    
    # Check for the correct redirect and flash message
    assert response.status_code == 302
    assert response.headers["Location"] == "/"  # Check redirect to index page

    # Now follow the redirect to capture the flash message
    response = client.get(response.headers["Location"], follow_redirects=True)
    assert b'Maximum number of administrators reached' in response.data

    # Check that only one user was created
    with app.app_context():
        admins = User.query.all()
        assert len(admins) == 1
        assert admins[0].username == 'admin1'



def test_login(client, auth):
    # Register a user
    auth.register()

    # Test valid login
    response = auth.login()
    assert response.status_code == 302  # should redirect after successful login

    # Follow the redirect
    response = client.get('/')
    assert response.status_code == 200  # ensure the user is redirected to the home page
    assert b'Logout' in response.data  # check if the page shows the user is logged in (e.g., via a "Log out" link)

    # Test invalid login
    response = client.post('/auth/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # stay on the login page
    assert b'Incorrect username.' in response.data or b'Incorrect password.' in response.data


# Logout test case
def test_logout(client, auth):
    # Log in first
    auth.register()
    auth.login()

    with client:
        response = auth.logout()
        assert response.status_code == 302  # should redirect after logout
        assert 'user_id' not in session  # Ensure the user_id is removed from the session

