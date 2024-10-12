import pytest
from myblog.model import User, Post
from flask import url_for

def test_index(client, db_session):
    # Create some test posts
    user = User.create_user('testuser', 'password123')
    db_session.add(user)
    db_session.commit()
    
    Post.create_post(user.id, 'Test Post 1', 'This is test post 1')
    Post.create_post(user.id, 'Test Post 2', 'This is test post 2')
    db_session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b'Test Post 1' in response.data
    assert b'Test Post 2' in response.data

def test_get_page(client, db_session):
    user = User.create_user('testuser', 'password123')
    db_session.add(user)
    db_session.commit()
    
    post = Post.create_post(user.id, 'Test Post', 'This is a test post')
    db_session.commit()

    response = client.get(f'/{post.created.year}/{post.created.month}/{post.created.day}/{post.slug}')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'This is a test post' in response.data

def test_create_post(client, auth, db_session):
    auth.register()
    auth.login()

    response = client.post('/create', data={
        'title': 'Created Post',
        'body': 'This is a created post'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Created Post' in response.data
    assert b'This is a created post' in response.data

def test_update_post(client, auth, db_session):
    auth.register()
    auth.login()

    user = User.get_user_by_username('testuser')
    post = Post.create_post(user.id, 'Original Post', 'This is the original post')
    db_session.commit()

    response = client.post(f'/{post.slug}/update', data={
        'title': 'Updated Post',
        'body': 'This is the updated post'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Updated Post' in response.data
    assert b'This is the updated post' in response.data

def test_delete_post(client, auth, db_session):
    auth.register()
    auth.login()

    user = User.get_user_by_username('testuser')
    post = Post.create_post(user.id, 'Post to Delete', 'This post will be deleted')
    db_session.commit()

    response = client.post(f'/{post.slug}/delete', follow_redirects=True)

    assert response.status_code == 200
    assert b'Post deleted successfully' in response.data
    assert Post.get_post(post.slug) is None

def test_login_required(client):
    response = client.get('/create')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required_for_modifying_posts(client, path):
    response = client.post(path)
    assert response.headers['Location'].startswith('/auth/login')

def test_author_required(client, auth, db_session):
    # Create two users
    auth.register('user1', 'password1')
    auth.register('user2', 'password2')
    
    # Log in as user1 and create a post
    auth.login('user1', 'password1')
    user1 = User.get_user_by_username('user1')
    post = Post.create_post(user1.id, 'User1 Post', 'This is user1\'s post')
    db_session.commit()

    # Log out user1 and log in as user2
    auth.logout()
    auth.login('user2', 'password2')

    # Try to update user1's post as user2
    response = client.post(f'/{post.slug}/update', data={
        'title': 'Unauthorized Update',
        'body': 'This update should not be allowed'
    }, follow_redirects=True)

    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    # Try to delete user1's post as user2
    response = client.post(f'/{post.slug}/delete', follow_redirects=True)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

