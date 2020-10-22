import numpy as np
from abc import ABC
from abc import abstractmethod

# TODO: como garantir horario do pedido ajuste no evaluation
# 1. [ ] adicionar custos temporais no input
# 2. [ ] tratar ajuste no input na matriz de distâncias
# 3. [ ] criar matriz de tempo
# 4. [ ] criar um objeto de tempos desejados por encodedName
# 5. [ ] criar uma lista "track_times" na formiga e/ou "current_time"
# 6. [ ] definir que acima de um certo treshold de deslocamento no tempo a distáncia fica sys.maxsize
# 7. [ ] definir que se o current_time for acima do fim do expediente do a gente a distáncia fica sys.maxsize
class EvaluationDefinition(ABC):
    def __init__(self):
        self.__loader = None

    def total_distance(self, solution):
        distance = 0
        current_state = solution[0]
        for state in solution[1:]:
            distance = distance + self.__loader.encodedMatrix[current_state, state]
            current_state = state
        return distance

    def __call__(self, loader, solutions):
        self.__loader = loader
        size = len(solutions)
        distances = np.zeros(size)

        for i in range(size):
            distances[i] = self.total_distance(solutions[i])

        return self.evaluate(distances)

    @abstractmethod
    def evaluate(self, distances):
        pass


class Evaluation(object):
    @staticmethod
    def squared_sum():
        class SquaredSumEvaluation(EvaluationDefinition):
            def evaluate(self, distances):
                return (distances ** 2).sum()

        return SquaredSumEvaluation()

    @staticmethod
    def minmax():
        class MinMaxEvaluation(EvaluationDefinition):
            def evaluate(self, distances):
                return distances.max()

        return MinMaxEvaluation()
