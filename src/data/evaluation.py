import numpy as np
from abc import ABC
from abc import abstractmethod

# TODO: como garantir horario do pedido ajuste no evaluation
# 1. [X] adicionar custos temporais no input
# 2. [X] tratar ajuste no input na matriz de distâncias
# 3. [X] criar matriz de tempo
# 4. [X] criar um objeto de tempos desejados por encodedName
# 5. [X] criar uma lista "track_times" na formiga e/ou "current_time"

# 6. [ ] definir que o deslocamento no tempo a distáncia afeta a distância num fator de e^((distancia/1000)^2)
# 7. [ ] definir que se o current_time for acima do fim do expediente do agente não é possível ter embarques
# 8. [ ] o while deve rodar ate que nenhuma das ants tenha neighborhood
# 9. [ ] evaluation para valorizar a concretização de todos os askedPoints

class EvaluationDefinition(ABC):
    def __init__(self):
        self.__loader = None

    def total_distance(self, solution):
        time_error = 0
        distance = 0
        current_time = 0
        current_state = solution[0]
        for state in solution[1:]:
            distance = distance + self.__loader.distanceMatrix[current_state, state]
            current_time = current_time + self.__loader.timeMatrix[current_state, state]
            time_error = time_error + np.abs(current_time - self.__loader.desiredTime[state])
            current_state = state
        return distance, time_error

    def __call__(self, loader, solutions):
        self.__loader = loader
        size = len(solutions)
        distances = np.zeros(size)
        time_erros = np.zeros(size)

        for i in range(size):
            distances[i], time_erros[i] = self.total_distance(solutions[i])

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
