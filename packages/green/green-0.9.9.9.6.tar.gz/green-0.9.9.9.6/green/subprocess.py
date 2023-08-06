import logging
import multiprocessing
from multiprocessing.pool import Pool
import random
import shutil
import sys
import tempfile
import traceback

try: # pragma: no cover
    import coverage
except: # pragma: no cover
    coverage = None

from green.result import ProtoTest, ProtoTestResult
from green.loader import getTests


class SubprocessLogger(object):


    def __init__(self, callable):
        self.__callable = callable


    def __call__(self, *args, **kwargs):
        try:
            result = self.__callable(*args, **kwargs)
        except Exception:
            # Here we add some debugging help. If multiprocessing's
            # debugging is on, it will arrange to log the traceback
            logger = multiprocessing.get_logger()
            if not logger.handlers:
                logger.addHandler(logging.StreamHandler())
            logger.error(traceback.format_exc())
            logger.handlers[0].flush()
            # Re-raise the original exception so the Pool worker can
            # clean up
            raise

        # It was fine, give a normal answer
        return result



class DaemonlessProcess(multiprocessing.Process):


    def _get_daemon(self):
        return False


    def _set_daemon(self, value):
        pass


    # 'daemon' attribute needs to always return False
    daemon = property(_get_daemon, _set_daemon)





class LoggingDaemonlessPool(Pool):


    Process = DaemonlessProcess


    def apply_async(self, func, args=(), kwds={}, callback=None):
        return Pool.apply_async(
                self, SubprocessLogger(func), args, kwds, callback)



def poolRunner(test_name, coverage_number=None, omit=[]):
    # Each pool worker gets his own temp directory, to avoid having tests that
    # are used to taking turns using the same temp file name from interfering
    # with eachother.  So long as the test doesn't use a hard-coded temp
    # directory, anyway.
    saved_tempdir = tempfile.tempdir
    tempfile.tempdir = tempfile.mkdtemp()

    # Each pool starts its own coverage, later combined by the main process.
    if coverage_number and coverage:
        cov = coverage.coverage(
                data_file='.coverage.{}_{}'.format(
                    coverage_number, random.randint(0, 10000)),
                omit=omit)
        cov.start()

    # Create a structure to return the results of this one test
    result = ProtoTestResult()
    test = None
    try:
        test = getTests(test_name)
        test.run(result)
    except:
        err = sys.exc_info()
        t             = ProtoTest()
        t.module      = 'green.runner'
        t.class_name  = 'N/A'
        t.description = 'Green encountered an error loading the unit test itself.'
        t.method_name = 'poolRunner'
        result.addError(t, err)

    # Finish coverage
    if coverage_number and coverage:
        cov.stop()
        cov.save()

    # Restore the state of the temp directory
    shutil.rmtree(tempfile.tempdir)
    tempfile.tempdir = saved_tempdir
    return result
