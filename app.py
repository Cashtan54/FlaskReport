from flask import Flask, render_template, request, jsonify, Response
from flask_restful import Resource, Api
from flasgger import Swagger
from dict2xml import dict2xml
from db import *

app = Flask(__name__)
api = Api(app, '/api/v1')
swagger = Swagger(app)
path_to_files = os.path.join(os.path.dirname(__file__), './data')
racers = rep.build_report(path_to_files)
app.config['DATABASE'] = 'racer.db'


@app.before_request
def _db_connect():
    database_name = app.config['DATABASE']
    db.init(database_name, pragmas={'foreign_keys': 1})
    if database_name != 'racer.db':
        fill_db()
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


@app.route('/report/')
@app.route('/report')
def report():
    order = request.args.get('order', default='asc')
    if order == 'asc':
        racers = RacerTime.select(Racer.name, RacerTime.best_lap).join(Racer).order_by(str(RacerTime.best_lap))
        return render_template('report.html',
                               racers=racers)
    elif order == 'desc':
        racers = RacerTime.select(Racer.name, RacerTime.best_lap).join(Racer).order_by(RacerTime.best_lap.desc())
        return render_template('report.html',
                               racers=racers)


@app.route('/report/drivers/')
def drivers():
    driver = request.args.get('driver_id')
    order = request.args.get('order', default='asc')
    if driver:
        return driver_info(driver)
    else:
        if order == 'asc':
            racers = Racer.select().order_by(Racer.name)
        elif order == 'desc':
            racers = Racer.select().order_by(Racer.name.desc())
        return render_template('drivers.html',
                               racers=racers,
                               title='Drivers')


def driver_info(driver):
    racer = RacerTime.select(RacerTime, Racer).join(Racer).where(Racer.driver_id == driver).get_or_none()
    if racer:
        return render_template('driver_info.html',
                               title=f'{driver} info',
                               racer=racer)
    else:
        return render_template('driver_not_found.html',
                               title='Driver not found')


# API part
def get_report():
    racers = RacerTime.select(Racer.name, RacerTime.best_lap).join(Racer)
    racers_dict = dict()
    racers_dict['racers'] = dict()
    for place, racer in enumerate(racers, 1):
        racers_dict['racers'][place] = {
            'name': racer.racer.name,
            'best_lap': racer.best_lap,
        }
    return racers_dict


def get_drivers():
    racers_dict = dict()
    racers_dict['racers'] = dict()
    for racer in Racer.select().order_by('driver_id'):
        racers_dict['racers'][racer.driver_id] = {
            'name': racer.name,
            'team': racer.team,
        }
    return racers_dict


def get_driver_by_id(driver_id):
    racer = RacerTime.select(RacerTime, Racer).join(Racer).where(Racer.driver_id == driver_id).get_or_none()
    if racer:
        racer_data = dict()
        racer_data[racer.racer.driver_id] = {
            'name': racer.racer.name,
            'team': racer.racer.team,
            'start_time': racer.start_time.strftime('%H.%M.%S.%f')[:-3],
            'end_time': racer.end_time.strftime('%H.%M.%S.%f')[:-3],
            'best_lap': racer.best_lap,
        }
        return racer_data


def handler_report(format):
    data = get_report()
    return get_representation(data, format)


def handler_drivers(driver_id, format):
    if driver_id:
        data = get_driver_by_id(driver_id)
    else:
        data = get_drivers()
    return get_representation(data, format)


def get_representation(data, format):
    if data:
        if format == 'json':
            return jsonify(data)
        if format == 'xml':
            return Response(dict2xml(data, newlines=False), content_type='application/xml')
    else:
        notfound = str({'errors': 'No data found', 'status_code': 404})
        return Response(notfound, status=404)


class ReportApi(Resource):
    def get(self):
        """
        file: swagger/report.yml
        """
        format = request.args.get('format', default='json')
        return handler_report(format)


class DriversApi(Resource):
    def get(self):
        """
        file: swagger/drivers.yml
        """
        format = request.args.get('format', default='json')
        driver_id = request.args.get('driver_id')
        return handler_drivers(driver_id, format)


api.add_resource(ReportApi, '/report/')
api.add_resource(DriversApi, '/report/drivers/')

if __name__ == '__main__':
    app.run(debug=True)
