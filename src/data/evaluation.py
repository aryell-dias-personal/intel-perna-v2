import numpy as np
from abc import ABC
from abc import abstractmethod

class EvaluationDefinition(ABC):
    def __init__(self):
        self.__loader = None

    def total_distance(self, solution, startEndtime):
        startTime, endTime = startEndtime
        time_error = 1
        distance = 0
        current_time = startTime
        current_state_index = solution[0]
        for state_index in solution[1:]:
            current_state = self.__loader.decodePlace(self.__loader.encodedNames[current_state_index])
            state = self.__loader.decodePlace(self.__loader.encodedNames[state_index])
            distance = distance + self.__loader.getDistance(current_state, state)
            current_time = current_time + self.__loader.getTimeCost(current_state, state)
            desired_time = self.__loader.desiredTime[state_index]
            if(desired_time > current_time): 
                current_time = desired_time
            if(desired_time >= 0):
                time_error = time_error + np.abs(current_time - desired_time)
            current_state_index = state_index
        return distance, time_error, len(solution)

    def __call__(self, loader, solutions, startEndtimes):
        self.__loader = loader
        size = len(solutions)
        distances = np.zeros(size)
        time_erros = np.zeros(size)
        numberOfPoints = np.zeros(size)

        for i in range(size):
            distances[i], time_erros[i], numberOfPoints[i] = self.total_distance(solutions[i], startEndtimes[i])

        notVisitedRate = (loader.dimension + size)/numberOfPoints.sum()
        return self.evaluate(distances, time_erros, notVisitedRate)

    @abstractmethod
    def evaluate(self, distances, time_erros, notVisitedRate):
        pass


class Evaluation(object):
    @staticmethod
    def sumEvaluation():
        class SumEvaluation(EvaluationDefinition):
            def evaluate(self, distances, time_erros, notVisitedRate):
                return distances.sum(), time_erros.sum(), notVisitedRate

        return SumEvaluation()
