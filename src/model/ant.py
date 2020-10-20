import uuid
import numpy as np
from src.helpers.constants import AGENT_FIELDS 


class Ant(object):
    def __init__(self, agent):
        self.__current_state = agent[AGENT_FIELDS.GARAGE]
        self.__solution = [self.__current_state]
        self.__id = str(uuid.uuid4())

    def move_to(self, state):
        self.__current_state = state
        self.__solution.append(state)

    @property
    def id(self):
        return self.__id

    @property
    def solution(self):
        return self.__solution.copy()

    @property
    def current_state(self):
        return self.__current_state

    def find_neighborhood(self, loader, taboo):
        visited = list(map(loader.encodedNameIndex, self.__solution))
        return loader.getRemainingNodes(visited, taboo)

    def state_transition_rule(self, loader, taboo, q0, alpha, beta, trails):
        neighborhood = self.find_neighborhood(loader, taboo)
        if(neighborhood):
            if np.random.uniform(0, 1) <= q0:
                return self.__exploit(loader, neighborhood, alpha, beta, trails)
            return self.__explore(loader, neighborhood, alpha, beta, trails)

    def __get_targets(self, loader, neighborhood, alpha, beta, trails):
        current_state_index = loader.encodedNameIndex(self.current_state)
        possible_trails = trails[current_state_index, neighborhood]
        original_index = loader.encodedNameIndex(self.current_state)
        attractiveness = loader.encodedMatrix[original_index, neighborhood] ** -1.0

        return (possible_trails ** alpha) * (attractiveness ** beta)

    def __exploit(self, loader, neighborhood, alpha, beta, trails):
        targets = self.__get_targets(loader, neighborhood, alpha, beta, trails)
        return loader.encodedNames[neighborhood[targets.argmax()]]

    def __explore(self, loader, neighborhood, alpha, beta, trails):
        targets = self.__get_targets(loader, neighborhood, alpha, beta, trails)

        probabilities = targets / targets.sum()
        return loader.encodedNames[np.random.choice(neighborhood, p=probabilities)]

    def __eq__(self, other):
        return self.id == other.id
