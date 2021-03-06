"""Define full-analyzer model
TODO raise error when each main process fails
TODO Separate severity of loggers for success and fails"""
import collections
import configparser
import logging
import multiprocessing
import sys
import time

from primely.models import pdf_converter, queueing, recording, txt_converter, visualizing
from primely.views import console, utils


# create logger with '__name__'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler with a defined log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handler(s)
# formatter = logging.Formatter('{asctime} {name} {levelname:8s} {message}', style='{')
formatter = logging.Formatter('[{levelname}] {message}', style='{')
ch.setFormatter(formatter)
# add the handler(s) to the logger
logger.addHandler(ch)
# don't allow passing events to higher level loggers
logger.propagate = False

PDF_STORAGE     = 'data/input'
TEXT_STORAGE    = 'data/tmp/txt'
JSON_STORAGE    = 'data/tmp/json'
GRAPH_STORAGE   = 'data/output/graphs_and_charts'
REPORT_STORAGE  = 'data/output/json'
GRAPH_FILENAME  = 'income_timechart.png'
REPORT_FILENAME = 'paycheck_timechart.json'


def timeit(method):
    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        if 'log_time' in kwargs:
            name = kwargs.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


class ConverterModel(object):
    """Contains functions that process a paycheck object.
    Steps:
    1. Get all pdf file name for paycheck
    2. for each file, proceed Extract and Transform
    """

    def __init__(self, filename, status=None):
        self.filename = filename
        self.status = status
        self.response = collections.defaultdict()

    # @timeit
    def convert_pdf_into_text(self):
        """Utilize pdf_converter module to convert a pdf file to a text file"""

        pdf_converter.convert_pdf_to_txt(self.filename, 
            PDF_STORAGE, TEXT_STORAGE)

    # @timeit
    def convert_text_into_dict(self):
        """Transform txt data to dict format"""

        try:
            converter = txt_converter.PartitioningDispatcher(self.filename, TEXT_STORAGE)
        except:
            self.status = 'error'
            msg = 'Could not complete text transformation process'
            logger.critical({
                'status': self.status,
                'msg': msg
            })
        else:
            self.status = 'success'
            msg = 'Text transformation complete'
            logger.info({
                'status': self.status,
                'msg': msg
            })
        finally:
            pass
        
        self.response = converter.get_response() 
        logger.debug({
            'filename': self.filename,
            'data': self.response
        })

    # @timeit
    def convert_dict_into_json(self):
        """Record dict_data to json files"""

        dest_info = {
            'filename': self.filename,
            'dir_path': JSON_STORAGE,
            'file_path': None
        }

        recording_model = recording.RecordingModel(**dest_info)
        recording_model.record_data_in_json(self.response)


class Dispatcher(object):

    @staticmethod
    def fully_convert(filename):
        coverter = ConverterModel(filename)
        coverter.convert_pdf_into_text()
        coverter.convert_text_into_dict()
        coverter.convert_dict_into_json()

class FullAnalyzer(object):
    """This is the main process of Primely which can handle multiple 
    pdf files to iterate through all the functionalities that the 
    Primely package ratains."""

    def __init__(self, speak_color='green', filenames=None, dataframe=None):
        super().__init__()
        self.speak_color = speak_color
        self.filenames = filenames
        self.dataframe = dataframe

    def starting_msg(self):
        template = console.get_template('start_proc.txt', self.speak_color)
        print(template.substitute({
            # 'message': 'Check data/output/graphs_and_charts for exported image!'
        }))

    def _setup_output_dir(func):
        """Decorator to set a queue if not loaded"""

        def wrapper(self):
            utils.setup_output_dir(TEXT_STORAGE)
            utils.setup_output_dir(JSON_STORAGE)
            utils.setup_output_dir(REPORT_STORAGE)
            return func(self)
        return wrapper

    def _queue_decorator(func):
        """Decorator to set a queue if not loaded"""

        def wrapper(self):
            if not self.filenames:
                self.filenames = queueing.extract_filenames(PDF_STORAGE)
                print('Queue is set')
            return func(self)
        return wrapper

    # @timeit
    @_setup_output_dir
    @_queue_decorator
    def process_all_input_data(self):
        """Use AnalyzerModel to process all PDF data"""

        """ Multiprocess"""
        with multiprocessing.Pool(8) as p:
            r = p.map(Dispatcher.fully_convert, self.filenames)
            logging.debug('executed')
            logging.debug(r)

        """ Single-process"""
        # for filename in self.filenames:
        #     Dispatcher.fully_convert(filename)

    def create_dataframe_in_time_series(self):
        """Visualize data from json file and export a graph image """
        # TODO Implement sorting, renaming, camouflaging (0/3)
        try:
            visual = visualizing.DataframeFactory(JSON_STORAGE)
            visual.classify_json_data_in_categories(visual.categories)
            # visual.sort_table()
            # visual.rename_columns()
            # visual.camouflage_values(True)
            self.dataframe = visual.category_dataframe
            # print(self.dataframe)
        except:
            self.status = 'error'
            msg = 'Chart output failed'
            logger.info({
                'status': self.status,
                'msg': msg
            })
        else:
            self.status = 'success'
            msg = 'Chart output complete'
            logger.info({
                'status': self.status,
                'msg': msg
            })
        finally:
            pass

    def get_packaged_paycheck_series(self):
        """
        1. Package 3 categories of dataframes in the hash table (self.dataframe)
        2. Get the Package
        """
        try:
            organizer = visualizing.OrganizerModel(**self.dataframe)
            organizer.trigger_update_event()
        except:
            self.status = 'error'
            msg = 'Json export failed'
            logger.info({
                'status': self.status,
                'msg': msg
            })
            raise
        else:
            self.status = 'success'
            msg = 'Json export complete'
            logger.info({
                'status': self.status,
                'msg': msg
            })
        finally:
            return organizer.get_response()

    def export_in_jsonfile(self, response):
        """Export api response of this whole package in a json file"""


        dir_path = REPORT_STORAGE
        dest_info = {
            'filename': REPORT_FILENAME,
            'dir_path': dir_path,
            'file_path': None
        }
        recording_model = recording.RecordingModel(**dest_info)
        recording_model.record_data_in_json(response)


    def ending_msg(self):
        # TODO include filenames and each processed status in the msg
        template = console.get_template('end_proc.txt', self.speak_color)
        print(template.substitute({
            'message': 'Check data/output/json/paycheck_timechart.json for preprocessed data!'
        }))

if __name__ == "__main__":
    pass