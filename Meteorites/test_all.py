from __future__ import absolute_import

######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

from builtins import str
from builtins import object
import collections
import io
import multiprocessing as mproc
import sys
import traceback

import runner
import text_display

try:
    from test_one import case_params, run_method, run_kwargs
    import turret as turret
    studentExc = None
    studentTraceback = ''
except Exception as e:
    studentExc = e
    studentTraceback = traceback.format_exc()

ESTIMATE_TIMEOUT = 10
DEFENSE_TIMEOUT = 45

FAILURE_EXCEPTION = 'exception_raised'
FAILURE_TIMEOUT = 'execution_time_exceeded'

GradingTask = collections.namedtuple('GradingTask',
                                     ('case_num', 'method_name', 'weight', 'timeout'))

TASKS = (GradingTask(1, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(2, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(3, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(4, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(5, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(6, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(7, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(8, 'estimate', 9, ESTIMATE_TIMEOUT),
         GradingTask(1, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(2, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(3, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(4, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(5, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(6, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(7, 'defense', 1, DEFENSE_TIMEOUT),
         GradingTask(8, 'defense', 1, DEFENSE_TIMEOUT))


def truncate_runlog(runlog, begin_lines=10, end_lines=10):
    lines = runlog.splitlines()
    if len(lines) <= begin_lines + end_lines:
        return str(runlog)
    else:
        return '\n'.join(lines[:begin_lines] + lines[-end_lines:])

class SingleCaseGrader(object):

    def __init__(self):
        # Using a Manager here to create the Queue resolves timeout
        # issue on Windows.
        self.result_queue = mproc.Manager().Queue(1)

    def _reset(self):
        while not self.result_queue.empty():
            self.result_queue.get()

    def run(self, method_name, case_num):

        self._reset()

        display = text_display.TextRunnerDisplay(fout=io.StringIO())
        msg = ''

        try:
            kwargs = run_kwargs(case_params(case_num))
            retcode, t = run_method(method_name)(display=display, **kwargs)
        except Exception as e:
            retcode = FAILURE_EXCEPTION
            t = 1000
            msg = traceback.format_exc()
#            msg = str(e) + ': ' + str(e.message)

        self.result_queue.put((retcode, t, display.fout.getvalue() + '\n' + msg))

class MultiCaseGrader(object):

    def __init__(self,
                 fout,
                 tasks=TASKS):
        self.fout = fout
        self.tasks = tuple(tasks)

    def run(self):

        score = 0
        max_score = 0

        for task in self.tasks:
            scg = SingleCaseGrader()
            test_process = mproc.Process(target=scg.run,
                    args=(task.method_name, task.case_num))
            runlog = ''

            try:
                test_process.start()
                test_process.join(task.timeout)
            except Exception:
                retcode = FAILURE_EXCEPTION

            if test_process.is_alive():
                test_process.terminate()
                retcode = FAILURE_TIMEOUT
            else:
                if not scg.result_queue.empty():
                    retcode, t, runlog = scg.result_queue.get()
                else:
                    retcode, t, runlog = 'EXITED', -1, 'program exited '

            case_score = task.weight if retcode == runner.SUCCESS else 0

            self.fout.write("begin case {}, method {}\n".format(
                task.case_num, task.method_name))
            self.fout.write(truncate_runlog(runlog))
            self.fout.write("end case {}, method {}, result: {}  ({}/{})\n".format(
                task.case_num, task.method_name, retcode, case_score,
                task.weight))
            self.fout.write('\n\n')

            score += case_score
            max_score += task.weight

        percent = int(round(float(score * 100) / float(max_score)))
        self.fout.write("raw score: %d/%d\n" % (score, max_score))
        self.fout.write("score: %d\n" % percent)
#        self.fout.write("overall score:  %d/%d\n" % (score, max_score))

if __name__ == '__main__':
    if studentExc:
        sys.stdout.write('error importing code:\n\n')
        sys.stdout.write(studentTraceback)
        sys.stdout.write('\n')
        sys.stdout.write('score: 0\n')
    else:
        student_id = turret.who_am_i()
        if student_id:
            try:
                mcg = MultiCaseGrader(sys.stdout)
                mcg.run()
            except Exception as e:
                sys.stdout.write(e)
                sys.stdout.write('score: 0\n')
        else:
            sys.stdout.write("Student ID not specified.  Please fill in 'whoami' variable.\n")
            sys.stdout.write('score: 0\n')
