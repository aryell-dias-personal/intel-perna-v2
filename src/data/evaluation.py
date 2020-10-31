import numpy as np
from abc import ABC
from abc import abstractmethod

# TODO: pensar sobre:
# 1. [ ] como lidar com usuários que não podem ser atendidos? queremos minimizar o numero de usuários não atendidos, 
# apesar de ser possível, uma vez que a formiga pode optar por um caminho no qual o fim de seu expediente ocorre antes
# do embarque
# 2. [ ] a formiga deve poder optar por não atender um pedido quando conveniente
# 3. [ ] a formiga deve poder optar por esperar a hora de um pedido
# 4. [ ] a formiga não deve poder fazer mais pedidos após a hora do fim de seu expediente
class EvaluationDefinition(ABC):
    def __init__(self):
        self.__loader = None

    def total_distance(self, solution, startEndtime):
        startTime, endTime = startEndtime
        time_error = 0
        distance = 0
        current_time = startTime
        current_state = solution[0]
        for state in solution[1:]:
            distance = distance + self.__loader.distanceMatrix[current_state, state]
            current_time = current_time + self.__loader.timeMatrix[current_state, state]
            desired_time = self.__loader.desiredTime[state]
            if(desired_time >= 0):
                time_error = time_error + np.abs(current_time - desired_time)
            current_state = state
        return distance, time_error

    def __call__(self, loader, solutions, startEndtimes):
        self.__loader = loader
        size = len(solutions)
        distances = np.zeros(size)
        time_erros = np.zeros(size)

        for i in range(size):
            distances[i], time_erros[i] = self.total_distance(solutions[i], startEndtimes[i])

        return self.evaluate(distances, time_erros)

    @abstractmethod
    def evaluate(self, distances, time_erros):
        pass


class Evaluation(object):
    @staticmethod
    def sumEvaluation():
        class SumEvaluation(EvaluationDefinition):
            def evaluate(self, distances, time_erros):
                return distances.sum(), time_erros.sum()

        return SumEvaluation()
