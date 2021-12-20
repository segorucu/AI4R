"""
 === Introduction ===

   The assignment is broken up into two parts.
   Part A:
        Create a SLAM implementation to process a series of landmark (gem) measurements and movement updates.
        The movements are defined for you so there are no decisions for you to make, you simply process the movements
        given to you.
        Hint: A planner with an unknown number of motions works well with an online version of SLAM.
    Part B:
        Here you will create the action planner for the robot.  The returned actions will be executed with the goal
        being to navigate to and extract a list of needed gems from the environment.  You will earn points by
        successfully extracting the list of gems from the environment. Extraction can only happen if within the
        minimum distance of 0.15.
        Example Actions (more explanation below):
            'move 3.14 1'
            'extract B 1.5 -0.2'
    Note: All of your estimates should be given relative to your robot's starting location.
    Details:
    - Start position
      - The robot will land at an unknown location on the map, however, you can represent this starting location
        as (0,0), so all future robot location estimates will be relative to this starting location.
    - Measurements
      - Measurements will come from gems located throughout the terrain.
        * The format is {'landmark id':{'distance':0.0, 'bearing':0.0, 'type':'D'}, ...}
      - Only gems that have not been collected and are within the horizon distance will return measurements.
    - Movements
      - Action: 'move 1.570963 1.0'
        * The robot will turn counterclockwise 90 degrees and then move 1.0
      - Movements are stochastic due to, well, it being a robot.
      - If max distance or steering is exceeded, the robot will not move.
    - Needed Gems
      - Provided as list of gem types: ['A', 'B', 'L', ...]
      - Although the gem names aren't real, as a convenience there are 26 total names, each represented by an
        upper case letter of the alphabet (ABC...).
      - Action: 'extract'
        * The robot will attempt to extract a specified gem from the current location..
      - When a gem is extracted from the terrain, it no longer exists in the terrain, and thus won't return a
        measurement.
      - The robot must be with 0.15 distance to successfully extract a gem.
      - There may be gems in the environment which are not required to be extracted.
    The robot will always execute a measurement first, followed by an action.
    The robot will have a time limit of 5 seconds to find and extract all of the needed gems.
"""

from typing import Dict, List, Tuple
import matrix
import math

# If you see different scores locally and on Gradescope this may be an indication
# that you are uploading a different file than the one you are executing locally.
# If this local ID doesn't match the ID on Gradescope then you uploaded a different file.
OUTPUT_UNIQUE_FILE_ID = False
if OUTPUT_UNIQUE_FILE_ID:
    import hashlib, pathlib
    file_hash = hashlib.md5(pathlib.Path(__file__).read_bytes()).hexdigest()
    print(f'Unique file ID: {file_hash}')

