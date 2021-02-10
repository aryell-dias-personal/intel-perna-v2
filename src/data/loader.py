import numpy as np
import sys
import osmnx as ox
from functools import lru_cache
from src.helpers.constants import MATRIX_FIELDS, ASKED_POINT_FIELDS, AGENT_FIELDS, ENCODED_NAMES

ox.config(use_cache=False, log_console=True)

class Loader(object):
    def __init__(self, matrix, agents):
        self.__edges = []
        self.__trails = []
        self.__default_trail = 1
        self.__graph = ox.graph_from_place(matrix[MATRIX_FIELDS.REGION], network_type='drive')
        self.__graph = ox.add_edge_speeds(self.__graph)
        self.__graph = ox.add_edge_travel_times(self.__graph)
        self.__matrix = matrix
        self.__agents = agents
        self.extractEncodedNames()
        self.extractOrigensAndDestines()
        self.mountDesiredTimes()

    def __len__(self):
        return self.dimension

    def askedPointFromRoute(self, encodedNameIndexList):
        visitedAskedpoint = []
        askedPointIdx = None 
        for idx in encodedNameIndexList:
            if idx in self.origens:
                askedPointIdx = self.origens.index(idx)
                visitedAskedpoint.append(self.askedPoints[askedPointIdx])
        return visitedAskedpoint
    
    def decodePlace(self, place):
        return place.split(ENCODED_NAMES.SEPARETOR)[0]

    def deltaPlaces(self, encodedName):
        return -1 if self.encodedNameIndex(encodedName) in self.origens else 1

    def mountDesiredTimes(self):
        self.__desiredTime = np.zeros([self.dimension]) - 1
        for askedPoint in self.askedPoints:
            startIndex = self.encodedNameIndex(askedPoint[ASKED_POINT_FIELDS.ORIGIN])
            askedStartAt = askedPoint.get(ASKED_POINT_FIELDS.ASKED_START_AT)
            if(askedStartAt is not None): 
                self.__desiredTime[startIndex] = askedStartAt
            endIndex = self.encodedNameIndex(askedPoint[ASKED_POINT_FIELDS.DESTINY])
            askedEndAt = askedPoint.get(ASKED_POINT_FIELDS.ASKED_END_AT)
            if(askedEndAt is not None): 
                self.__desiredTime[endIndex] = askedEndAt

    @lru_cache(maxsize=None)
    def strToCoord(self, string):
        return ox.get_nearest_node(self.__graph, tuple(float(coord) for coord in self.decodePlace(string).split(',')))

    @lru_cache(maxsize=None)
    def getDistance(self, origenStr, destinationStr):
        origen = self.strToCoord(origenStr) 
        destination = self.strToCoord(destinationStr)
        route = ox.shortest_path(self.__graph, origen, destination, weight='travel_time')
        edge_lengths = ox.utils_graph.get_route_edge_attributes(self.__graph, route, 'length')
        return sum(edge_lengths)

    @lru_cache(maxsize=None)
    def getTimeCost(self, origenStr, destinationStr):
        origen = self.strToCoord(origenStr) 
        destination = self.strToCoord(destinationStr)
        route = ox.shortest_path(self.__graph, origen, destination, weight='travel_time')
        edge_times = ox.utils_graph.get_route_edge_attributes(self.__graph, route, 'travel_time')
        return sum(edge_times)

    def getIncludedOrigens(self, current_state, current_time, end_time, shoudntblockOrigens):
        if(shoudntblockOrigens):
            time_cost_list = np.array([])
            for origenIndex in self.origens:
                decoded_next_state = self.decodePlace(self.encodedNames[origenIndex])
                decoded_current_state = self.decodePlace(current_state)
                time_spent = self.getTimeCost(decoded_next_state, decoded_current_state)
                time_cost_list = np.append(time_cost_list, time_spent)
            future_time = time_cost_list + current_time 
            origens = np.array(self.origens)
            return set(origens[future_time < end_time])
        return set()

    def getRemainingNodes(self, visited, taboo, includedOrigens):
        tabooIndexes = list(map(self.encodedNameIndex, taboo))
        origensSet = set(self.origens)
        visitedSet = set(visited)
        visitedOrigens = list(origensSet.intersection(visitedSet))
        openDestinations = set([
            self.destinations[
                self.origens.index(origen)
            ] for origen in visitedOrigens
        ])
        possibleChoices = includedOrigens.union(openDestinations)
        blockedChoices = set(tabooIndexes).union(visitedSet)
        return list(possibleChoices - blockedChoices)

    def encodedNameIndex(self, encodedName):
        return self.encodedNames.index(encodedName)
        
    def extractEncodedNames(self):
        self.__encodedNames = np.unique([[agent[AGENT_FIELDS.GARAGE]]*2 for agent in self.__agents] + [[
            point[ASKED_POINT_FIELDS.ORIGIN],
            point[ASKED_POINT_FIELDS.DESTINY] 
        ] for point in self.askedPoints]).flatten().tolist()

    def extractOrigensAndDestines(self):
        if len(self.askedPoints) :
            self.origens, self.destinations = list(zip(*[
                (self.encodedNames.index(askedPoint[ASKED_POINT_FIELDS.ORIGIN]),
                    self.encodedNames.index(askedPoint[ASKED_POINT_FIELDS.DESTINY]))
                for askedPoint in self.askedPoints
            ]))
        else:
            self.origens, self.destinations = [], []

    def getCurrentTime(self, startTime, startEncodedName, endEncodedName):
        time = startTime
        startName = self.decodePlace(startEncodedName)
        endName = self.decodePlace(endEncodedName)
        timeSpent = self.getTimeCost(startName, endName)
        endIndex = self.encodedNameIndex(endEncodedName)
        desiredTime = self.desiredTime[endIndex]
        time += timeSpent
        return time if time > desiredTime else desiredTime

    def prepareTrails(self, edge, delta_matrix, step):
        if(list(edge) not in self.__edges):
            self.__edges.append(list(edge))
            self.__trails.append(self.__default_trail)
            delta_matrix = np.append(delta_matrix, step)
        else:
            edge_index = self.__edges.index(list(edge))
            delta_matrix[edge_index] += step

        return delta_matrix
    
    def updateTrails(self, rho, delta_matrix):
        self.__trails = (1 - rho)*np.array(self.__trails) + delta_matrix

        npEdges = np.array(self.__edges)
        condition = self.__trails > self.__default_trail
        self.__edges = npEdges[condition].tolist()
        self.__trails = self.__trails[condition].tolist()

    def getTrail(self, current, neighbor):
        current_edge = [current, neighbor]
        if(current_edge in self.__edges):
            edge_index = self.__edges.index(current_edge)
            return self.__trails[edge_index]
        else:
            return self.__default_trail

    def localPheromoneUpdate(self, rho, teams): 
        delta_matrix = np.zeros(len(self.__trails))

        for team in teams:
            step = 1.0 / np.random.choice(team.evaluation, p=[0.75, 0.25, 0])
            for solution in team.solution:
                src = solution[:-1]
                dest = solution[1:]
                solution_edges = list(zip(*[src, dest]))
                for edge in solution_edges:
                    delta_matrix = self.prepareTrails(edge, delta_matrix, step)
        
        self.updateTrails(rho, delta_matrix)

    def globalPheromoneUpdate(self, rho, best_solution, best_evaluation):
        delta_matrix = np.zeros_like(self.__trails)

        step = 1.0 / np.random.choice(best_evaluation,  p=[0, 0.25, 0.75])
        for solution in best_solution:
            src = solution[:-1]
            dest = solution[1:]
            solution_edges = list(zip(*[src, dest]))
            for edge in solution_edges:
                delta_matrix = self.prepareTrails(edge, delta_matrix, step)

        self.updateTrails(rho, delta_matrix)

    @property
    def encodedNames(self):
        return self.__encodedNames

    @property
    def dimension(self):
        return len(self.encodedNames)

    @property
    def askedPoints(self):
        return self.__matrix[MATRIX_FIELDS.ASKED_POINTS]

    @property
    def desiredTime(self):
        return self.__desiredTime