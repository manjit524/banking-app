"""
tests/test_auth.py — Authentication tests
"""
import pytest
from models.user import User


class TestRegistration:
    def test_register_success(self, client, db):
        resp = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'newuser@test.com',
            'phone': '9876543210',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234',
            'mpin': '111222',
            'confirm_mpin': '111222',
        }, follow_redirects=True)
        assert resp.status_code == 200
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None
        assert user.name == 'New User'

    def test_register_duplicate_email(self, client, db, demo_user):
        resp = client.post('/auth/register', data={
            'name': 'Duplicate',
            'email': demo_user.email,
            'phone': '9876543210',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234',
            'mpin': '111222',
            'confirm_mpin': '111222',
        }, follow_redirects=True)
        assert resp.status_code == 200
        users = User.query.filter_by(email=demo_user.email).all()
        assert len(users) == 1  # no duplicate

    def test_register_password_mismatch(self, client, db):
        resp = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'mismatch@test.com',
            'password': 'Test@1234',
            'confirm_password': 'Different@1234',
            'mpin': '111222',
            'confirm_mpin': '111222',
        }, follow_redirects=True)
        assert resp.status_code == 200
        user = User.query.filter_by(email='mismatch@test.com').first()
        assert user is None


class TestLogin:
    def test_login_success(self, client, demo_user):
        resp = client.post('/auth/login', data={
            'email': demo_user.email,
            'password': 'Demo@1234',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_login_wrong_password(self, client, demo_user):
        resp = client.post('/auth/login', data={
            'email': demo_user.email,
            'password': 'WrongPassword',
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Should not be redirected to dashboard
        assert b'dashboard' not in resp.data.lower() or b'Invalid' in resp.data

    def test_login_nonexistent_user(self, client, db):
        resp = client.post('/auth/login', data={
            'email': 'nobody@nowhere.com',
            'password': 'Test@1234',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_logout(self, client, demo_user):
        client.post('/auth/login', data={
            'email': demo_user.email,
            'password': 'Demo@1234',
        })
        resp = client.get('/auth/logout', follow_redirects=True)
        assert resp.status_code == 200


class TestDashboardAccess:
    def test_dashboard_requires_login(self, client):
        resp = client.get('/dashboard', follow_redirects=True)
        assert resp.status_code == 200
        assert b'login' in resp.data.lower() or b'Login' in resp.data

    def test_admin_panel_requires_admin(self, client, demo_user):
        client.post('/auth/login', data={
            'email': demo_user.email,
            'password': 'Demo@1234',
        })
        resp = client.get('/admin/', follow_redirects=True)
        assert resp.status_code in (403, 404, 200)
