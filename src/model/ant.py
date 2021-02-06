import uuid
import numpy as np
from src.helpers.constants import AGENT_FIELDS 

class Ant(object):
    def __init__(self, agent):
        self.__start_time = agent[AGENT_FIELDS.ASKED_START_AT]
        self.__end_time = agent[AGENT_FIELDS.ASKED_END_AT]
        self.__garage = agent[AGENT_FIELDS.GARAGE]
        self.__current_state = agent[AGENT_FIELDS.GARAGE]
        self.__current_time = self.__start_time
        self.__track_times = [self.__current_time]
        self.__max_avaiable_places = agent[AGENT_FIELDS.NUMBER_OF_PLACES]
        self.__avaiable_places = self.__max_avaiable_places
        self.__solution = [self.__current_state]
        self.__id = str(uuid.uuid4())

    def reset(self):
        self.__current_state = self.__garage
        self.__solution = [self.__current_state]
        self.__avaiable_places = self.__max_avaiable_places
        self.__current_time = self.__start_time
        self.__track_times = [self.__current_time]
        return self.current_state

    def move_to(self, state, loader):
        self.__current_time = loader.getCurrentTime(self.__current_time, self.__current_state, state)
        self.__track_times.append(self.__current_time)
        self.__current_state = state
        self.__avaiable_places += loader.deltaPlaces(state)
        self.__solution.append(state)

    @property
    def id(self):
        return self.__id
    
    @property
    def track_times(self):
        return self.__track_times

    @property
    def startEndTime(self):
        return self.__start_time, self.__end_time
    
    @property
    def solution(self):
        return self.__solution.copy()

    @property
    def current_state(self):
        return self.__current_state

    def find_neighborhood(self, loader, taboo):
        visited = list(map(loader.encodedNameIndex, self.__solution))
        hasntEnded =  self.__current_time < self.__end_time
        hasAvaiablePlaces = self.__avaiable_places > 0
        shoudntblockOrigens = hasntEnded and hasAvaiablePlaces
        includedOrigens = loader.getIncludedOrigens(self.current_state, self.__current_time, self.__end_time, shoudntblockOrigens)
        return loader.getRemainingNodes(visited, taboo, includedOrigens)

    def state_transition_rule(self, loader, taboo, q0, alpha, beta):
        neighborhood = self.find_neighborhood(loader, taboo)
        if(neighborhood):
            function = self.__exploit if np.random.uniform(0, 1) <= q0 else self.__explore            
            return function(loader, neighborhood, alpha, beta)

    def __get_targets(self, loader, neighborhood, alpha, beta):
        current_state_index = loader.encodedNameIndex(self.current_state)
        time_cost_list = np.array([])
        distance_list = np.array([])
        possible_trails = np.array([])
        for neighbor in neighborhood:
            trail = loader.getTrail(current_state_index, neighbor)
            possible_trails = np.append(possible_trails, trail)
            decoded_next_state = loader.decodePlace(loader.encodedNames[neighbor])
            decoded_current_state = loader.decodePlace(self.current_state)
            time_spent = loader.getTimeCost(decoded_next_state, decoded_current_state)
            time_cost_list = np.append(time_cost_list, time_spent)
            distance = loader.getDistance(decoded_next_state, decoded_current_state) or 1e-14
            distance_list = np.append(distance_list, distance)
        possible_trails = np.array(possible_trails)
        time_shift = np.abs(loader.desiredTime[neighborhood] - (time_cost_list + self.__current_time)) + 1e-14
        attractiveness = [distance_list, time_shift][np.random.choice(2)] ** -1.0

        return (possible_trails ** alpha) * (attractiveness ** beta)

    def __exploit(self, loader, neighborhood, alpha, beta):
        targets = self.__get_targets(loader, neighborhood, alpha, beta)
        return loader.encodedNames[neighborhood[targets.argmax()]]

    def __explore(self, loader, neighborhood, alpha, beta):
        targets = self.__get_targets(loader, neighborhood, alpha, beta)

        probabilities = targets / targets.sum()
        return loader.encodedNames[np.random.choice(neighborhood, p=probabilities)]

    def __eq__(self, other):
        return self.id == other.id
