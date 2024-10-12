import pytest
import time
from myblog.model import User, Post


def generate_unique_username():
    return f"testuser_{int(time.time() * 1000)}"

def generate_unique_title():
    return f"Test Post {int(time.time() * 1000)}"


def test_create_user(app):
    with app.app_context():
        user = User.create_user(username='testuser', password='testpass')
        assert user.username == 'testuser'
        assert user.check_password('testpass')

def test_get_user_by_username(app):
    with app.app_context():
        username = generate_unique_username()
        print("username is", username)
        User.create_user(username=username, password='testpass')
        user = User.get_user_by_username(username)
        assert user is not None
        assert user.username == username


def test_authenticate_user(app):
    with app.app_context():
        username = generate_unique_username()
        print("username is", username)
        User.create_user(username=username, password='testpass')
        user = User.authenticate_user(username, 'testpass')
        assert user is not None
        assert user.username == username


def test_create_post(app, db_session):
    with app.app_context():
        try:
            username = generate_unique_username()
            user = User.create_user(username=username, password='testpass')
            db_session.flush()

            title1 = generate_unique_title()
            post1 = Post.create_post(author_id=user.id, title=title1, body='This is test post 1.')
            db_session.flush()

            title2 = generate_unique_title()
            post2 = Post.create_post(author_id=user.id, title=title2, body='This is test post 2.')
            db_session.flush()

            # Assert that the posts were created successfully
            assert post1.title == title1
            assert post2.title == title2
            assert post1.body == 'This is test post 1.'
            assert post2.body == 'This is test post 2.'

            # Assert that the slugs were generated correctly and are unique
            assert post1.slug != post2.slug
            assert post1.slug == post1.slug.lower()
            assert post2.slug == post2.slug.lower()
            assert '-' in post1.slug
            assert '-' in post2.slug

            # Verify that we can retrieve the posts by their slugs
            retrieved_post1 = Post.get_post(post1.slug)
            retrieved_post2 = Post.get_post(post2.slug)
            assert retrieved_post1 is not None
            assert retrieved_post2 is not None
            assert retrieved_post1.id == post1.id
            assert retrieved_post2.id == post2.id

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            pytest.fail(f"Test failed: {str(e)}")


def test_get_post(app, db_session):
     with app.app_context():
        try:
            username = generate_unique_username()
            user = User.create_user(username=username, password='testpass')
            db_session.flush()  # This assigns an ID to the user without committing
            
            post = Post.create_post(author_id=user.id, title='Test Post', body='This is a test post.')
            db_session.flush()  # This assigns an ID to the post without committing
            
            # At this point, the post is in the db_session but not committed to the database
            
            fetched_post = Post.get_post('test-post')
            assert fetched_post is not None
            assert fetched_post.title == 'Test Post'
            assert fetched_post.author_id == user.id
            
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            pytest.fail(f"Test failed: {str(e)}")

def test_update_post(app, db_session):
    with app.app_context():
        try:
            username = generate_unique_username()
            user = User.create_user(username=username, password='testpass')
            db_session.flush()

            original_title = generate_unique_title()
            post = Post.create_post(author_id=user.id, title=original_title, body='This is a test post.')
            db_session.flush()

            original_slug = post.slug

            updated_title = f"Updated {original_title}"

            updated_post = Post.update_post(original_slug, updated_title, 'This post has been updated.')
            db_session.flush()

            assert updated_post.title == updated_title
            assert updated_post.body == 'This post has been updated.'
            assert updated_post.slug != original_slug

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            pytest.fail(f"Test failed: {str(e)}")


def test_delete_post(app, db_session):
    with app.app_context():
        try:
            user = User.create_user(username='testuser', password='testpass')
            db_session.flush()

            post = Post.create_post(author_id=user.id, title='Test Post', body='This is a test post.')
            db_session.flush()

            deleted_post = Post.delete_post('test-post')
            db_session.flush()

            assert deleted_post is not None
            assert Post.get_post('test-post') is None

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            pytest.fail(f"Test failed: {str(e)}")


def test_get_all_posts(app, db_session):
    with app.app_context():
        try:
            username = generate_unique_username()
            user = User.create_user(username=username, password='testpass')
            db_session.flush()

            Post.create_post(author_id=user.id, title='Test Post 1', body='This is test post 1.')
            Post.create_post(author_id=user.id, title='Test Post 2', body='This is test post 2.')
            db_session.flush()

            posts = Post.get_all_posts()
            print("posts", posts)
            assert len(posts) == 2
            assert posts[0].title == 'Test Post 2'  # Most recent post should be first
            assert posts[1].title == 'Test Post 1'

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            pytest.fail(f"Test failed: {str(e)}")


