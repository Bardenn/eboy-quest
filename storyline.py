from typing import List, Optional
import pygame
import time

import game
from config import *

class Interactable:
    def __init__(self, identifier: str, keywords: List[str]):
        self.keywords = keywords
        self.identifier = identifier
        self.wow = None

    def does_interact(self, inp: str) -> bool:
        """Returns True if inp results in iteraction with this instance"""
        return inp in [kw % self.identifier for kw in self.keywords]

    def interact(self, cls, inp, current_room, events, inventory):
        raise NotImplementedError()

class Item(Interactable):
    def __init__(self, name):
        super(Item, self).__init__(name, ["pick up %s", "pick %s up", "take %s", "use %s"])

class Character(Interactable):
    def __init__(self, name):
        super(Character, self).__init__(name, ["speak with %s", "talk to %s", "wave at %s"])

class Room:
    def __init__(self, description, peek_description, textures, interactables, loop=True, fps=10):
        self.set_textures(textures, loop)
        self.fps = fps
        self.interactables = interactables
        self.description = description
        self.peek_description = peek_description
        self.connections = [None, None, None, None] # tuple, N E S W
        self.keys = [None, None, None, None]
        self._frame = 0
        self._endtime = time.time()

    def set_connection(self, direction: game.Cardinal, other_room, key: Optional[Interactable] = None, bidirectional: bool = True):
        self.connections[direction.value] = other_room
        self.keys[direction.value] = key

        if bidirectional:
            other_directions = {game.Cardinal.NORTH: game.Cardinal.SOUTH, game.Cardinal.SOUTH: game.Cardinal.NORTH, game.Cardinal.EAST: game.Cardinal.WEST, game.Cardinal.WEST: game.Cardinal.EAST}
            other_direction = other_directions[direction]
            other_room.set_connection(other_direction, self, key, bidirectional = False)

    def render(self, screen):
        time_since_last_frame = time.time() - self._endtime 
        screen.blit(self._textures[self._frame], (0, 0))
        if 1.0/time_since_last_frame < self.fps:
            self._frame += 1
            if self._frame >= self._texturecount:
                if self.loop:
                    self._frame = 0
                else:
                    self._frame = self._texturecount - 1
            self._endtime = time.time()

    def on_enter(self, cls, inp, events, inventory):
        events.append({"type": game.EventType.OUTPUT, "value": self.description})

    def set_textures(self, textures, loop=True):
        self._textures = []
        for texture in textures:
            img = pygame.image.load(texture)
            img = pygame.transform.scale(img, (WIDTH, HEIGHT//3*2))
            self._textures.append(img)
        self._texturecount = len(self._textures)
        self.loop = loop
        self._frame = 0


"""
def get_item_interact(message):
    def interact(self, inp, current_room, events, inventory):
        inventory.append(self)
        current_room.interactables.remove(self)
        events.append({"type": game.EventType.OUTPUT, "value": message})
    return interact
"""
        

def get_demo_room() -> Room:
    rooms = []

    
    key1 = Item("a golden key")
    def key1_interact(self, inp, current_room, events, inventory):
        if self in inventory:
            events.append({"type": game.EventType.OUTPUT, "value": "You need to find a door for this key"})
            return current_room
        inventory.append(self)
        current_room.interactables.remove(self)
        current_room.set_textures(["keynot.jpg"])
        events.append({"type": game.EventType.OUTPUT, "value": "You picked up the key"})
        return current_room
    # key1.interact = get_item_interact("You picked up the key") functional programming is whack
    key1.interact = key1_interact #holy shit

    dwarf = Character("Dwarfilius")

    first_room = Room("You are in a dimly lit room.", "You see a door to a room", ["keyonfloor.jpg", "keynot.jpg",], [key1, dwarf], fps=5)
    
    second_room = Room("You are on an open field", "You see door that leads outside", ["600 copy 7.jpg"], [])
    def on_win(cls, inp, events, inventory):
        events.append({"type": game.EventType.OUTPUT, "value": "welldone cunt, you won"})

    second_room.on_enter = on_win



    first_room.set_connection(game.Cardinal.NORTH, second_room, key1)
    second_room.set_connection(game.Cardinal.SOUTH, first_room)
    
    return first_room

def get_initial_room(events: List[dict]):
    events.append({"type": game.EventType.OUTPUT, "value": "You wake up on the floor with a lingering headache, you see the forest canopy above you."}) #starting lore
    start_room = Room("Forest, the place you woke up.", "a clearing with a mark on the grass.", ["Assets/forest/clearing.png"], [], fps=1) # players starting position
    
    # #### ITEMS ####
    rusty_flask = Item("rusty flask")
    def rusty_flask_interact(self, inp, current_room, events, inventory):
        if self in inventory:
            events.append({"type": game.EventType.OUTPUT, "value": "There is a bit of water left in the flask, it smells faintly of urine."})
        else:
            inventory.append(self)
            current_room.interactables.remove(self)
            events.append({"type": game.EventType.OUTPUT, "value": "You picked up the flask and drank from it. You feel slightly sick but hydrated."})
        return current_room
    rusty_flask.interact = rusty_flask_interact



    # #### ROOMS ####    
    forest_path_0 = Room("A dirt trail in the forest, next to where you woke up.", "down the forest trail.", ["Assets/forest/dirtpath.png"], [rusty_flask]) # starting branching off point
    def on_forest_path_0_enter(self, inp, events, inventory):
        if rusty_flask not in inventory:
            events.append({"type": game.EventType.OUTPUT, "value": "you are very dehyrdated and cannot venture further without water... look around for a drink."}) #starting restriction
        else:
            events.append({"type": game.EventType.OUTPUT, "value": self.description})
    forest_path_0.on_enter = on_forest_path_0_enter

    forest_path_1 = Room("A dirt trail in the forest, you see a crossing to the north and a cliff to the west.", "down the forest trail near a water source, you can see it curve round.", ["Assets/forest/cliffpath.png"], []) # monodirectional example, cliff to the left, crossroads 1 to the north

    forest_path_2 = Room("Forest enterance outside the town gates of coolsville.", "the path ahead looks well used.", ["Assets/forest/gatepath.png"], []) # starting branching off point

    forest_path_3 = Room("A dirt trail in the forest, you see it curve round.", "the forest trail curves round, you can't see very far ahead.", ["Assets/forest/curvedpath.png"], []) # starting branching off point

    # #### CONNECTIONS ####
    start_room.set_connection(game.Cardinal.NORTH, forest_path_0)

    forest_path_0.set_connection(game.Cardinal.WEST, forest_path_1, key = rusty_flask) # requires
    forest_path_0.set_connection(game.Cardinal.NORTH, forest_path_2, key = rusty_flask) # requires flask
    forest_path_0.set_connection(game.Cardinal.EAST, forest_path_3, key = rusty_flask) # to leave

    return start_room