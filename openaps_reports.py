"""
Interface for openaps reports

"""
from datetime import datetime
from glob import glob
import json
import os


class Settings(object):
    """Filenames containing report data are relative to the openaps path"""

    # What glucose measurement scale should we use. Use "mg/dL" for USA, otherwise "mmol/L"
    DISPLAY_UNIT = "mg/dL"

    # A report containing glucose data in reverse-chronological order. Each entry should contain both a local timestamp
    # and a glucose value:
    # {
    #   "date" | "display_time" : "<ISO date string>",
    #   "sgv" | "amount" | "glucose" : 100
    # }
    CLEAN_GLUCOSE = 'clean_glucose.json'

    # A report containing IOB levels in chronological order. Each entry should contain a local timestamp and an IOB value:
    # {
    #   "date": "<ISO date string>",
    #   "amount": 1.0
    #   "unit": "U"
    # }
    IOB = 'iob_history.json'


    # A report containing history data in reverse-chronological order. Each entry should be in the dictionary format as
    # defined by openapscontrib.mmhistorytools, and should be fully munged by those steps for best display.
    NORMALIZE_HISTORY = 'prepared_history_with_dose.json'

    # A report containing predicted glucose values in chronological order. Each entry should contain a local timestamp
    # and a glucose value:
    # {
    #   "date": "<ISO date string>",
    #   "glucose": 100
    # }
    PREDICT_GLUCOSE = 'predict_glucose_with_dose.json'

    # A report containing predicted glucose values prior to added dose in chronological order. Each entry should contain a local timestamp
    # and a glucose value:
    # {
    #   "date": "<ISO date string>",
    #   "glucose": 100
    # }
    PREDICT_GLUCOSE_WITHOUT_DOSE = 'predict_glucose_without_future_basal.json'
    
    # A report containing the output of the openaps medtronic vendor command "read_bg_targets".
    READ_BG_TARGETS = 'read_bg_targets.json'


class OpenAPS(object):
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)

    # Filesystem utils ####################

    def _all_files(self):
        for f in sorted(glob('{}/*.json'.format(self.path)), key=os.path.getmtime, reverse=True):
            yield f

        for f in glob('{}/*.ini'.format(self.path)):
            yield f

    def all_filenames(self):
        for f in self._all_files():
            yield os.path.basename(f)

    def all_filenames_and_data(self):
        for f in self._all_files():
            with open(f) as fp:
                yield os.path.basename(f), datetime.fromtimestamp(os.path.getmtime(f)), fp.read()

    def _get_report_path(self, report_filename):
        return os.path.join(self.path, report_filename)

    def _read_json(self, filename, default=None):
        try:
            with open(self._get_report_path(filename)) as fp:
                return json.load(fp)
        except (IOError, ValueError):
            return default

    # Reports #############################

    def read_bg_targets(self):
        return self._read_json(Settings.READ_BG_TARGETS, {'targets': []})

    def predicted_glucose(self):
        return self._read_json(Settings.PREDICT_GLUCOSE, [])
        
    def predicted_glucose_without_dose(self):
        return self._read_json(Settings.PREDICT_GLUCOSE_WITHOUT_DOSE, [])

    def recent_glucose(self):
        return self._read_json(Settings.CLEAN_GLUCOSE, [])

    def normalized_history(self):
        return self._read_json(Settings.NORMALIZE_HISTORY, [])

    def iob(self):
        return self._read_json(Settings.IOB, [])
