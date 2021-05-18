"""
next steps:
- terminal: class, write events to terminal (render them)
- terminal input -> register keydownevent, wait for return key to 'send' input to game handler
- room description: where am i?
"""

import pygame
from enum import Enum
from typing import List, Tuple
import pickle
import os
import sys
# import antigravity, for future revisions

from config import *
from storyline import *
# from storyline import Room, Interactable, Character, Item, get_initial_room
# hard coding res because dynamic sizing is for nerds

class Cardinal(Enum): # custom typing for directions
    NORTH = 0
    
    EAST = 1
    SOUTH = 2
    WEST = 3

class EventType(Enum):
    INPUT = 0
    OUTPUT = 1
    START_TIME = 2
    
def inpevent(text):
    return {"type": EventType.INPUT, "value": text}

def outevent(text):
    return {"type": EventType.OUTPUT, "value": text}
    
class Terminal:
    def __init__(self):
        self.events = []
        # just for testing
        #
        #for i in range(500):
        #    if i % 2 == 0:
        #        self.events.append({'type': EventType.INPUT, "value": str(i)})
        #    else:
        #        self.events.append({'type': EventType.OUTPUT, "value": str(i)})
        #    # self.events.extend(self.events)
        self.curr_input = ""
        self.offset = 0
    
    
    def render_text_lines(self, screen: pygame.Surface, font: pygame.font.Font, text: str, colour: Tuple[int, int, int], y_bottom: int) -> int:
        surfaces = [] # holds rendered text textures
        while text: # while text is not empty
            subtext = text # single line of text 
            subtext_surface = font.render(subtext, True, colour) # render line texture
            while subtext_surface.get_width() > WIDTH * 0.95: # truncating rendered lines to fit screen with padding of 5%
                if len(subtext) == 1:
                    raise Exception("Font size too large")
                # more pythonic approach to the above validation: assert len(subtext) > 1, "Font size too large, no character fits on screen"
                if " " in subtext:
                    char = None
                    while char != " " and len(subtext) > 0: # removing whole words: while the current character isnt a space, remove from subtext 
                        char = subtext[-1]
                        subtext = subtext[:-1]
                #subtext = subtext[:-1] # removes one char from line
                # if no space was found, remove a character
                else:
                    subtext = subtext[:-1]
                subtext_surface = font.render(subtext, True, colour) # re-renders texture to see if it fits
            text = text[len(subtext)+1:] # subtext is removed from remaining text
            surfaces.append(subtext_surface) # completed line added to array of textures to render
        for surface in surfaces[::-1]: # rendering the line textures bottom to top
            y_bottom -= surface.get_height() # get height of line of text
            screen.blit(surface,(0.025*WIDTH, y_bottom)) # render line of text
        return y_bottom

    def render(self, screen, font):
        """
        |               |
        |    UwU        |
        |---------------| if collison, last to render, draw room
        |  asd          |
        | aaasdads      |
        |>              |
        """
        y_bottom = self.render_text_lines(screen, font, "> " + self.curr_input, COLOUR_INPUT_BUFFER, HEIGHT-5)
        down_arrow = "▼"
        if self.offset != 0:
            # draw scroll indicator
            indicator = font.render(down_arrow, True, COLOUR_INPUT_BUFFER)
            screen.blit(indicator, (WIDTH-10-indicator.get_width(), y_bottom - indicator.get_height()))
        for event in self.events[-self.offset-1::-1]: # iterating backwards
            if y_bottom < HEIGHT//3 * 2: # text would be obstructed fully by room texture
                break
            if event["type"].value in [EventType.INPUT.value, EventType.OUTPUT.value]: # event type checking
                colour = COLOUR_INPUT_LOG if event["type"] == EventType.INPUT else COLOUR_OUTPUT_LOG # colour hard coding
                # text = "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum "
                y_bottom = self.render_text_lines(screen, font, event["value"], colour, y_bottom)

