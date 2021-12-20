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
from typing import Dict, Tuple

# If you see different scores locally and on Gradescope this may be an indication
# that you are uploading a different file than the one you are executing locally.
# If this local ID doesn't match the ID on Gradescope then you uploaded a different file.
OUTPUT_UNIQUE_FILE_ID = False
if OUTPUT_UNIQUE_FILE_ID:
    import hashlib, pathlib
    file_hash = hashlib.md5(pathlib.Path(__file__).read_bytes()).hexdigest()
    print(f'Unique file ID: {file_hash}')

def pressure_pd_solution(delta_t: float, current_pressure: float, target_pressure: float,
                         data: Dict) -> Tuple[float, Dict]:
    """
    Student solution to maintain pressure in the fuel tank at a level of 100.

    Args:
        delta_t (float): Time step length.
        current_pressure (float): Current pressure level of the fuel tank.
        target_pressure (float): Target pressure level of the fuel tank.
        data (dict): Data passed through out run.  Additional data can be added and existing values modified.
            'ErrorP': Proportional error.  Initialized to 0.0
            'ErrorD': Derivative error.  Initialized to 0.0

    Returns:
        2 item tuple representing (valve_adjustment, data):
            valve_adjustment (float): amount to adjust flow rate into the fuel tank
            data (dict): (see Args above)
    """
    # TODO: implement PD solution here
    if 'error' in data.keys():
        error = data['error']
    else:
        error = 0.

    cte = target_pressure - current_pressure
    data['ErrorP'] = 0.02
    data['ErrorD'] = 0.2
    valve_adj = data['ErrorP'] * cte + data['ErrorD'] * ( cte - error )
    if (valve_adj > 0):
        valve_adj = min(1.,valve_adj)
    elif ( valve_adj < 0):
        valve_adj = max(-1.,valve_adj)
    data['error'] = cte

    return valve_adj, data


def rocket_pid_solution(delta_t: float, current_velocity: float, optimal_velocity: float,
                        data: Dict) -> Tuple[float, Dict]:
    """
    Student solution for maintaining rocket throttle through the launch based on an optimal flight path

    Args:
        delta_t: Time step length.
        current_velocity: Current velocity of rocket.
        optimal_velocity: Optimal velocity of rocket.
        data: Data passed through out run.  Additional data can be added and existing values modified.
            'ErrorP': Proportional error.  Initialized to 0.0
            'ErrorI': Integral error.  Initialized to 0.0
            'ErrorD': Derivative error.  Initialized to 0.0

    Returns:
        Throttle to set, data dictionary to be passed through run.
    """
    # TODO: implement Rocket PID solution here

    if 'error' in data.keys():
        error = data['error']
        sumerr = data['sumerr']
    else:
        error = 0.
        sumerr = 0.
        data['throttle'] = 0.

    data['ErrorP'] = 30.0
    data['ErrorI'] = 1.0
    data['ErrorD'] = 6.0
    cte = optimal_velocity - current_velocity
    if data['throttle'] >= 0 and data['throttle'] <= 1:
        sumerr += cte
    throttle = data['ErrorP'] * cte + data['ErrorI'] * sumerr + data['ErrorD'] * (cte-error)
    data['error'] = cte
    data['sumerr'] = sumerr
    data['throttle'] = throttle

    return throttle, data


def bipropellant_pid_solution(delta_t: float, current_velocity: float, optimal_velocity: float,
                              data: Dict) -> Tuple[float, float, Dict]:
    """
    Student solution for maintaining fuel and oxidizer throttles through the launch based on an optimal flight path

    Args:
        delta_t: Time step length.
        current_velocity: Current velocity of rocket.
        optimal_velocity: Optimal velocity of rocket.
        data: Data passed through out run.  Additional data can be added and existing values modified.
            'ErrorP': Proportional error.  Initialized to 0.0
            'ErrorI': Integral error.  Initialized to 0.0
            'ErrorD': Derivative error.  Initialized to 0.0

    Returns:
        Fuel Throttle, Oxidizer Throttle to set, data dictionary to be passed through run.
    """
    # TODO: implement Bi-propellant PID solution here

    return 0.0, 0.0, data

def who_am_i():
    # Please specify your GT login ID in the whoami variable (ex: jsmith221).
    whoami = 'sgorucu3'
    return whoami
