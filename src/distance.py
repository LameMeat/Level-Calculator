class Distance:
    def __init__(self, point1, point2, distance: float):
        self.point1 = point1
        self.point2 = point2
        try:
            self.distance = float(distance)
        except ValueError:
            raise ValueError("Distance must be a float")

    def __str__(self):
        return f"{self.point1}-{self.point2}: {self.distance}"