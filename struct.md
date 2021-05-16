"""
text input
TA handling, depending on room, display these assets
output to log, terminal renders log

Interactables - characters wip, items wip, physical objects (doors, switch, etc) wip
rooms - half done, music done, textures wip
terminal - wip

room: #init all rooms, then connect
    rendering:
        pass
    characters:
        character.villager
    items:
        item.key

class GameHandler:
    _inventory
    _current_room
    _events = [
        {type: "input", "text": "hello!"},
        {type: "output", "text": "hey there!"}
    ]
    
    loop()
    render()
    get_current_room()
    serialize_state() #if imput in log, input before rendering
    parse_input("pick up key") #search interactables in room, if matches, perform interaction
    ...

class Interactable():
    _keywords = ["pick up %s", "take %s", "use %s"]
    on_interact()

class MusicPlayer():
    _current_path
    _currentRoompath:
            return
        _current.unload() #is this c?
        _current = pygame.mixer.music.load(filepath)
        _current.play()


class Room(): #upper element
    _textures = []

    _interactables = []
    on_enter():
        musicplayer.play(self.music)
    render()

class Terminal(): #user imput
    on_keyboard_down()
    render()


save file:im
"""