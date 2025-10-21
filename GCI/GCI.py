'''
GCI - Ground Controlled Intercept
Aryan Takalkar
Made for Terminal Game Jam

A savage enemy creeps over the horizon. Bombers snake over an iron sky, casting their Plexiglass eyes upon our dear nation.
You, the player, are our last line of defense. Take command of fighters in GCI: Ground Controlled Intercept, and guide them though cloud and fog
to destroy the fiendish bombers and defend our glorious homeland.
'''

import math
from utils import *
from random import randint

'''
Magic number zone.
'''
DELTA_T = 6.0
# Map data. XMID is horizontal center of the map. YMID is vertical center. 
# These are stored seperately so I can organize things with the center of the map as origin (x = x + MAP_XMID) instead of the top left. 
# Furthermore, Y is inverted everywhere. This is because top rows are drawn first.
MAP_WIDTH = 50
MAP_HEIGHT = 50
MAP_XMID = MAP_WIDTH//2
MAP_YMID = MAP_HEIGHT//2
CITY_POS = [(MAP_XMID - 5, MAP_YMID - 5), (MAP_XMID + 10, MAP_YMID - 12), (MAP_XMID - 2, MAP_YMID - 7), (MAP_XMID + 3, MAP_YMID + 4)]
BASE_POS = (MAP_XMID, MAP_YMID)
# Fighter data
FIGHTER_NUMBER = 4
FIGHTER_MAXFUEL = 14
FIGHTER_MAXTURN = 90
FIGHTER_MAXSPEED = 2
# Bomber data
BOMBER_TIMER = 3   # The lower this is, the faster they spawn
BOMBER_MAXFUEL = 45
BOMBER_MAXTURN = 30
BOMBER_MAXSPEED = 1
BOMB_RADIUS = 1
# Assorted variables
INTERCEPT_RADIUS = 3
# Display characters for each
FIGHTER_CHAR = "^"
BOMBER_CHAR = "v"
CITY_CHAR = "#"
BASE_CHAR = "A"
CRASH_CHAR = "*"

# Game "dialogue".
WELCOME_MSG = f"Welcome to GCI, the ground-controlled intercept simulation game!\nThis game was built for the MNIT Terminal Game Jam.\n\nIn this game, you control fighter aircraft, with the aim to shoot down missiles before they bomb your cities.\nYou will see a map every turn; this is your view of the world.\n{BOMBER_CHAR} indicates bombers; {FIGHTER_CHAR} indicates fighters. The \"identifying number\" of each aircraft is printed above it, and its heading is printed below.\nYour fighters will automatically shoot down any bombers they come close to - this happens at a range of {INTERCEPT_RADIUS}.\nGuide your fighters by giving them orders in the following format:\n >>> f1 <f1_heading> f2 <f2_heading> f3 <f3_heading>\nDo not deviate from this!\n Happy hunting, and good luck!"
LOSS_CITIES = "All of your cities were bombed out, Commander. You have cost us the war. \nConsider yourself dishonourably dismissed!"
LOSS_FIGHTERS = "Your fighters have been run into the ground. You have cost us valuable men, and have left us defenseless against the onslaught. \nConsider yourself dishonourably dismissed!"
VICTORY_MSG = f"Congratulations, commander. With a force of just {FIGHTER_NUMBER}, you have repelled the enemy bombardment.\nWord of your deeds will travel far. We are lucky to have you.\nYou can expect a medal, and if fortune favours you, a promotion."

'''
Incremental-inheritance class-ladder hell. The "blocks".
Blocks should NOT interact with each other. They must NOT reference each other.
They must simply provide just enough data about themselves to the glue for the glue to do its job.
TODO - cut this down!

Inheritance tree:
    GameObject (Unused)
    ||               ||          ||         ||
    ||               ||          ||         ||
  PLANE (Unused)    City        Base      Crash
    ||   \\ 
    ||    \\ 
FIGHTER   BOMBER

All-caps objects are dynamic.
'''
# Generic game object. Has a position and a display character. 
# Can only return its position.
class GameObject():
    def __init__(self, x, y, displayChar):
        self.x = float(x)
        self.y = float(y)
        self.displayChar = displayChar
    
    def get_pos(self) -> tuple:
        return (int(self.x), int(self.y))

