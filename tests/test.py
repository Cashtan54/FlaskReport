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


def test_get_json_report(app, client):
    resp1 = client.get('api/v1/report/')
    resp2 = client.get('api/v1/report/?format=json')
    assert resp1.status_code == 200
    assert b'{"racers":{"1":{"best_lap":"1:04.415","name":"Sebastian Vettel"}' in resp1.data
    assert resp2.status_code == 200
    assert b'{"racers":{"1":{"best_lap":"1:04.415","name":"Sebastian Vettel"}' in resp2.data


def test_get_json_drivers(app, client):
    resp1 = client.get('api/v1/report/drivers/')
    resp2 = client.get('api/v1/report/drivers/?format=json')
    assert resp1.status_code == 200
    assert b'{"racers":{"BHS":{"name":"Brendon Hartley","team":"SCUDERIA TORO ROSSO HONDA"}' in resp1.data
    assert resp2.status_code == 200
    assert b'{"racers":{"BHS":{"name":"Brendon Hartley","team":"SCUDERIA TORO ROSSO HONDA"}' in resp2.data


def test_get_json_driver_by_id(app, client):
    resp1 = client.get('api/v1/report/drivers/?driver_id=SVF')
    resp2 = client.get('api/v1/report/drivers/?format=json&driver_id=SVF')
    wrongresp= client.get('api/v1/report/drivers/?driver_id=123')
    assert resp1.status_code == 200
    assert b'{"SVF":{"best_lap":"1:04.415","end_time":"12.04.03.332",' \
           b'"name":"Sebastian Vettel","start_time":"12.02.58.917","team":"FERRARI"}}\n' == resp1.data
    assert resp2.status_code == 200
    assert b'{"SVF":{"best_lap":"1:04.415","end_time":"12.04.03.332",' \
           b'"name":"Sebastian Vettel","start_time":"12.02.58.917","team":"FERRARI"}}\n' == resp2.data
    assert wrongresp.status_code == 404
    assert b"{'errors': 'No data found', 'status_code': 404}" == wrongresp.data


def test_get_xml_report(app, client):
    resp = client.get('api/v1/report/?format=xml')
    assert resp.status_code == 200
    assert b'<racers><1><best_lap>1:04.415</best_lap><name>Sebastian Vettel</name></1>' in resp.data


def test_get_xml_drivers(app, client):
    resp = client.get('api/v1/report/drivers/?format=xml')
    assert resp.status_code == 200
    assert b'<racers><BHS><name>Brendon Hartley</name><team>SCUDERIA TORO ROSSO HONDA</team></BHS>' in resp.data


def test_get_xml_driver_by_id(app, client):
    resp = client.get('api/v1/report/drivers/?format=xml&driver_id=SVF')
    wrongresp = client.get('api/v1/report/drivers/?format=xml&driver_id=123')
    assert resp.status_code == 200
    assert b'<SVF><best_lap>1:04.415</best_lap><end_time>12.04.03.332</end_time>' \
           b'<name>Sebastian Vettel</name><start_time>12.02.58.917</start_time>' \
           b'<team>FERRARI</team></SVF>' == resp.data
    assert wrongresp.status_code == 404
    assert b"{'errors': 'No data found', 'status_code': 404}" == wrongresp.data