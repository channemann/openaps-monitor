import os
import urllib2
import sys

from flask import Flask, render_template

from openapscontrib.predict.predict import Schedule

from chart import glucose_line_chart
from chart import input_history_area_chart
from highchart import glucose_line_chart
from highchart import glucose_target_range_chart

from openaps_reports import OpenAPS, Settings


app = Flask(__name__)

@app.route('/')
def monitor():
    aps = app.config['OPENAPS']

    recent_glucose = aps.recent_glucose()
    predicted_glucose = aps.predicted_glucose()
    targets = Schedule(aps.read_bg_targets()['targets'])
    normalized_history = aps.normalized_history()
    iob = aps.iob()
    recent_dose = aps.recent_dose()

    history_cols, history_rows = input_history_area_chart(normalized_history, iob, Settings.DISPLAY_UNIT)
    actual_glucose = glucose_line_chart(reversed(recent_glucose))
    predicted_glucose = glucose_line_chart(predicted_glucose)

    return render_template(
        'monitor.html',
        openaps=aps,
        history_cols=history_cols,
        history_rows=history_rows,
        actual_glucose=actual_glucose,
        predicted_glucose=predicted_glucose,
        target_glucose=glucose_target_range_chart(targets, actual_glucose[0]['x'], predicted_glucose[-1]['x']),
        CSS_ASSETS=CSS_ASSETS,
        JS_ASSETS=JS_ASSETS,
        display_unit=Settings.DISPLAY_UNIT
    )


CSS_ASSETS = (
    ('static/third_party/bootstrap.css', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'),
    ('static/third_party/tooltip.css', 'https://ajax.googleapis.com/ajax/static/modules/gviz/1.0/core/tooltip.css'),
    ('static/styles.css', None)
)


FONT_ASSETS = (
    ('static/third_party/Roboto.ttf', 'http://fonts.gstatic.com/s/roboto2/v5/Nd9v8a6GbXQiNddD22JCiwLUuEpTyoUstqEm5AMlJo4.ttf'),
)


JS_ASSETS = (
    ('static/third_party/jquery.js', 'https://code.jquery.com/jquery-2.1.4.min.js'),
    ('static/third_party/bootstrap.js', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js'),
    ('static/third_party/jsapi.js', 'https://www.google.com/jsapi'),
    ('static/third_party/chart.js', 'https://www.google.com/uds/api/visualization/1.1/9543863e4f7c29aa0bc62c0051a89a8a/'
                        'dygraph,webfontloader,format+en,default+en,ui+en,line+en,corechart+en.I.js'),
    ('static/monitor.js', None),
    ('static/third_party/highcharts.js', 'http://code.highcharts.com/highcharts.js'),
    ('static/third_party/highcharts-more.js', 'http://code.highcharts.com/highcharts-more.js')
)


def preload_assets():
    for filename, url in (JS_ASSETS + CSS_ASSETS + FONT_ASSETS):
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
