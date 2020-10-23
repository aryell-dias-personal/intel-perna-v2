import sys
from src.model.ant import Ant
import numpy as np

class AntTeam(object):
    def __init__(self, agents, evaluation):
        self.__taboo = []
        self.__solution = []
        self.__loader = None
        self.__initial_states = []
        self.__evaluation = sys.maxsize
        self.__evaluation_criterion = evaluation
        self.__ants = [ Ant(agent) for agent in agents ]

    @property
    def evaluation(self):
        return self.__evaluation

    @property
    def solution(self):
        return self.__solution.copy()

    def __distance_of(self, solution):
        distance = 0
        if(solution):
            current_state = solution[0]
            for state in solution[1:]:
                current_state_index = self.__loader.encodedNameIndex(current_state)
                state_index = self.__loader.encodedNameIndex(state)
                distance = distance + self.__loader.distanceMatrix[current_state_index, state_index]
                current_state = state
        return distance

    def __find_init(self, ant):
        return self.__initial_states[self.__ants.index(ant)]

    def __go_back(self, initial_states):
        for idx, state in enumerate(initial_states):
            self.__ants[idx].move_to(state, self.__loader)

    def __update_taboo(self):
        for ant in self.__ants:
            self.__taboo += ant.solution
        self.__taboo = list(set(self.__taboo))
        self.__remain = set(self.__loader.encodedNames) - set(self.__taboo)

    def __move_ant(self, ant, transition_params):
        next_state = ant.state_transition_rule(*transition_params)
        ant.move_to(next_state, self.__loader)

    def __evaluate(self, ant): 
        if(len(ant.find_neighborhood(self.__loader, self.__taboo))):
            return self.__distance_of(ant.solution + [ant.solution[0]])
        else:
            return sys.maxsize

    def __choose_next_ant(self):
        return min(self.__ants, key=self.__evaluate)

    def build_solution(self, loader, q0, alpha, beta, trails):
        self.__taboo = []
        self.__solution = []
        self.__loader = loader
        self.__initial_states = list(map(lambda x: x.reset(), self.__ants))
        self.__update_taboo()

        while len(self.__taboo) < len(loader):
            transition_params = [loader, self.__taboo, q0, alpha, beta, trails]
            ant = self.__choose_next_ant()
            self.__move_ant(ant, transition_params)
            self.__update_taboo()

        self.__go_back(self.__initial_states)
        self.__solution = list(map(
            lambda x: list(map(
                loader.encodedNameIndex, x.solution
            )
        ), self.__ants))
        self.__evaluation = self.__evaluation_criterion(loader, self.__solution)
