""" Generic conversion utilities used by the Hue Node Server. """


def id_2_addr(hue_id):
    """ Convert a Phillips Hue ID to ISY Address """
    return hue_id.replace(':', '').replace('-', '')[-14:]


# Taken from: http://www.cse.unr.edu/~quiroz/inc/colortransforms.py
# License: Code is given as is. Use at your own risk and discretion.
# pylint: disable=invalid-name
def RGB_2_xy(R, G, B):
    """ Convert from RGB color to XY color. """
    if R + G + B == 0:
        return 0, 0

    var_R = (R / 255.)
    var_G = (G / 255.)
    var_B = (B / 255.)

    if var_R > 0.04045:
        var_R = ((var_R + 0.055) / 1.055) ** 2.4
    else:
        var_R /= 12.92

    if var_G > 0.04045:
        var_G = ((var_G + 0.055) / 1.055) ** 2.4
    else:
        var_G /= 12.92

    if var_B > 0.04045:
        var_B = ((var_B + 0.055) / 1.055) ** 2.4
    else:
        var_B /= 12.92

    var_R *= 100
    var_G *= 100
    var_B *= 100

    # Observer. = 2 deg, Illuminant = D65
    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

    # Convert XYZ to xy, see CIE 1931 color space on wikipedia
    return X / (X + Y + Z), Y / (X + Y + Z)


colors = {
    'white': (255, 255, 255), 'beige': (245, 245, 220), 'tan': (210, 180, 140),
    'gray': (128, 128, 128), 'navy blue': (0, 0, 128),
    'royal blue': (8, 76, 158), 'blue': (0, 0, 255), 'azure': (0, 127, 255),
    'aqua': (127, 255, 212), 'teal': (0, 128, 128), 'green': (0, 255, 0),
    'forest green': (34, 139, 34), 'olive': (128, 128, 0),
    'chartreuse': (127, 255, 0), 'lime': (191, 255, 0),
    'golden': (255, 215, 0), 'red': (255, 0, 0), 'coral': (0, 63, 72),
    'hot pink': (252, 15, 192), 'fuchsia': (255, 119, 255),
    'lavender': (181, 126, 220), 'indigo': (75, 0, 130), 'maroon': (128, 0, 0),
    'crimson': (220, 20, 60)}
""" Common color names and their RGB values. """

color_names = colors.keys()
color_names.sort()


def color_xy(cname):
    """ Lookup a color and return the XY values for that color. """
    return RGB_2_xy(*colors[cname])
