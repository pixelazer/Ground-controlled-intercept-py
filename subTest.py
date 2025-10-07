import matplotlib.pyplot as plt
import math
import pandas as pan

'''
Text-based submarine game. 
The system: player will interact with the sub by contacting crew members, who will performs actions.

TASK LIST:
- Create basic ship class.  (DONE)
- Make the ships move.      (DONE)
- Create convoys - move ships in concert.
- Create contacts system, and basic AI for ships to react to contacts. (Grouping together with convoy, turning together with convoy, etc.)
'''

'''
Magic number zone
'''
dt = 0

# Initialize the ship list from a CSV file.
def init_ship_list(filePath:str) -> pan.DataFrame:
    try:
        shipList = pan.read_csv(filePath, skipinitialspace = True)
        return shipList
    except:
        print("Error: Could not read ship list file.")
        return None

class Ship:
    def __init__(self, shipList: pan.DataFrame, ID: int, pos: list, heading: int = 0, name: str = None):
        # --- Identity variables ---
        self.ID = ID                                                        # ID number. Used to pull from the shipList.
        self.name = name if name is not None else shipList.loc[ID, "name"]  # Ships can have "special" names, if you don't want to use the generic type name.
        self.tonnage = shipList.loc[ID, "tonnage"]                          # Ship tonnage - will be added to player's score after ship killed.

        # --- Ship Performance ---
        self.max_speed = shipList.loc[ID, "max_speed"]
        self.max_turnrate = shipList.loc[ID, "max_turnrate"]                # Turnrate under optimal conditions
        self.max_acceleration = shipList.loc[ID, "max_acceleration"]        # Acceleration when throttle is 1.0
        self.drag_coeff = shipList.loc[ID, "drag_coefficient"]              # How much drag slows the ship

        # --- State variables ---
        self.pos = [float(pos[0]), float(pos[1])]                           # Ship position, [x, y]
        self.heading = float(heading)                                       # Ship heading, degrees. 90 is north
        self.speed = 0.0                                                    

        # --- Control Inputs ---
        self.throttle = 0.0                                                 # %age throttle, or %age max acceleration. 0.0 -> 1.0
        self.rudder_pos = 0.0                                               # Rudder position, or %age max turn rate. -1.0 -> 1.0

    # Sets engine throttle. Clamped between 0.0 and 1.0.
    def set_throttle(self, level):
        self.throttle = max(0.0, min(1.0, level))

    # Sets rudder angle. Clamped between -1.0 (left) and 1.0 (right).
    def set_rudder(self, angle):
        self.rudder_pos = max(-1.0, min(1.0, angle))

    def plot_course(self, desiredPoint):
        # Given a desired point [x, y], return a list of (rudder, throttle) maneuvers to reach it.
        maneuvers = []

        # Parameters for control
        distance_threshold = 5.0
        distance = 6

        while distance > distance_threshold:
            pass

        return maneuvers

    # Updates the ship  every time step "dt".
    def update(self):
        # Update heading
        # Turning is less effective as the ship approaches its max speed
        turn_effectiveness = 1.0 - (self.speed/ self.max_speed)
        effective_turn = self.rudder_pos * turn_effectiveness * self.max_turnrate
        self.heading = (self.heading + effective_turn * dt)% 360

        # Update speed
        # Calculate forces upon the ship...
        thrust = self.throttle * self.max_acceleration
        drag = self.drag_coeff * (self.speed**2)
        # ... and apply them.
        net_accel = thrust - drag
        self.speed += net_accel * dt
        # Speed is clamped between max_speed and 0.
        self.speed = max(0.0, min(self.speed, self.max_speed))

        # Update position
        # self.x += (distance covered) * cos(heading) - for y, swap cos with sin
        self.pos[0] += (self.speed * dt) * math.cos(math.radians(self.heading))
        self.pos[1] += (self.speed * dt) * math.sin(math.radians(self.heading))

    # Called to give the dev an overview of the class for debugging.
    def __repr__(self):
        return (f"{self.name} (ID={self.ID}) - "
                # Prints variables considered immutable
                f"Ship vitals: (Tonnage={self.tonnage}, "
                f"Max Speed={self.max_speed:.2f}, "
                f"Max Acceleration={self.max_acceleration:.2f}, "
                f"Drag coeff.={self.drag_coeff:.2f}) "
                # Printing mutable variables
                f"\nState variables: (x-pos={self.pos[0]}, "
                f"y-pos={self.pos[1]}, "
                f"heading={self.heading}, "
                f"speed={self.speed}, "
                f"throttle setting={self.throttle}, "
                f"rudder setting={self.rudder_pos})")
    

if __name__ == "__main__":
    shipList = init_ship_list("./shipList.csv")

    testShip = Ship(shipList, 0, [0, 0])
    print(testShip.plot_course([25,30]))