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

import argparse
import json
import numpy as np
import math
import random

from meteorite import Meteorite, MeteorShower
from arena import FIELD_X_BOUNDS, FIELD_Y_BOUNDS
import arena
from turret import Turret


INITIAL_LASER_STATE = {"h": np.pi * 0.5,
                       "hp": 50}

TURRET_INITIAL_POS = {'x': 0.0,
                      'y': -1.0}

P_HIT = 0.75

IN_BOUNDS = {"x_bounds": FIELD_X_BOUNDS,
             "y_bounds": FIELD_Y_BOUNDS}

TEENSY_COEFFICIENT = -1e-12


class MeteorShowerGenerator(object):
    """Creates a group of Meteorites in random positions and initializes motion."""

    def __init__(self, seed):
        """Initialize a generator for a group of Meteorite objects."""
        self.random_state = random.Random(seed)
        self.seed = seed
        self.current_count = 1000

    def random_float_between(self, low, high):
        """Generate a random number between bounds low and high."""
        return ((high - low) * self.random_state.random()) + low

    def generate_meteorite_coeffs(self,
                                  ax_bounds, bx_bounds, cx_bounds,
                                  ay_bounds, by_bounds, cy_bounds, t_start):
        """Generate random coefficients for Meteorite motion."""
        self.current_count += 1
        coeff = ({
            'a_x': self.random_float_between(*ax_bounds),
            'b_x': self.random_float_between(*bx_bounds),
            'c_x': self.random_float_between(*cx_bounds),
            'a_y': self.random_float_between(*ay_bounds),
            'b_y': self.random_float_between(*by_bounds),
            'c_y': self.random_float_between(*cy_bounds),
            't_start': t_start,
            'id': self.current_count,
        })
        return coeff

    def generate(self, t_past, t_future, t_step,
                 turret,
                 arena,
                 a_max=0.00001,
                 b_max=0.01,
                 meteorite_seed=0,
                 min_dist=0.03,
                 cy_bounds=(-0.8, 1.0)):
        """Generate Meteorite coefficients over time."""
        x_bound_coe = 0.05
        ax_left_bounds = (-a_max * x_bound_coe,  a_max * x_bound_coe)
        bx_left_bounds = (0.0, b_max * x_bound_coe)
        cx_left_bounds = (-0.9, 0.0)

        ax_right_bounds = (-a_max * x_bound_coe, a_max * x_bound_coe)
        bx_right_bounds = (-b_max * x_bound_coe, 0.0)
        cx_right_bounds = (0.0, 0.9)

        ay_bounds = (-a_max, TEENSY_COEFFICIENT)
        by_bounds = (-b_max, TEENSY_COEFFICIENT)
        cy_bounds = cy_bounds

        meteorites = []

        def meteorite_init_location_bad(coes):
            tmp_meteorite = Meteorite(coes)
            xypos = tmp_meteorite.xy_pos(0)
            return (xypos[0] <= arena.x_bounds[0]) or \
                (xypos[0] >= arena.x_bounds[1]) or (xypos[1] < 0.0)

        for t in range(t_past, t_future):
            if not (t % t_step):
                if len(meteorites) % 2:
                    theaxbounds = ax_left_bounds
                    thebxbounds = bx_left_bounds
                    thecxbounds = cx_left_bounds
                else:
                    theaxbounds = ax_right_bounds
                    thebxbounds = bx_right_bounds
                    thecxbounds = cx_right_bounds
                regenerate = True
                while regenerate:
                    coeffs = self.generate_meteorite_coeffs(theaxbounds,
                                                            thebxbounds,
                                                            thecxbounds,
                                                            ay_bounds,
                                                            by_bounds,
                                                            cy_bounds, t)
                    regenerate = meteorite_init_location_bad(coeffs)

                a = Meteorite(coeffs)
                meteorites.append(a)

        y_range = cy_bounds[1] - cy_bounds[0]
        y_speed = self.random_float_between(0.0, b_max)
        ticks_across = int(math.floor(y_range / y_speed))
        cy_start = self.random_float_between(*cy_bounds)

        later_coeffs = {'a_x': 0.0,
                        'b_x': 0.0,
                        'c_x': 0.0,
                        'a_y': -y_speed,
                        'b_y': 0.0,
                        'c_y': cy_start,
                        't_start': 0,
                        'id': 0}
        ticks = 0

        while ticks <= t_future:
            regenerate = True
            while regenerate:
                later_coeffs = self.generate_meteorite_coeffs(theaxbounds,
                                                              thebxbounds,
                                                              thecxbounds,
                                                              ay_bounds,
                                                              by_bounds,
                                                              cy_bounds, t)
                regenerate = meteorite_init_location_bad(later_coeffs)
            stack_cnt = 0
            later_coeffs['t_start'] = int(math.floor(ticks))

            ticks = (((later_coeffs['c_y'] - cy_bounds[0]) / y_range) *
                     ticks_across) + ticks
            later_coeffs['c_y'] = cy_bounds[1]

        return MeteorShower(arena, self.seed, P_HIT, meteorites, turret,
                            min_dist)

