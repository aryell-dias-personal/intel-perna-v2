import sys
from src.model.ant import Ant
import numpy as np

class AntTeam(object):
    def __init__(self, agents, evaluation):
        self.__taboo = []
        self.__solution = []
        self.__solution_track_times = []
        self.__loader = None
        self.__initial_states = []
        self.__evaluation = sys.maxsize
        self.__evaluation_criterion = evaluation
        self.__ants = [ Ant(agent) for agent in agents ]
        self.__startEndtimes = list(map(lambda x: x.startEndTime, self.__ants))

    @property
    def evaluation(self):
        return self.__evaluation

    @property
    def solution(self):
        return self.__solution.copy()
    
    @property
    def solution_track_times(self):
        return self.__solution_track_times

    @property
    def startEndtimes(self):
        return self.__startEndtimes

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

    def __evaluate_ant(self, ant):
        ant_solution = list(map(
            self.__loader.encodedNameIndex, ant.solution + [ant.solution[0]]
        ))
        return self.__evaluation_criterion(self.__loader, [ant_solution], [ant.startEndTime])

    def __evaluate(self, ant, option): 
        if(len(ant.find_neighborhood(self.__loader, self.__taboo))):
            ant_evaluation = self.__evaluate_ant(ant)
            if(option == 2): 
                return -ant_evaluation[option]
            return ant_evaluation[option]
        else:
            return sys.maxsize

    def __choose_next_ant(self):
        option = np.random.choice(3)
        def evaluate(ant):
            return self.__evaluate(ant, option)
        return min(self.__ants, key=evaluate)

    def __update_solution(self):
        for ant in self.__ants:
            self.__solution.append(list(map(
                self.__loader.encodedNameIndex, ant.solution
            )))
            self.__solution_track_times.append(ant.track_times)

    def build_solution(self, loader, q0, alpha, beta):
        self.__taboo = []
        self.__solution = []
        self.__solution_track_times = []
        self.__loader = loader
        self.__initial_states = list(map(lambda x: x.reset(), self.__ants))
        self.__update_taboo()

        while len(self.__taboo) < len(loader):
            transition_params = [loader, self.__taboo, q0, alpha, beta]
            ant = self.__choose_next_ant()
            next_state = ant.state_transition_rule(*transition_params)
            if(not next_state): break
            ant.move_to(next_state, self.__loader)
            self.__update_taboo()

        self.__go_back(self.__initial_states)
        self.__update_solution()
        self.__evaluation = self.__evaluation_criterion(loader, self.__solution, self.startEndtimes)
