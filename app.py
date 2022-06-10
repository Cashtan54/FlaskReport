from flask import Flask, render_template, request, jsonify, Response
from flask_restful import Resource, Api
from flasgger import Swagger
import report.report as rep
import os
from xml.etree import ElementTree
import json
from datetime import datetime
from dict2xml import dict2xml

app = Flask(__name__)
api = Api(app, '/api/v1')
swagger = Swagger(app)
path_to_files = os.path.join(os.path.dirname(__file__), './data')
racers = rep.build_report(path_to_files)


@app.route('/report/')
@app.route('/report')
def report():
    order = request.args.get('order')
    return render_template('report.html',
                           racers=sorted(racers,
                                         key=lambda racer: racer.best_lap if racer.best_lap else racer.name,
                                         reverse=get_order(order)))


@app.route('/report/drivers/')
def drivers():
    driver = request.args.get('driver_id')
    order = request.args.get('order')
    if driver:
        return driver_info(driver)
    else:
        return render_template('drivers.html',
                               racers=racers,
                               title='Drivers',
                               reverse_order=get_order(order))


def driver_info(driver):
    for racer in racers:
        if racer.abb == driver:
            return render_template('driver_info.html',
                                   title=f'{driver} info',
                                   racer=racer)
    else:
        return render_template('driver_not_found.html',
                               title='Driver not found')


def get_order(order):
    return order == 'desc'


def get_report():
    racers_dict = dict()
    racers_dict['racers'] = dict()
    for place, racer in enumerate(racers, 1):
        racers_dict['racers'][place] = {
            'name': racer.name,
            'best_lap': racer.best_lap
        }
    return racers_dict


def get_drivers():
    racers_dict = {'racers': rep.parse_abbreviations(path_to_files)}
    return racers_dict


def get_driver_by_id(driver_id):
    racer_data = dict()
    for racer in racers:
        if racer.abb == driver_id:
            racer_data[racer.abb] = {
                'name': racer.name,
                'team': racer.team,
                'start_time': racer.start_time.strftime('%H.%M.%S.%f')[:-3],
                'end_time': racer.end_time.strftime('%H.%M.%S.%f')[:-3],
                'best_lap': racer.best_lap
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