class SLAM:
    """Create a basic SLAM module.
    """

    def __init__(self):
        """Initialize SLAM components here.
        """
        # TODO
        self.Omega = matrix.matrix()
        self.Xi = matrix.matrix()
        self.list_lm = []
        self.time = 0
        self.bearing = 0.
        self.loclm = []

    # Provided Functions
    def get_coordinates_by_landmark_id(self, landmark_id: str):
        """
        Retrieves the x, y locations for a given landmark

        Args:
            landmark_id: The id for a processed landmark

        Returns:
            the coordinates relative to the robots frame with an initial position of 0.0
        """
        # TODO:

        i = self.list_lm.index(landmark_id)
        i = 2 * i




        return self.loclm[i][0],self.loclm[i+1][0]

    def process_measurements(self, measurements: Dict):
        """
        Process a new series of measurements.

        Args:
            measurements: Collection of measurements
                in the format {'landmark id':{'distance':0.0, 'bearing':0.0, 'type':'B'}, ...}

        Returns:
            x, y: current belief in location of the robot
        """
        # TODO:
        self.time += 1
        if self.time == 1:
            dim = 2
            self.Omega.zero(dim, dim)
            self.Omega.value[0][0] = 1.0
            self.Omega.value[1][1] = 1.0
            self.Xi.zero(dim, 1)
            # self.Xi.value[0][0] = 0.0
            # self.Xi.value[1][0] = 0.0

        for key, value in measurements.items():
            if key in self.list_lm:
                m = 2 * ( 1 + self.list_lm.index(key))
            else:
                self.list_lm.append(key)
                m = self.Omega.dimx
                list1 = [*range(0,m)]
                self.Omega = self.Omega.expand(m+2,m+2,list1,list1)
                self.Xi = self.Xi.expand(m + 2, 1, list1, [0])
            distance = value['distance']
            measurement_noise = max(distance,1)
            angle = self.bearing + value['bearing']
            measurement = [distance*math.cos(angle), distance*math.sin(angle)]

            for b in range(2):
                self.Omega.value[b][b] += 1.0 / measurement_noise
                self.Omega.value[m + b][m + b] += 1.0 / measurement_noise
                self.Omega.value[b][m + b] += -1.0 / measurement_noise
                self.Omega.value[m + b][b] += -1.0 / measurement_noise
                self.Xi.value[b][0] += -measurement[b] / measurement_noise
                self.Xi.value[m + b][0] += measurement[b] / measurement_noise

        mu = self.Omega.inverse() * self.Xi
        x, y = mu[0], mu[1]




        return x, y

    def process_movement(self, steering: float, distance: float):
        """
        Process a new movement.

        Args:
            steering: amount to turn
            distance: distance to move

        Returns:
            x, y: current belief in location of the robot
        """
        # TODO:
        self.bearing += steering
        motion = [distance*math.cos(self.bearing),distance*math.sin(self.bearing)]

        dim = self.Omega.dimx
        list1 = [0, 1]
        for i in range(4, dim + 2):
            list1.append(i)

        self.Omega = self.Omega.expand(dim + 2, dim + 2, list1, list1)
        self.Xi = self.Xi.expand(dim + 2, 1, list1, [0])
        motion_noise = 1.5

        for b in range(4):
            self.Omega.value[b][b] += 1.0 / motion_noise
        for b in range(2):
            self.Omega.value[b][b + 2] += -1.0 / motion_noise
            self.Omega.value[b + 2][b] += -1.0 / motion_noise
            self.Xi.value[b][0] += -motion[b] / motion_noise
            self.Xi.value[b + 2][0] += motion[b] / motion_noise

        newlist = range(2, len(self.Omega.value))
        a = self.Omega.take([0, 1], newlist)
        b = self.Omega.take([0, 1])
        c = self.Xi.take([0, 1], [0])
        self.Omega = self.Omega.take(newlist) - a.transpose() * b.inverse() * a
        self.Xi = self.Xi.take(newlist, [0]) - a.transpose() * b.inverse() * c

        mu = self.Omega.inverse() * self.Xi

        self.loclm = mu[2:]

        return mu[0][0], mu[1][0]


