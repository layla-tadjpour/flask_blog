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
