from flask import Flask, render_template, request
import report.report as rep

app = Flask(__name__)
path_to_files = 'data\\'
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


if __name__ == '__main__':
    app.run()