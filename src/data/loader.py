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

    def __len__(self):
        return self.dimension

    def decodePlace(self, place):
        return place.split(ENCODED_NAMES.SEPARETOR)[0]

    def mountEncodedMatrix(self):
        self.__encondedMatrix = np.zeros([self.dimension, self.dimension])
        for i in range(self.dimension):
            encodedNameI = self.encodedNames[i]
            originalI = self.getOriginalIndex(encodedNameI)
            for j in range(self.dimension):
                encodedNameJ = self.encodedNames[j]
                originalJ = self.getOriginalIndex(encodedNameJ)
                self.__encondedMatrix[i, j] = self.matrix[originalI, originalJ] or 1e-14

    def getOriginalIndex(self, encodedName):
        originalName = self.decodePlace(encodedName)
        return self.localNames.index(originalName)

    def getRemainingNodes(self, visited, taboo):
        tabooIndexes = list(map(self.encodedNameIndex, taboo))
        origensSet = set(self.origens)
        visitedOrigens = list(origensSet.intersection(set(visited)))
        openDestinations = set([
            self.destinations[
                self.origens.index(origen)
            ] for origen in visitedOrigens
        ])
        return list(origensSet.union(openDestinations) - set(tabooIndexes).union(set(visited)))

    def encodedNameIndex(self, encodedName):
        return self.encodedNames.index(encodedName)
        
    def extractEncodedNames(self):
        self.__encodedNames = np.unique([[agent[AGENT_FIELDS.GARAGE] for agent in self.__agents]] + [[
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
    def encodedMatrix(self):
        return np.array(self.__encondedMatrix)
    
    @property
    def matrix(self):
        return np.array(self.__matrix[MATRIX_FIELDS.ADJACENCY_MATRIX])

    @property
    def nodes(self):
        return list(range(0, self.dimension))