def args_as_dict(args):
    if isinstance(args, dict):
        return args
    elif isinstance(args, argparse.Namespace):
        return vars(args)
    else:
        raise RuntimeError('cannot convert to dict: %s' % str(args))

def args_as_namespace(args):
    if isinstance(args, dict):
        return argparse.Namespace(**args)
    elif isinstance(args, argparse.Namespace):
        return args
    else:
        raise RuntimeError('cannot convert to namespace: %s' % str(args))


def params(args):
    """Process arguments and set up the environment."""
    my_args = args_as_namespace(args)

    field_generator = MeteorShowerGenerator(seed=my_args.seed)

    dummy_arena = arena.Arena()
    laser_state = {'h': math.pi * 0.5,
                   'hp': my_args.turret_hp}

    dummy_turret = Turret({'x': my_args.turret_x, 'y': -1.0},
                          dummy_arena.contains,
                          my_args.max_angle_change,
                          laser_state)

    field = field_generator.generate(t_past=my_args.t_past,
                                     t_future=my_args.t_future,
                                     t_step=my_args.t_step,
                                     turret=dummy_turret,
                                     arena=dummy_arena,
                                     a_max=my_args.meteorite_a_max,
                                     b_max=my_args.meteorite_b_max,
                                     meteorite_seed=my_args.seed,
                                     min_dist=my_args.min_dist,
                                     cy_bounds=(my_args.meteorite_y_min, my_args.meteorite_y_max))

    return {"meteorites": [dict(a.params) for a in field.meteorites],
            "initial_laser_state": laser_state,
            "in_bounds": dict(IN_BOUNDS),
            "min_dist": my_args.min_dist,
            "noise_sigma": my_args.noise_sigma,
            "nsteps": my_args.nsteps,
            "_args": vars(my_args)}


def main(args):
    """Set up parameters and run the simulation."""
    p = params(args=args)

    f = open(args.outfile, 'w')
    f.write("params = " + json.dumps(p, indent=2) + "\n")
    f.close()

    print("Wrote %s" % args.outfile)


def parser():
    """Parse arguments."""
    prsr = argparse.ArgumentParser("Generate parameters for a test case and write them to file.")
    prsr.add_argument("outfile",
                      help="name of file to write")
    prsr.add_argument("--turret_x",
                      help="X-location of turret (should be in the range (-1.0, 1.0))",
                      type=float,
                      default=0.0)
    prsr.add_argument("--turret_hp",
                      help="Turret's initial health point count",
                      type=int,
                      default=50)
    prsr.add_argument("--t_past",
                      help="time in past (negative integer) from which to start generating meteorites",
                      type=int,
                      default=-100)
    prsr.add_argument("--t_future",
                      help="time into future (positive integer) at which to stop generating meteorites",
                      type=int,
                      default=500)
    prsr.add_argument("--t_step",
                      help="add a meteorite every N-th time step",
                      type=int,
                      default=1)
    prsr.add_argument("--noise_sigma",
                      help="sigma of Gaussian noise applied to meteorite measurements",
                      type=float,
                      default=0.02)
    prsr.add_argument("--nsteps",
                      help="Number of timesteps to simulate",
                      type=int,
                      default=1000)
    prsr.add_argument("--meteorite_a_max",
                      help="maximum magnitude for quadratic meteorite coefficient",
                      type=float,
                      default=0.00001)
    prsr.add_argument("--meteorite_b_max",
                      help="maximum magnitude for linear meteorite coefficient",
                      type=float,
                      default=0.005)
    prsr.add_argument("--meteorite_y_max",
                      help="maximum start height of meteorite",
                      type=float,
                      default=1.0)
    prsr.add_argument("--meteorite_y_min",
                      help="minimum start height of meteorite",
                      type=float,
                      default=0.5)
    prsr.add_argument("--min_dist",
                      help="minimum distance estimate must be from meteorite location to be considered correct; also, if a laser comes within this distance of a meteorite, the meteorite is destroyed.",
                      type=float,
                      default=0.02)
    prsr.add_argument("--max_angle_change",
                      help="maximum increment of the laser's angle (radians)",
                      type=float,
                      default=np.pi/15.0)
    prsr.add_argument("--seed",
                      help="random seed to use when generating meteorites",
                      type=int,
                      default=0)
    return prsr


if __name__ == '__main__':
    args = parser().parse_args()
    main(args)
