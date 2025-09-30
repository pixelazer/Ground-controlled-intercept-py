from enum import Enum                   #eeeeenummunum
import math
from matplotlib import pyplot as plt    # test feature to plot ship movement
from alive_progress import alive_bar    # progress bar for long load ops


'''
Magic constants zone
'''
class ContactType(Enum):    # Type of contact. Used in the contacts dict.
    CONVOY = 0 
    NEUTRAL = 1
    HOSTILE = 2


'''
Text-based submarine game. 
The system: player will interact with the sub by contacting crew members, who will performs actions.

TASK LIST:
- Create basic ship class, with movement and health.    (DONE)
- Make the ships move.                                  (DONE)
- Create convoys - move ships in concert
- Create contacts system, and basic AI for ships to react to contacts. (Grouping togethe rwith convoy, turning together with convoy, etc.)
'''


class GameController():
    def __init__(self, ships: list) -> None:
        self.ships = ships

    '''
    "Update All" fuction, to ease the game loop.
    For now, only updates ships.
    '''
    def update_all(self) -> None:
        # Update all ships in the list.
        for ship in self.ships:
            ship.update()
            
    def change_all_courses(self, newHeading: int, newSpeed: int) -> None:
        for ship in self.ships:
            ship.change_course(newHeading, newSpeed)


'''
Generic ship template. Needs to account for navigation, convoy behavior, contacts, and damage.
'''
class Ship():
    def __init__(self, name: str, agility: float, health: int = 1, team: int = 0) -> None:
        # Externally supplied variables.
        self.name = name            # Ship's name. For display purposes.
        # self.type = type          # Type of ship. Why commented out? Because it's redundant anyway. Ship types will be defined by pulling from the class.
        self.health = health        # Health of ship. If 0, ship is destroyed.
        self.agility = agility      # How quickly the ship can change course. Scales from 0 (cannot change course) to 1 (instant change).
        self.team = team            # "Team" number. Allows grouping of ships into convoys. A ship will only concern itself with ships on its team.
                                    # Prevents a convey escort from panicking because a torpedo was sighted halfway across the map.

        # Internally defined variables.
        self.pos = [0, 0]           # Position in x, y coordinates.
                                    # Why not depth? Because subs will be a different class, of course ;)

        '''
        A note on ship movement. For now, ships only have and angular heading, and a speed. 
        However, this system can lead to some unrealistic behavior, such as a ship being able to turn faster the further it is from its desired course.
        This is fine in the internim, but a better system would be to have:
            A "net speed", inculuding speed and turn speed,
            An "acceleration", including straight-line accel and angular acceleration, 
            A cap on the aforementioned acceleration and speeds.
        This would let ships behave more realistically. 
        First, speed changes position, and then acceleration changes speed.
        '''
        self.course = (0, 0)        # Actual course in degrees, speed in knots.
        self.desiredCourse = (0, 0) # Desired course - course the ship will shift towards.
        self.contacts = {}          # Dict of contacts. Contacts are other ships the ship is aware of.
                                    # Will be in the format {contactID: (contactObject, contactType, lastKnownPos, lastKnownCourse)}
                                    # contactType will be an enum.
    
    # Method that updates the ship. Changes positiona and course.
    def update(self) -> None:
        # Update position based on course and speed. Keep in mind course is in degrees. Line is so long due to tuples not supporting item assignment.
        self.pos = (self.pos[0] + int(self.course[1] * math.cos(math.radians(self.course[0]))), self.pos[1] + int(self.course[1] * math.sin(math.radians(self.course[0]))))

        # Update course to move towards desired course. TODO - refine this.
        self.course = (self.course[0] + (self.desiredCourse[0] - self.course[0]) * self.agility, self.desiredCourse[1] + (self.desiredCourse[1] - self.course[1]) * self.agility)

        # Stop if HP == 0.
        if self.health <= 0:
            self.desiredCourse = self.course
            self.change_course(newSpeed = 0)

    # Method to change the ship's DESIRED course. Will hold previous course if no new course is given. 
    # This allows for only the speed or heading to be changed.
    def change_course(self, newHeading: int = None, newSpeed: int = None) -> None:
        if newHeading is None:
            newHeading = self.desiredCourse[0]
        if newSpeed is None:
            newSpeed = self.desiredCourse[1]

        # Update dersiredCourse.
        self.desiredCourse = (abs(newHeading % 360), newSpeed) # Makes sure heading is always between 0 and 359.

'''
Class for "fighting" ships. Needs to account for weapons, sensors, etc.
'''
class CombatShip(Ship):
    pass

class PlayerSub(Ship):
    def __init__(self, name: str = "INS Magarmachh", agility: float = 0.5, health: int = 1, team: int = 0) -> None:
        super().__init__(name, agility, health)

        # Externally supplied variables.
        self.name = name            
        self.health = health        
        self.agility = agility      
        self.team = team            

        # Internally defined variables.
        self.pos = [0, 0, 0]                   
        self.team = 0

if __name__ == "__main__":
    # List of all ships
    ships = []

    # Initialize loading bar, with 5 objects to load.
    # A word on the bar - bar() increments it, and bar.text() sets the text next to it.
    with alive_bar(total = 10) as bar:

        testTanker = Ship("Test Tanker 1", 0.01, team = 1)
        bar()
        testTanker2 = Ship("Test Tanker 2", 0.01, team = 1)
        bar()
        testTanker3 = Ship("Test Tanker 3", 0.01, team = 1)
        bar()
        testTanker4 = Ship("Test Tanker 4", 0.01, team = 1)
        bar()

        ships = [testTanker, testTanker2, testTanker3, testTanker4]
        x_points = []
        y_points = []
        bar()

        game = GameController(ships)
        bar()

        testTanker.pos = [0, 0]
        testTanker2.pos = [0, 50]
        testTanker3.pos = [50, 50]
        testTanker4.pos = [50, 0]

        # Set initial courses.
        game.change_all_courses(newHeading = 90, newSpeed = 50)

        for i in ships:
            for j in range(400):
                # Record positions for plotting.
                x_points.append(i.pos[0])
                y_points.append(i.pos[1])
                i.update()

            plt.plot(x_points, y_points, label = i.name)
            x_points = []
            y_points = []
            bar()

    # Plot tanker movements.
    
    plt.show()