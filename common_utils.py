

# default dimensions for the pitch
PITCH_LENGTH = 105
PITCH_WIDTH = 68
# Note: pitch_x is the field length, pitch_y is the field width

def cartesian_distance(x1, y1, x2, y2):
    x1 *= PITCH_LENGTH
    x2 *= PITCH_LENGTH
    y1 *= PITCH_WIDTH
    y2 *= PITCH_WIDTH
    return ((x1-x2)**2 + (y1-y2)**2)**(0.5)