class GemExtractionPlanner:
    """
    Create a planner to navigate the robot to reach and extract all the needed gems from an unknown start position.
    """

    def __init__(self, max_distance: float, max_steering: float):
        """
        Initialize your planner here.

        Args:
            max_distance: the max distance the robot can travel in a single move.
            max_steering: the max steering angle the robot can turn in a single move.
        """
        # TODO
        self.max_distance = max_distance
        self.max_steering = max_steering

        self.Omega = matrix.matrix()
        self.Xi = matrix.matrix()
        self.list_lm = []
        self.lmtype = []
        self.time = 0
        self.bearing = 0.
        self.loclm = []
        self.d = 0.5
        self.fail = 0

    def process_measurements(self, measurements: Dict):
        """
        Process a new series of measurements.

        Args:
            measurements: Collection of measurements
                in the format {'landmark id':{'distance':0.0, 'bearing':0.0, 'type':'B'}, ...}

        Returns:
            x, y: current belief in location of the robot
        """
        # TODO:
        self.time += 1
        if self.time == 1:
            dim = 2
            self.Omega.zero(dim, dim)
            self.Omega.value[0][0] = 1.0
            self.Omega.value[1][1] = 1.0
            self.Xi.zero(dim, 1)
            # self.Xi.value[0][0] = 0.0
            # self.Xi.value[1][0] = 0.0

        for key, value in measurements.items():
            if key in self.list_lm:
                m = 2 * ( 1 + self.list_lm.index(key))
            else:
                self.list_lm.append(key)
                self.lmtype.append(value['type'])
                m = self.Omega.dimx
                list1 = [*range(0,m)]
                self.Omega = self.Omega.expand(m+2,m+2,list1,list1)
                self.Xi = self.Xi.expand(m + 2, 1, list1, [0])
            distance = value['distance']
            measurement_noise = max(distance,1)
            angle = self.bearing + value['bearing']
            measurement = [distance*math.cos(angle), distance*math.sin(angle)]

            for b in range(2):
                self.Omega.value[b][b] += 1.0 / measurement_noise
                self.Omega.value[m + b][m + b] += 1.0 / measurement_noise
                self.Omega.value[b][m + b] += -1.0 / measurement_noise
                self.Omega.value[m + b][b] += -1.0 / measurement_noise
                self.Xi.value[b][0] += -measurement[b] / measurement_noise
                self.Xi.value[m + b][0] += measurement[b] / measurement_noise

        mu = self.Omega.inverse() * self.Xi
        x, y = mu[0][0], mu[1][0]
        self.loclm = mu[2:]




        return x, y

    def process_movement(self, steering: float, distance: float):
        """
        Process a new movement.

        Args:
            steering: amount to turn
            distance: distance to move

        Returns:
            x, y: current belief in location of the robot
        """
        # TODO:
        self.bearing += steering
        motion = [distance*math.cos(self.bearing),distance*math.sin(self.bearing)]

        dim = self.Omega.dimx
        list1 = [0, 1]
        for i in range(4, dim + 2):
            list1.append(i)

        self.Omega = self.Omega.expand(dim + 2, dim + 2, list1, list1)
        self.Xi = self.Xi.expand(dim + 2, 1, list1, [0])
        motion_noise = 1.5

        for b in range(4):
            self.Omega.value[b][b] += 1.0 / motion_noise
        for b in range(2):
            self.Omega.value[b][b + 2] += -1.0 / motion_noise
            self.Omega.value[b + 2][b] += -1.0 / motion_noise
            self.Xi.value[b][0] += -motion[b] / motion_noise
            self.Xi.value[b + 2][0] += motion[b] / motion_noise

        newlist = range(2, len(self.Omega.value))
        a = self.Omega.take([0, 1], newlist)
        b = self.Omega.take([0, 1])
        c = self.Xi.take([0, 1], [0])
        self.Omega = self.Omega.take(newlist) - a.transpose() * b.inverse() * a
        self.Xi = self.Xi.take(newlist, [0]) - a.transpose() * b.inverse() * c

        mu = self.Omega.inverse() * self.Xi

        self.loclm = mu[2:]

        return mu[0][0], mu[1][0]

    def get_coordinates_by_landmark_id(self, landmark_id: str):
        """
        Retrieves the x, y locations for a given landmark

        Args:
            landmark_id: The id for a processed landmark

        Returns:
            the coordinates relative to the robots frame with an initial position of 0.0
        """
        # TODO:

        i = self.list_lm.index(landmark_id)
        i = 2 * i

        return self.loclm[i][0],self.loclm[i+1][0]

    def next_move(self, needed_gems: List[str], measurements: Dict):
        """Next move based on the current set of measurements.
        Args:
            needed_gems: List of gems remaining which still need to be found and extracted.
            measurements: Collection of measurements from gems in the area.
                                {'landmark id': {
                                                    'distance': 0.0,
                                                    'bearing' : 0.0,
                                                    'type'    :'B'
                                                },
                                ...}
        Return: action: str, points_to_plot: dict [optional]
            action (str): next command to execute on the robot.
                allowed:
                    'move 1.570963 1.0'  - Turn left 90 degrees and move 1.0 distance.
                    'extract B 1.5 -0.2' - [Part B] Attempt to extract a gem of type B from your current location.
                                           This will succeed if the specified gem is within the minimum sample distance.
            points_to_plot (dict): point estimates (x,y) to visualize if using the visualization tool [optional]
                            'self' represents the robot estimated position
                            <landmark_id> represents the estimated position for a certain landmark
                format:
                    {
                        'self': (x, y),
                        '<landmark_id_1>': (x1, y1),
                        '<landmark_id_2>': (x2, y2),
                        ....
                    }
        """
        # TODO

        x,y = self.process_measurements(measurements)
        dist = 1000.0
        for i in range(len(self.lmtype)):
            gem = self.lmtype[i]
            if gem in needed_gems:
                id1 = self.list_lm[i]
                x1, y1 = self.get_coordinates_by_landmark_id(id1)
                point = (x1,y1)
                current_position = (x,y)
                d, b = self.measure_distance_and_bearing_to(point,current_position)
                if d < dist:
                    dist = d
                    gem_sel = gem
                    id = id1
                    bearing = b
        if len(self.lmtype) == 0:
            self.d += 0.1
            self.fail += 1
            dist = self.d
            bearing = 0.
            if self.fail%5==0:
                bearing = self.max_steering
        try:
            gem_sel
        except NameError:
            self.d += 0.1
            self.fail += 1
            dist = self.d
            bearing = 0.
            if self.fail % 5 == 0:
                bearing = self.max_steering
        else:
            pass

        #Loc = self.get_coordinates_by_landmark_id(id)
        move = min(dist,self.max_distance)
        if move < 0.05 and len(self.lmtype)>0:
            txt = 'extract ' + str(gem_sel) + ' ' + str(x) + ' ' + str(y)
        else:
            steer = bearing
            if (steer > self.max_steering):
                move = 0.0 #*= self.max_steering / steer
                steer = self.max_steering
            elif (steer < -self.max_steering):
                move = 0.0 #*= abs(self.max_steering / steer)
                steer = -self.max_steering
            move = min(move,0.8*dist)
            if (dist < 0.2):
                move = min(move,0.05)
            txt = 'move ' + str(steer) + ' ' + str(move)
            x, y = self.process_movement(steer, move)



        dict = {}
        dict['self'] = (x,y)

        return txt, dict

    def measure_distance_and_bearing_to(self,point: Tuple, current_position: Tuple):
        """
            Measure the distance and bearing to a point.

            Args:
                point: Point to take measurement reading to.
                noise: Measure using set noise values.

            Returns:
                The distance and bearing to the point.
            """

        distance_to_point = self.compute_distance(current_position, point)
        bearing_to_point = self.compute_bearing(current_position, point)
        bearing_to_point = bearing_to_point - self.bearing
        if bearing_to_point < -math.pi:
            bearing_to_point += 2. * math.pi
        elif bearing_to_point > math.pi:
            bearing_to_point -= 2. * math.pi



        return distance_to_point, bearing_to_point


    def compute_distance(self, p: Tuple, q: Tuple):
        """Compute the distance between two points.

        Args:
            p: Point 1
            q: Point 2

        Returns:
            The Euclidean distance between the points.
        """

        x1, y1 = p
        x2, y2 = q

        dx = x2 - x1
        dy = y2 - y1

        return math.sqrt(dx ** 2 + dy ** 2)

    def compute_bearing(self, p: Tuple, q: Tuple):
        """
        Compute bearing between two points.

        Args:
            p: Point 1
            q: Point 2

        Returns:
            The bearing as referenced from the horizontal axis.
        """
        x1, y1 = p
        x2, y2 = q

        dx = x2 - x1
        dy = y2 - y1

        return math.atan2(dy, dx)

def who_am_i():
    # Please specify your GT login ID in the whoami variable (ex: jsmith221).
    whoami = 'sgorucu3'
    return whoami
