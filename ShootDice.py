from random import randint


class ShootDice:
    def __init__(self):
        self.randomSeries = list()
        self.finalPoints = list()
        self.finalPoints.append(1)

    def __set_final_points(self, points):
        self.finalPoints = []
        self.finalPoints.append(points[0])
        if points[1] != 0:
            self.finalPoints.append(points[1])

    def __get_random_series(self):
        self.randomSeries = []
        for j in range(200):
            self.randomSeries.append(randint(0, 5))

    def set_dice(self, points):
        if points[2] is False:
            self.__set_final_points(points)
            self.__get_random_series()
