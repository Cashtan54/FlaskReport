from flask import Flask, render_template, request, jsonify, Response
from flask_restful import Resource, Api
from flasgger import Swagger
import report.report as rep
import os
from xml.etree import ElementTree
import json
from datetime import datetime

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


def get_json_report():
    racers_dict = dict()
    racers_dict['racers'] = dict()
    for place, racer in enumerate(racers, 1):
        racers_dict['racers'][place] = dict()
        racers_dict['racers'][place]['name'] = racer.name
        racers_dict['racers'][place]['best_lap'] = racer.best_lap
    return jsonify(racers_dict)


def get_json_drivers():
    racers_dict = dict()
    racers_dict['racers'] = rep.parse_abbreviations(path_to_files)
    return jsonify(racers_dict)


def get_json_driver_by_id(driver_id):
    racer_data = dict()
    for racer in racers:
        if racer.abb == driver_id:
            racer_data[racer.abb] = dict()
            racer_data[racer.abb]['name'] = racer.name
            racer_data[racer.abb]['team'] = racer.team
            racer_data[racer.abb]['start_time'] = racer.start_time
            racer_data[racer.abb]['end_time'] = racer.end_time
            racer_data[racer.abb]['best_lap'] = racer.best_lap
            return jsonify(racer_data)
    else:
        racer_data[driver_id] = 'There is no racer with this abb'
        return jsonify(racer_data)


def get_xml_report():
    root = ElementTree.Element('racers')
    for place, racer in enumerate(racers, 1):
        racer_place = ElementTree.SubElement(root, 'racer_place')
        racer_place.text = str(place)
        name = ElementTree.SubElement(racer_place, 'name')
        name.text = racer.name
        best_lap = ElementTree.SubElement(racer_place, 'best_lap')
        best_lap.text = racer.best_lap
    tree = ElementTree.tostring(root)
    return tree


def get_xml_drivers():
    root = ElementTree.Element('racers')
    for racer, data in rep.parse_abbreviations(path_to_files).items():
        print(racer, data)
        racer_abb = ElementTree.SubElement(root, 'racer_id')
        racer_abb.text = racer
        racer_name = ElementTree.SubElement(racer_abb, 'name')
        racer_name.text = data['name']
        racer_team = ElementTree.SubElement(racer_abb, 'team')
        racer_team.text = data['team']
    tree = ElementTree.tostring(root)
    return tree


def get_xml_driver_by_id(driver_id):
    root = ElementTree.Element('racer')
    for racer in racers:
        if racer.abb == driver_id:
            racer_abb = ElementTree.SubElement(root, 'racer_abb')
            racer_abb.text = racer.abb
            racer_name = ElementTree.SubElement(racer_abb, 'name')
            racer_name.text = racer.name
            racer_team = ElementTree.SubElement(racer_abb, 'team')
            racer_team.text = racer.team
            racer_start_time = ElementTree.SubElement(racer_abb, 'start_time')
            racer_start_time.text = racer.start_time.strftime('%M.%S.%f')[:-3]
            racer_end_time = ElementTree.SubElement(racer_abb, 'end_time')
            racer_end_time.text = racer.end_time.strftime('%M.%S.%f')[:-3]
            racer_best_lap = ElementTree.SubElement(racer_abb, 'best_lap')
            racer_best_lap.text = racer.best_lap
            tree = ElementTree.tostring(root)
            return tree
    else:
        racer_abb = ElementTree.SubElement(root, 'racer_abb')
        racer_abb.text = driver_id
        no_data = ElementTree.SubElement(racer_abb, 'response')
        no_data.text = 'There is no racer with this abb'
        tree = ElementTree.tostring(root)
        return tree


class ReportApi(Resource):
    def get(self):
        format = request.args.get('format')
        if format is None or format == 'json':
            return get_json_report()
        if format == 'xml':
            return Response(get_xml_report(), content_type='application/xml')


class DriversApi(Resource):
    def get(self):
        format = request.args.get('format')
        driver_id = request.args.get('driver_id')
        if driver_id:
            if format is None or format == 'json':
                return get_json_driver_by_id(driver_id)
            if format == 'xml':
                return Response(get_xml_driver_by_id(driver_id), content_type='application/xml')
        else:
            if format is None or format == 'json':
                return get_json_drivers()
            if format == 'xml':
                return Response(get_xml_drivers(), content_type='application/xml')


api.add_resource(ReportApi, '/report/')
api.add_resource(DriversApi, '/report/drivers/')

if __name__ == '__main__':
    app.run(debug=True)
