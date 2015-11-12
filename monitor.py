import os
import urllib2
import sys

from flask import Flask, render_template

from openapscontrib.predict.predict import Schedule

from highchart import glucose_target_range_chart
from highchart import input_history_area_chart
from highchart import line_chart

from openaps_reports import OpenAPS, Settings


app = Flask(__name__)

@app.route('/')
def monitor():
    aps = app.config['OPENAPS']

    recent_glucose = aps.recent_glucose()
    predicted_glucose = aps.predicted_glucose()
    predicted_glucose_without_dose = aps.predicted_glucose_without_dose()
    targets = Schedule(aps.read_bg_targets()['targets'])
    normalized_history = aps.normalized_history()
    iob = aps.iob()

    basal, bolus, square, carbs = input_history_area_chart(reversed(normalized_history))
    actual_glucose = line_chart(reversed(recent_glucose), name='Glucose')
    predicted_glucose = line_chart(predicted_glucose, name='Predicted')
    predicted_glucose_without_dose = line_chart(predicted_glucose_without_dose, name='Predicted Without Dose')
    iob = line_chart(iob, 'IOB')

    target_glucose = glucose_target_range_chart(targets, actual_glucose, predicted_glucose, predicted_glucose_without_dose)

    return render_template(
        'monitor.html',
        openaps=aps,
        actual_glucose=actual_glucose,
        predicted_glucose=predicted_glucose,
        predicted_glucose_without_dose=predicted_glucose_without_dose,
        target_glucose=target_glucose,
        iob=iob,
        basal=basal,
        bolus=bolus,
        square=square,
        carbs=carbs,
        CSS_ASSETS=CSS_ASSETS,
        JS_ASSETS=JS_ASSETS,
        display_unit=Settings.DISPLAY_UNIT
    )


CSS_ASSETS = (
    ('static/third_party/bootstrap.css', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'),
    ('static/styles.css', None)
)


JS_ASSETS = (
    ('static/third_party/jquery.js', 'https://code.jquery.com/jquery-2.1.4.min.js'),
    ('static/third_party/bootstrap.js', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js'),
    ('static/third_party/highcharts.js', 'http://code.highcharts.com/highcharts.js'),
    ('static/third_party/highcharts-more.js', 'http://code.highcharts.com/highcharts-more.js'),
    ('static/monitor.js', None),
)


def preload_assets():
    for filename, url in (JS_ASSETS + CSS_ASSETS):
        if not os.path.exists(filename):
            print '{} not found, downloading from {}'.format(filename, url)
            try:
                contents = urllib2.urlopen(url).read()
            except ValueError, urllib2.HTTPError:
                pass
            else:
                try:
                    os.makedirs(os.path.dirname(filename))
                except os.error:
                    pass

                with open(filename, mode='w') as fp:
                    fp.write(contents)


if __name__ == '__main__':
    path = sys.argv[1]
    preload_assets()

    if os.path.exists(path):
        path = os.path.abspath(path)
        app.config['OPENAPS'] = OpenAPS(path)
        app.debug = True
        app.run(host='0.0.0.0')
    else:
        exit(1)
