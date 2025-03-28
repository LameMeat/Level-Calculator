from .distance import Distance

class Point:
    def __init__(self, label, height: float):
        self.label = label
        self.height = height
        self.distances = {}
        self.target_thickness = 'X'

    def add_reference(self, point, distance: float):
        if point not in self.distances:
            self.distances[point] = Distance(self.label, point, distance)

    def __str__(self):
        return f"{self.label}: {self.height}"