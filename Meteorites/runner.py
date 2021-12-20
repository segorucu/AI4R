
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

from builtins import range
from builtins import object
import math
import random

NUM_STEPS_GOOD_EST_REQUIRED = 5
ESTIMATE_ACCURACY_THRESHOLD = 0.9
INIT_IMMUNITY_DTS = 5
LASER_RIGHT_ANGLE = 0.0
LASER_LEFT_ANGLE = math.pi


def l2(xy0, xy1):
    """Compute the L2 norm (distance) between points xy0 and xy1."""
    dx = xy0[0] - xy1[0]
    dy = xy0[1] - xy1[1]
    return math.sqrt((dx * dx) + (dy * dy))


def clamp(value, lower, upper):
    """Clamp value to be in the range [lower, upper].

    This function is from this StackOverflow answer:
    https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python/58470178#58470178
    """
    # Beginning of code from
    # https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python/58470178#58470178
    return lower if value < lower else upper if value > upper else value
    # End of code from
    # https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python/58470178#58470178


class BaseRunnerDisplay(object):
    """Base class for procedure runners."""

    def setup(self, x_bounds, y_bounds,
              in_bounds,
              margin,
              noise_sigma,
              turret,
              max_angle_change):
        """Create base class version of fcn to initialize procedure runner."""
        pass

    def begin_time_step(self, t):
        """Create base class version of timestep start for procedure runner."""
        pass

    def meteorite_at_loc(self, i, x, y):
        pass

    def meteorite_estimated_at_loc(self, i, x, y, is_match=False):
        pass

    def meteorite_estimates_compared(self, num_matched, num_total):
        pass

    def turret_at_loc(self, h, laser_len=None):
        pass

    def laser_target_heading(self, rad, laser_len):
        pass

    def estimation_done(self, retcode, t):
        pass

    def end_time_step(self, t):
        pass

    def teardown(self):
        pass

    def laser_destruct(self):
        pass


SUCCESS = 'success'
FAILURE_TOO_MANY_STEPS = 'too_many_steps'

# Custom failure states for defense.
DEF_FAILURE = 'explosion'


def add_observation_noise(meteorite_locations, noise_sigma=0.0,
                          random_state=None):
    """Add noise to meteorite observations."""
    my_random_state = random_state if random_state else random.Random(0)
    ret = ()
    for i, x, y in meteorite_locations:
        err_r = my_random_state.normalvariate(mu=0.0, sigma=noise_sigma)
        err_theta = my_random_state.random() * math.pi * 2
        err_x = err_r * math.cos(err_theta)
        err_y = err_r * math.sin(err_theta)
        ret += ((i, x + err_x, y + err_y),)
    return ret


class MalformedEstimate(Exception):
    """Raise this type of exception if an estimate is not a three-tuple."""

    pass


def validate_estimate(tpl):
    """Ensure that estimate of meteorite location is valid."""
    try:
        i, x, y = tpl
        return (int(i), float(x), float(y))
    except (ValueError, TypeError) as e:
        raise MalformedEstimate('Estimated location %s should be of the form (i, x, y), a triple with type (int, float, float) or equivalent numpy types.' % str(tpl))


def run_estimation(field,
                   in_bounds,
                   noise_sigma,
                   min_dist,
                   turret,
                   turret_init_health,
                   max_angle_change,
                   nsteps,
                   seed,
                   display=None):
    """Run the estimation procedure."""
    ret = (FAILURE_TOO_MANY_STEPS, nsteps)
    num_steps_gt_90pct = 0

    random_state = random.Random(seed)

    display.setup(field.x_bounds, field.y_bounds,
                  in_bounds,
                  margin=min_dist,
                  noise_sigma=noise_sigma,
                  turret=turret,
                  max_angle_change=max_angle_change)

    estimated_locs = ()  # estmated locations

    for t in range(nsteps):
        display.begin_time_step(t)

        meteorite_coordinates = field.meteorite_locations(t)

        estimated_locs = turret.observe_and_estimate(
                add_observation_noise(meteorite_coordinates, noise_sigma,
                                      random_state))

        actual = {}
        matches = ()

        for i, x, y in meteorite_coordinates:
            if i == -1:
                continue
            display.meteorite_at_loc(i, x, y)
            actual[i] = (x, y)

        estimated_locs_seen = set()

        for tpl in estimated_locs:

            i, x, y = validate_estimate(tpl)

            if i in estimated_locs_seen:
                continue
            if i == -1:
                continue

            estimated_locs_seen.add(i)

            if i in actual:
                dist = l2((x, y), actual[i])
                is_match = (dist < min_dist)
                if is_match:
                    matches += (i,)
            else:
                is_match = False

            display.meteorite_estimated_at_loc(i, x, y, is_match)

        # estimated = dict([(i, (x, y)) for i, x, y in estimated_locs])

        # Calculate estimates for next time step.
        # estimated_locs = turret.kf_estimate()

        display.meteorite_estimates_compared(len(matches), len(actual))

        # If this step's estimates were good enough, we're done.
        if len(matches) > len(actual) * ESTIMATE_ACCURACY_THRESHOLD:
            num_steps_gt_90pct += 1
        else:
            num_steps_gt_90pct = 0
            display.end_time_step(t)
        if num_steps_gt_90pct >= NUM_STEPS_GOOD_EST_REQUIRED:
            ret = (SUCCESS, t)
            display.end_time_step(t)
            break

    display.estimation_done(*ret)
    display.teardown()
    return ret


