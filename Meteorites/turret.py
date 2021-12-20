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
from builtins import object
from copy import deepcopy

import numpy as np
from math import *

from matrix import matrix

# If you see different scores locally and on Gradescope this may be an indication
# that you are uploading a different file than the one you are executing locally.
# If this local ID doesn't match the ID on Gradescope then you uploaded a different file.
OUTPUT_UNIQUE_FILE_ID = True
if OUTPUT_UNIQUE_FILE_ID:
    import hashlib, pathlib
    file_hash = hashlib.md5(pathlib.Path(__file__).read_bytes()).hexdigest()
    print(f'Unique file ID: {file_hash}')


class Turret(object):
    """The laser used to defend against invading Meteorites."""

    def __init__(self, init_pos, arena_contains_fcn, max_angle_change,
                 initial_state):
        """Initialize the Turret."""
        self.x_pos = init_pos['x']
        self.y_pos = init_pos['y']
        self.arena_contains_fcn = arena_contains_fcn

        self.bounds_checker = arena_contains_fcn
        self.max_angle_change = max_angle_change

    #   F is not changing through time or meteorite, it is fixed.
        F = np.identity(6)
        F[0, 2] = 1.
        F[1, 3] = 1.
        F[0, 4] = 0.5
        F[1, 5] = 0.5
        F[2, 4] = 1.
        F[3, 5] = 1.
        self.F = F

    #   H is not changing through time or meteorite, it is fixed.
        H = np.zeros((2,6))
        H[0][0] = 1.
        H[1][1] = 1.
        self.H = H

    #   R is fixed and same for all meteorites
        R = np.identity(2)
        R = R * 0.1
        self.R = R

    #   Identity matrix
        self.I = np.identity(6)

    #   Q not used because it was making worse.
        Q = np.identity(6)
        Q = Q * 0.1
        self.Q = Q

    #   Initialize self.Data
        self.Data = [[], [], []]

        self.val = 'turn'


    def observe_and_estimate(self, meteorite_locations):
        """Observe the locations of the Meteorites.

        self is a reference to the current object, the Turret.
        meteorite_locations is a list of observations of meteorite locations.
        Each observation in meteorite_locations is a tuple (i, x, y), where i
        is the unique ID for an meteorite, and x, y are the x, y locations
        (with noise) of the current observation of that meteorite at this
        timestep. Only meteorites that are currently 'in-bounds' will appear in
        this list, so be sure to use the meteorite ID, and not the
        position/index within the list to identify specific meteorites. (The
        list may change in size as meteorites move in and out of bounds.)
        In this function, return the estimated meteorite locations as a tuple
        of (i, x, y) tuples, where i is a meteorite's ID, x is its
        x-coordinate, and y is its y-coordinate.
        """
        # TODO: Update the Turret's estimate of where the meteorites are
        # located at the current timestep and return the updated estimates


        # State uncertainty model P

        ret = []
        for id,xi,yi in meteorite_locations:
            try:
                Pindex = self.Data[0].index(id)
            except ValueError:
                self.Data[0].append(id)
                Pindex = self.Data[0].index(id)
            #   Data[1] is P
                P = np.identity(6)
                self.Data[1].append(P)
            #   Data[2] is x
            #   x(bat) = [x,y,dx,dy,dxx,dyy]
                x = np.zeros((6,1))
                x[0][0] = xi
                x[1][0] = yi
                self.Data[2].append(x)
            else:
                P = self.Data[1][Pindex]
                x = self.Data[2][Pindex]

            Z = np.zeros((2,1))
            Z[0][0] = xi
            Z[1][0] = yi

        #   Observe
            y = Z - np.matmul(self.H,x)
            S = np.matmul(self.H, np.matmul(P, self.H.transpose())) + self.R
            K = np.matmul(P, np.matmul(self.H.transpose(), np.linalg.inv(S)))
            x = x + np.matmul(K, y)
            P = np.matmul((self.I - np.matmul(K, self.H)), P)

        #   Predict
            x = np.matmul(self.F, x)
            P = np.matmul(self.F, np.matmul(P, self.F.transpose())) #+ self.Q

            self.Data[1][Pindex] = P
            self.Data[2][Pindex] = x

        #   To be used for defense

            ret.append((id,x[0][0],x[1][0]))

        self.locations = np.array(ret)
        ret = tuple(ret)
        return ret

    def get_laser_action(self, current_aim_rad):
        """Return the laser's action; it can change its aim angle or fire.

        self is a reference to the current object, the Turret.
        current_aim_rad is the laser turret's current aim angle, in radians,
        provided by the simulation.

        The laser can aim in the range [0.0, pi].
        The maximum amount the laser's aim angle can change in a given timestep
        is self.max_angle_change radians. Larger change angles will be
        clamped to self.max_angle_change, but will keep the same sign as the
        returned desired angle change (e.g. an angle change of -3.0 rad would
        be clamped to -self.max_angle_change).
        If the laser is aimed at 0.0 rad, it will point horizontally to the
        right; if it is aimed at pi rad, it will point to the left.
        If the value returned from this function is the string 'fire' instead
        of a numerical angle change value, the laser will fire instead of
        moving.
        Returns: Float (desired change in laser aim angle, in radians), OR
        String 'fire' to fire the laser
        """
        # TODO: Update the change in the laser aim angle, in radians, based
        # on where the meteorites are currently, OR return 'fire' to fire the
        # laser at a meteorite

        if (self.val == 'turn'):
            self.locations = self.locations[self.locations[:,0]>0]
            x = self.locations[:,1]
            y = self.locations[:,2]
            if (len(y)<1):
                return 'fire'
            Pindex = np.argmin(y)
            metnum = self.locations[:,0][Pindex]
            xi = x[Pindex]
            yi = y[Pindex]
            dx = xi
            dy = yi + 1.
            final = atan2(dy, dx)
            final = max(final,0.001)
            final = min(final,pi - 0.001)
            decision = final - current_aim_rad
            if (decision > self.max_angle_change):
                decision = self.max_angle_change - 0.0001
            elif (decision < -self.max_angle_change):
                decision = -self.max_angle_change + 0.0001
            self.val = 'fire'
        else:
            decision = 'fire'
            self.val = 'turn'

        return decision  # or 'fire'


def who_am_i():
    # Please specify your GT login ID in the whoami variable (ex: jsmith221).
    whoami = 'sgorucu3'
    return whoami
