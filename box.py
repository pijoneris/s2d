import uuid


class KeyPoints:
    ext_px = 40
    def __init__(self, start, end, type):
        self.start = start
        self.end = end
        self.type = type

    def get_ext_start(self):
        if type == 'low_height':
            return (self.start[0] - self.ext_px, self.start[1]), (self.end[0] + self.ext_px, self.end[1])
        elif type == 'low_width':
            return (self.start[0], self.start[1] - self.ext_px), (self.end[0], self.end[1] + self.ext_px)

        return self.start, self.end
class BoundingBox:
    def __init__(self, image, coordinates, label, score):
        width, height = image.size
        ymin, xmin, ymax, xmax = coordinates[0:4]

        self.id = uuid.uuid4()
        self.ymin = ymin * height
        self.ymax = ymax * height
        self.xmin = xmin * width
        self.xmax = xmax * width
        self.coordinates = [
            (xmin * width, ymin * height),
            (xmin * width, ymax * height),
            (xmax * width, ymin * height),
            (xmax * width, ymax * height),
            ((xmax * width + xmin * width) / 2, (ymax * height + ymin * height) / 2)
        ]

        self.label = label
        self.score = score
        self.used = False
        self.text = None
        self.key_points = None
