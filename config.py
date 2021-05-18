_RES = "small"

if _RES == "large":
    WIDTH = 900
    HEIGHT = 900
    FONT_SIZE = 18
if _RES == "medium":
    WIDTH = 750
    HEIGHT = 750
    FONT_SIZE = 18
if _RES == "small":
    WIDTH = 600
    HEIGHT = 600
    FONT_SIZE = 18



# COLOURS
_SCHEME = "monokai"
if _SCHEME == "monokai":
    COLOUR_BG = (29, 31, 33)
    COLOUR_INPUT_BUFFER = (201, 174, 130)
    COLOUR_INPUT_LOG = (229, 181, 103)
    COLOUR_OUTPUT_LOG = (232, 125, 62)

elif _SCHEME == "light":
    COLOUR_BG = (255, 255, 255)
    COLOUR_INPUT_BUFFER = (0, 0, 0)
    COLOUR_INPUT_LOG = (0, 0, 0)
    COLOUR_OUTPUT_LOG = (0, 0, 0)

elif _SCHEME == "matrix":
    COLOUR_BG = (0, 17, 0)
    COLOUR_INPUT_BUFFER = (0, 187, 0)
    COLOUR_OUTPUT_LOG = (0, 255, 0)
    COLOUR_INPUT_LOG = (0, 119, 0)
