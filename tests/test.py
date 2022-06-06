from flask import Flask
import pytest
import app as flaskapp


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


@pytest.fixture
def client():
    flaskapp.app.config['TESTING'] = True
    with flaskapp.app.test_client() as client:
        yield client


def test_report(app, client):
    resp = client.get('/report')
    assert resp.status_code == 200
    assert b'Sebastian Vettel 1:04.415' in resp.data


def test_drivers(app, client):
    resp = client.get('/report/drivers/')
    assert resp.status_code == 200
    assert b'Sebastian Vettel' in resp.data


def test_driver_info(app, client):
    resp = client.get('/report/drivers/?driver_id=SVF')
    assert resp.status_code == 200
    assert b'Best lap: 1:04.415' in resp.data


def test_driver_info_wrong(app, client):
    resp = client.get('/report/drivers/?driver_id=123')
    assert resp.status_code == 200
    assert b'There is no racer with this abb' in resp.data