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

import sys
import numpy as np

from runner import BaseRunnerDisplay

class TextRunnerDisplay(BaseRunnerDisplay):

    def __init__(self, fout=None):
        self.fout = fout

    def _log(self, s):
        fout = self.fout or sys.stdout
        if hasattr(self, 't'):
            fout.write("[t {0}]  {1}\n".format(self.t, s))
        else:
            fout.write("{0}\n".format(s))

    def setup(self, x_bounds, y_bounds,
              in_bounds,
              margin,
              noise_sigma,
              turret,
              max_angle_change):
        self._log("setup  margin: {0}  noise_sigma: {1} max_angle_change: {2}".format(margin, noise_sigma, max_angle_change))
        self.t = 0

    def begin_time_step(self, t):
        self.t = t

    def meteorite_at_loc(self, i, x, y):
        pass

    def meteorite_estimated_at_loc(self, i, x, y, is_match=False):
        pass

    def meteorite_estimates_compared(self, num_matched, num_total):
        self._log("estimates matching: {0} / {1}".format(num_matched, num_total))
        pass

    def turret_at_loc(self, hdg):
        pass

    def turret_health(self, hp, hp0):
        self._log(
            "Turret has {0} (out of initial {1}) health points remaining.".format(
                int(hp), int(hp0)))

    def laser_target_heading(self, rad, laser_len):
        self._log("Turret aiming at {0} rad ({1} deg)".format(rad, rad / np.pi * 180))

    def estimation_done(self, retcode, t):
        self._log("estimation done: {0}".format(retcode))

    def end_time_step(self, t):
        pass
