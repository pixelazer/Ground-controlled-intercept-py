'''
File for generic functions. Used by GCI.py, the ground-controlled intercept game.
'''

import os
import math

def __init__():
    pass

def clrs():
    os.system('cls' if os.name == 'nt' else 'clear')
    return None

def distance(pointOne, pointTwo):
    return math.sqrt((pointOne[0] - pointTwo[0])**2 + (pointOne[1] - pointTwo[1])**2)