# Airbase.
# Simply a GameObject with a display char.
class Base(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, BASE_CHAR)

# City.
# Simply a GameObject with a display char.
class City(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, CITY_CHAR)

# Wreck.
# Simply a GameObject with a display char. Placed at the position any aircraft is "downed"
class Wreck(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, CRASH_CHAR)

# Generic plane. No display char.
# Can move, turn, run out of fuel, and update itself.
class Plane(GameObject):
    def __init__(self, x, y, displayChar):
        super().__init__(x, y, displayChar)
        self.fuel = 0
        self.heading = 0.0
        self.desiredHeading = self.heading
        self.alive = True

        self.maxSpeed = 0
        self.maxTurn = 0

    def change_heading(self, newHeading: int):
        self.desiredHeading = newHeading % 360
    
    def update(self):
        if self.fuel <= 0:
            return
        
        # Update heading
        # Calculate the shortest difference between desired and current heading
        diff = (self.desiredHeading - self.heading + 180) % 360 - 180
        # Clamp the turn to the maxTurn rate
        delta_h = max(-self.maxTurn, min(self.maxTurn, diff))
        # Apply the turn and wrap around 360
        self.heading = (self.heading + delta_h) % 360

        # Update position
        rad = math.radians(self.heading)
        self.x += self.maxSpeed * math.cos(rad)
        self.y -= self.maxSpeed * math.sin(rad)

        # Clamp position to map boundaries
        self.x = max(0, min(self.x, MAP_WIDTH - 1))
        self.y = max(0, min(self.y, MAP_HEIGHT - 1))

        self.fuel -= 1

# Fighter.
# Simply a plane that can refuel. Has a display char.
class Fighter(Plane):
    def __init__(self, x, y):
        super().__init__(x, y, FIGHTER_CHAR)
        self.fuel = FIGHTER_MAXFUEL
        self.maxSpeed = FIGHTER_MAXSPEED
        self.maxTurn = FIGHTER_MAXTURN

    def refuel(self):
        self.fuel = FIGHTER_MAXFUEL

# Bomber.
# A plane that can "target" a point. It will attempt to face that point. Has a display char.
class Bomber(Plane):
    def __init__(self, x, y, targetX, targetY):
        super().__init__(x, y, BOMBER_CHAR)
        self.fuel = BOMBER_MAXFUEL
        self.maxSpeed = BOMBER_MAXSPEED
        self.maxTurn = BOMBER_MAXTURN
        
        # There two variables keep track of where the bomber wants to bomb.
        self.targetX = targetX
        self.targetY = targetY

        # Point the bomber towards the target
        self.set_heading_towards_target(self.targetX, self.targetY, True)

    def set_heading_towards_target(self, targetX, targetY, instant: bool):
        # Set heading towards target. instant = True if the bomber wants to snap straight to the target heading.
        deltaX = targetX - self.x
        deltaY = targetY - self.y

        rad = math.atan2(-deltaY, deltaX)
        if instant:
            self.heading = math.degrees(rad)
            self.desiredHeading = math.degrees(rad)
        else:
            self.desiredHeading = math.degrees(rad)