class GameHandler:
    def __init__(self):
        pygame.init() # init pygame window
        pygame.font.init() # initalize font renderer
        self.font = pygame.font.SysFont('Consolas', FONT_SIZE) # font family
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) # set screen size
        self.done = False # keeps window alive
        # self.current_room = Room(["600.jpg", "600 copy.jpg", "600 copy 2.jpg", "600 copy 3.jpg", "600 copy 4.jpg", "600 copy 5.jpg", "600 copy 6.jpg", "600 copy 7.jpg"], [])
        self.inventory = [] #init inv
        self.terminal = Terminal() # terminal handling
        self.current_room = get_initial_room(self.terminal.events) #init game
        self.clock = pygame.time.Clock() # fps bs
        pygame.display.set_caption("uwu") # title
        self.terminal.events.append({"type": EventType.START_TIME, "value": time.time()})

    def handle_input(self, input_text: str, filtered = False) -> List[dict]:
        self.terminal.events.append(inpevent(input_text))
        input_text = input_text.lower()
        if input_text.startswith("load ") and not filtered:
            # loading with pickle
            file_name = os.path.join("Saves", input_text[len("load "):] + ".rpg")
            self.terminal.events = pickle.load(open(file_name, "rb"))
            self.current_room = get_initial_room()
            for event in self.terminal.events:
                if event["type"] == EventType.INPUT:
                    self.handle_input(event["value"], filtered=True)

            self.terminal.events.append(outevent(f"Loaded from {file_name}"))
            # save file
            # load save file
        elif input_text.startswith("save ") and not filtered:
            file_name = os.path.join("Saves", input_text[len("save "):] + ".rpg")
            # writing with pickle
            with open(file_name, "wb") as f:
                f.write(pickle.dumps(self.terminal.events))
            self.terminal.events.append(outevent(f"Saved to {file_name}"))
            # save file
            
        elif input_text in ["look around", "observe", "look"]:
            # descriptions
            self.terminal.events.append(outevent(self.current_room.description))

            # doors
            doors = []
            for i, room in enumerate(self.current_room.connections):
                if room is not None:
                    doors.append(Cardinal(i).name.lower())
            if len(doors) > 0:
                self.terminal.events.append(outevent("There are paths to: " + ", ".join(doors)))
            # interactables
            if len(self.current_room.interactables) == 0:
                self.terminal.events.append(outevent("You see nothing"))
            else:
                items = []
                for item in self.current_room.interactables:
                    items.append(item.identifier)
                self.terminal.events.append(outevent("You see: " + ", ".join(items)))
        elif input_text.startswith("look ") or input_text.startswith("check ") or input_text.startswith("peek "):
            d = input_text.split(" ")[-1]
            if d not in ["north", "east", "south", "west"]:
                self.terminal.events.append(outevent("That's not a valid cardinal direction!"))
                return
            direction = Cardinal[d.upper()]
            try:
                self.terminal.events.append(outevent(self.current_room.connections[direction.value].peek_description))
            except AttributeError:
                print(self.current_room)

        elif input_text in ["bag", "inventory"]:
            # print player inventory
            items = []
            for item in self.inventory:
                items.append(item.identifier)
            self.terminal.events.append(outevent("You have: " + ", ".join(items)))
        elif input_text in ["go north", "go east", "go south", "go west"]:
            direction = Cardinal[input_text[len("go "):].upper()]

            # check if a door exists
            if self.current_room.connections[direction.value] is None:
                self.terminal.events.append(outevent("There's no path there.."))
                return
            
            # check if it's locked
            if self.current_room.keys[direction.value] is not None and self.current_room.keys[direction.value] not in self.inventory:
                self.terminal.events.append(outevent("You cannot access this path! Yet..."))
                return
            # change room
            self.current_room = self.current_room.connections[direction.value]
            self.terminal.events.append(outevent(f"You went {input_text[len('go '):]}"))
            self.current_room.on_enter(self.current_room, input_text, self.terminal.events, self.inventory)
        else:
            # go through interactables in this room and find which one to interact with
            # basics hardcoded, this where custom interactions can happen, as interactions are handled by the item, not the gamehandler
            found = False
            for interactable in self.current_room.interactables:
                if interactable.does_interact(input_text):
                    self.current_room = interactable.interact(interactable, input_text, self.current_room, self.terminal.events, self.inventory)
                    found = True
                    break
            if not found:
                for interactable in self.inventory:
                    if interactable.does_interact(input_text):
                        self.current_room = interactable.interact(interactable, input_text, self.current_room, self.terminal.events, self.inventory)
                        found = True
                        break
            if not found:
                self.terminal.events.append(outevent("Sorry, that doesn't make sense."))

    def loop(self): # loop to keep window alive
        while not self.done: # while window is kept alive
            for event in pygame.event.get(): # an event occured (mouseclick, button click, keyboard input, ...)
                    if event.type == pygame.QUIT: # quitting event
                            self.done = True # very
                            pygame.display.quit() # convoluted
                            sys.exit(0) # exit code
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            if len(self.terminal.curr_input)>0:
                                self.terminal.curr_input = self.terminal.curr_input[:-1]
                        elif event.key == pygame.K_RETURN: # process input
                            self.handle_input(self.terminal.curr_input)

                            self.terminal.curr_input = ""
                        else: # add input to buffer
                            self.terminal.curr_input += event.unicode
            # scrolling
            keys = pygame.key.get_pressed()    
            if keys[pygame.K_UP]: # scroll up
                self.terminal.offset += 1
            elif keys[pygame.K_DOWN]: # scroll down
                self.terminal.offset -= 1
                self.terminal.offset = max(self.terminal.offset, 0)

            self.screen.fill(COLOUR_BG) # background
            self.render() # render shit idk
            pygame.display.flip() # swap display buffers
            self.clock.tick(30)

    def render(self): # render all the things
        self.terminal.render(self.screen, self.font)
        self.current_room.render(self.screen)

if __name__ == "__main__": # main loop
    game = GameHandler() # game instance, arguments for window size
    game.loop() # run the loop