def run_defense(field,
                in_bounds,
                noise_sigma,
                min_dist,
                turret,
                turret_init_health,
                max_angle_change,
                nsteps,
                seed,
                display=None):
    """Run defense procedure."""
    ret = (DEF_FAILURE, nsteps)
    random_state = random.Random(seed)

    display.setup(field.x_bounds, field.y_bounds,
                  in_bounds,
                  margin=min_dist,
                  noise_sigma=noise_sigma,
                  turret=turret,
                  max_angle_change=max_angle_change)

    turret_health = turret_init_health

    # This makes meteorites that are below the "hit" boundary before time
    # starts go away before the turret's health can be affected
    field.laser_or_ground_hit(INIT_IMMUNITY_DTS, 0, False)

    # Set the current laser angle to its initial value
    laser_angle_rad = math.pi * 0.5
    laser_is_on = False

    for t in range(0, nsteps):
        display.begin_time_step(t)

        # Actual meteorite locations
        meteorite_coordinates = field.meteorite_locations(t)

        if not meteorite_coordinates:
            break

        # Turret estimating meteorite locations from noisy observations
        estimated_locs = turret.observe_and_estimate(
                add_observation_noise(meteorite_coordinates, noise_sigma,
                                      random_state))

        # display the meteorites in the GUI
        for i, x, y in meteorite_coordinates:
            if i == -1:
                continue
            display.meteorite_at_loc(i, x, y)

        # Display the turret and its health points
        display.turret_health(turret_health, turret_init_health)
        display.turret_at_loc(laser_angle_rad)

        if laser_is_on:
            display.laser_target_heading(laser_angle_rad, 2.0)

        health_loss = field.laser_or_ground_hit(t, laser_angle_rad,
                                                laser_is_on)

        # The turret does not lose any health points during the first
        # INIT_IMMUNITY_DTS timesteps of the simulation
        if t > INIT_IMMUNITY_DTS:
            # If we are past the immunity period of INIT_IMMUNITY_DTS
            # timesteps, deduct one health point for each meteorite that hits
            # the ground.
            turret_health -= health_loss

        if turret_health <= 0:
            display.laser_destruct()
            ret = (DEF_FAILURE, t)
            display.end_time_step(t)
            break
        else:
            # Update laser_angle_rad for turret's aim in the current timestep
            laser_action = turret.get_laser_action(laser_angle_rad)

            if isinstance(laser_action, float) or isinstance(laser_action, int):
                # if laser_action is a float or int, interpret it as the change
                # in the laser's aim angle (in radians) and add it to the
                # laser's previous angle
                laser_is_on = False
                laser_angle_change = float(laser_action)
                # if abs value of change angle is greater than allowed, keep
                # the same sign, but reduce change angle to max_angle_change
                if abs(laser_angle_change) > max_angle_change:
                    laser_angle_change = math.copysign(max_angle_change,
                                                       laser_angle_change)
                # Clip laser angle to within allowed bounds
                laser_angle_rad = clamp(laser_angle_rad + laser_angle_change,
                                        LASER_RIGHT_ANGLE,
                                        LASER_LEFT_ANGLE)
            elif isinstance(laser_action, str):
                # If the laser's action is a string, if the string is 'fire',
                # don't move the laser, but fire it
                if 'fire' in laser_action.lower():
                    laser_is_on = True

            display.end_time_step(t)

    # we have reached the end of simulation time, so if the turret is not dead,
    # this case was a success
    if turret_health > 0:
        ret = (SUCCESS, t)

    display.teardown()
    return ret