'''
Class that handles the game itself. The "glue".
'''
class GameController:
    def __init__(self):
        # Initializing self variables
        self.turns = 0
        self.score = 0
        self.headline = ""  # Prints an update for the turn

        # Initializing fixed objects
        self.cities = [City(i[0], i[1]) for i in CITY_POS]
        self.base = Base(BASE_POS[0], BASE_POS[1])

        # Initializing dynamic objects
        # FIX: range(FIGHTER_NUMBER) not FIGHTER_NUMBER - 1
        self.fighters = [Fighter(MAP_XMID + 2*i, MAP_YMID + 2*i) for i in range(FIGHTER_NUMBER)]
        self.bombers = []
        self.crashes = []

    def spawn_bomber(self):
        # Summons a bomber.
        # Decide which side the bomber will spawn from - N, E, S, W
        side = randint(0, 3)
        # Decide which city the bomber will target, and fetch its co-ords.
        # Grab a city from self.cities to only target living cities.
        # TODO: If the city a bomber is targeting is bombed before it gets there, the bomber will continue on, "wasting" itself. Fix?
        targetCity = randint(0, len(self.cities) - 1)
        targetCity = self.cities[targetCity].get_pos()

        if side == 0:
            bomberPos = (randint(0, MAP_WIDTH - 1), 0)
        elif side == 1:
            bomberPos = (0, randint(0, MAP_HEIGHT - 1))
        elif side == 2:
            bomberPos = (randint(0, MAP_WIDTH - 1), MAP_HEIGHT - 1)
        elif side == 3:
            bomberPos = (MAP_WIDTH - 1, randint(0, MAP_HEIGHT - 1))
        
        # Create the bomber.
        self.bombers.append(Bomber(bomberPos[0], bomberPos[1], targetCity[0], targetCity[1]))

    def title_card(self):
        # Run when the game starts up.
        print(WELCOME_MSG)

    def end_game(self):
        # Run when the game ends.
        if len(self.cities) <= 0:
            print(LOSS_CITIES)
        elif len(self.fighters) <= 0:
            print(LOSS_FIGHTERS)
        else:
            print(VICTORY_MSG)

    def update(self):
        # Update everything in the game. The beating heart.
        self.turns += 1
        self.headline = ""

        # --- Fighter Update Loop ---
        # Use a new list to avoid modifying list while iterating
        surviving_fighters = []
        for i, f in enumerate(self.fighters):
            f.update()
            
            # Refuel the fighter if at base
            # FIX: Moved this *before* the crash check so fighters can land
            if distance(f.get_pos(), self.base.get_pos()) <= 1.0:
                if f.fuel < FIGHTER_MAXFUEL: # Only report if it actually needed fuel
                    self.headline += f"Fighter {i + 1} has been refueled. "
                    f.refuel()
            
            # Fighter crashes if no fuel.
            if f.fuel <= 0:
                self.headline += f"Fighter {i + 1} has crashed. "
                self.crashes.append(Wreck(f.get_pos()[0], f.get_pos()[1]))
                f.alive = False
            
            if f.alive:
                surviving_fighters.append(f)
                self.headline += f"Fighter {i + 1} is at {f.get_pos()}, facing {round(f.heading)}. "
        
        self.fighters = surviving_fighters # Replace old list with survivors

        # --- Bomber Update Loop ---
        surviving_bombers = []
        for i, b in enumerate(self.bombers):
            b.update()
            
            # Bomber crashes if no fuel.
            if b.fuel <= 0:
                self.headline += f"Bomber {i + 1} has crashed. "
                self.crashes.append(Wreck(b.get_pos()[0], b.get_pos()[1]))
                b.alive = False

            else:
                # Check for intercepts
                for f_i, f in enumerate(self.fighters):
                    if distance(f.get_pos(), b.get_pos()) <= INTERCEPT_RADIUS:
                        self.headline += f"Bomber {i + 1} has been intercepted by fighter {f_i + 1}. "
                        self.crashes.append(Wreck(b.get_pos()[0], b.get_pos()[1]))
                        b.alive = False
                        break # Bomber is shot down, no need to check other fighters

                # Check if it has reached the city; destroy the city if so.
                # Only check if bomber is still alive
                if b.alive:
                    # Iterate over a *copy* of self.cities so we can remove from the original
                    for c in self.cities[:]: 
                        if distance(b.get_pos(), c.get_pos()) <= BOMB_RADIUS:
                            city_index = self.cities.index(c) + 1 # Get index *before* removing
                            self.headline += f"City {city_index} has been bombed! "
                            self.crashes.append(Wreck(c.x, c.y))
                            self.cities.remove(c)
                            b.alive = False
                            break # Bomber is destroyed after bombing one city
            
            if b.alive:
                surviving_bombers.append(b)
                self.headline += f"Bomber {i + 1} is at {b.get_pos()}, facing {round(b.heading)}. "

        self.bombers = surviving_bombers

        # Spawn new bomber if the spawn timer is a multiple of the spawn rate
        # FIX: Added check for len(self.cities) to prevent crash when all cities are gone
        if self.turns % BOMBER_TIMER == 0 and len(self.cities) > 0:
            self.spawn_bomber()
            self.headline += f"Bomber sighted at {self.bombers[-1].get_pos()}! "


        # Placeholder headline, if no other headline has been generated this turn.
        if len(self.headline) == 0:
            self.headline = "Your orders, sir?"

    def draw(self):
        # Draw the map to the screen, along with any other data.
        clrs()
        
        # Initializing a blank map
        # FIX: Use MAP_WIDTH/HEIGHT directly, not -1
        map = [[" " for _ in range(MAP_WIDTH)] for _ in range (MAP_HEIGHT)]

        # --- Draw static objects ---
        statics = self.cities + [self.base] + self.crashes
        for obj in statics:
            x, y = obj.get_pos()
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                map[y][x] = obj.displayChar

        # --- Draw dynamic objects and labels (more efficient) ---
        # Draw cities labels
        for i, c in enumerate(self.cities):
            x, y = c.get_pos()
            if 0 <= x < MAP_WIDTH and 0 <= y + 1 < MAP_HEIGHT:
                map[y + 1][x] = str(i + 1)
        
        # Draw fighters and labels
        for i, f in enumerate(self.fighters):
            x, y = f.get_pos()
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                map[y][x] = f.displayChar
                # Add labels with bounds checking
                if y + 1 < MAP_HEIGHT:
                    map[y + 1][x] = str(i + 1)
                if y - 1 >= 0:
                    map[y - 1][x] = str(round(f.heading))

        # Draw bombers and labels
        for i, b in enumerate(self.bombers):
            x, y = b.get_pos()
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                map[y][x] = b.displayChar
                # Add labels with bounds checking
                if y + 1 < MAP_HEIGHT:
                    map[y + 1][x] = str(i + 1)
                if y - 1 >= 0:
                    map[y - 1][x] = str(round(b.heading))

        # Print this turn's "headline"
        print(self.headline)
        print("_" * MAP_WIDTH)
        
        # Actually draw the map.
        for row in map:
            print(*row, sep = "")
        
        # Bottom border
        print("_" * MAP_WIDTH)

        # Fighter fuel levels
        for i, f in enumerate(self.fighters):
            print(f"f{i + 1} has {f.fuel} turns of fuel. ")

    def take_inp(self):
        # Inputs will be taken in the form
        # "f1 150 f2 90 f3 0" etc.
        command = input("Enter your orders: \n>>> ").split()

        if len(command) != 0:
            try:
                # OPTIMIZE: Clearer loop for parsing
                for i in range(0, len(command), 2):
                    fighter_id_str = command[i]   # e.g., "f1"
                    heading_str = command[i+1]    # e.g., "150"

                    fighter_index = int(fighter_id_str[1]) - 1
                    heading = int(heading_str)

                    # Check if fighter index is valid
                    if 0 <= fighter_index < len(self.fighters):
                        self.fighters[fighter_index].change_heading(heading)
                    else:
                        print(f"Invalid order: Fighter {fighter_index + 1} does not exist.")

            # OPTIMIZE: Catch specific errors
            except (IndexError, ValueError): 
                print("Invalid order format, Commander! Use 'f1 <hdg> f2 <hdg>'... We have no time for tomfoolery!")
            except Exception as e:
                print(f"An unexpected error occurred with your order: {e}")

    def run(self):
        # Function that actually runs the game.
        self.title_card()

        while (len(self.cities) > 0) and (len(self.fighters) > 0) and (self.turns <= 51):
            # Run the game as long as the player has at least one city left and one fighter left.
            # The game lasts 51 turns.
            self.update()
            self.draw()
            self.take_inp()

        self.end_game()

'''
Main function. Runs the program.
'''
if __name__ == "__main__":
    game = GameController()
    game.run()