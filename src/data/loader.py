import numpy as np
import sys
from src.helpers.constants import MATRIX_FIELDS, ASKED_POINT_FIELDS, AGENT_FIELDS, ENCODED_NAMES

class Loader(object):
    def __init__(self, matrix, agents):
        self.__matrix = matrix
        self.__agents = agents
        self.extractEncodedNames()
        self.extractOrigensAndDestines()
        self.mountEncodedMatrix()
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

    def mountEncodedMatrix(self):
        self.__distanceMatrix = np.zeros([self.dimension, self.dimension])
        self.__timeMatrix = np.zeros([self.dimension, self.dimension])
        for i in range(self.dimension):
            encodedNameI = self.encodedNames[i]
            originalI = self.getOriginalIndex(encodedNameI)
            for j in range(self.dimension):
                encodedNameJ = self.encodedNames[j]
                originalJ = self.getOriginalIndex(encodedNameJ)
                self.__distanceMatrix[i, j] = self.matrix[originalI, originalJ][0] or 1e-14
                self.__timeMatrix[i, j] = self.matrix[originalI, originalJ][1]


    def getOriginalIndex(self, encodedName):
        originalName = self.decodePlace(encodedName)
        return self.localNames.index(originalName)

    def getIncludedOrigens(self, current_state, current_time, end_time, shoudntblockOrigens):
        if(shoudntblockOrigens):
            current_index = self.encodedNameIndex(current_state)
            time_cost = self.timeMatrix[current_index, self.origens]
            future_time = time_cost + current_time 
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
        startIndex, endIndex = self.encodedNameIndex(startEncodedName), self.encodedNameIndex(endEncodedName)
        timeSpent = self.timeMatrix[startIndex, endIndex]
        desiredTime = self.desiredTime[endIndex]
        time += timeSpent
        return time if time > desiredTime else desiredTime

    @property
    def encodedNames(self):
        return self.__encodedNames

    @property
    def dimension(self):
        return len(self.encodedNames)

    @property
    def localNames(self):
        return self.__matrix[MATRIX_FIELDS.LOCAL_NAMES]

    @property
    def askedPoints(self):
        return self.__matrix[MATRIX_FIELDS.ASKED_POINTS]
    
    @property
    def distanceMatrix(self):
        return np.array(self.__distanceMatrix)
    
    @property
    def timeMatrix(self):
        return np.array(self.__timeMatrix)

    @property
    def desiredTime(self):
        return self.__desiredTime
    
    @property
    def matrix(self):
        return np.array(self.__matrix[MATRIX_FIELDS.ADJACENCY_MATRIX])

    @property
    def nodes(self):
        return list(range(0, self.dimension))