import numpy as np
import concurrent.futures
from src.helpers.constants import MATRIX_FIELDS, AGENT_FIELDS, ENCODED_NAMES, ANT_CNFG, ASKED_POINT_FIELDS

class AntTeam(object):

    def __init__(self, alpha=1, beta=5, evaporationRate=0.5, Q=100, initialPheromone=0.1):
        self.Q = Q
        self.beta = beta
        self.evaporationRate = evaporationRate
        self.alpha = alpha
        self.iteration = 0
        self.numLabels = None
        self.localNames = None
        self.askedPoints = None
        self.maxNodeNumber = 100
        self.adjacencyMatrix = None
        self.pheromonesDistrib = None
        self.bestSolution = None, None
        self.bestSolutionRecord = None
        self.initialPheromone = initialPheromone

    def initialize(self, localNames, adjacencyMatrix, askedPoints, agent):
        self.garage = 0
        self.localNames = localNames
        self.askedPoints = askedPoints
        self.numLabels = len(localNames)
        self.bestSolution = None, np.inf
        self.adjacencyMatrix = adjacencyMatrix
        self.endTime = agent[AGENT_FIELDS.ASKED_END_AT]
        self.startTime = agent[AGENT_FIELDS.ASKED_START_AT]
        self.bestSolutionRecord = [self.bestSolution[1]]
        self.places = agent[AGENT_FIELDS.NUMBER_OF_PLACES]
        self.extractEncodedNames(agent[AGENT_FIELDS.GARAGE])
        self.extractOrigensAndDestines()
        self.initPheromone()

    def extractEncodedNames(self, garageName):
        self.encodedNames = [garageName] + np.unique([[
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

    def initPheromone(self):
        self.pheromonesDistrib = np.zeros(2*[len(self.localNames)]+[3])
        for i in range(self.numLabels):
            for j in range(self.numLabels):
                self.pheromonesDistrib[i, j] = [
                    self.initialPheromone, *self.adjacencyMatrix[i][j]
                ]

    def decodeInd(self, encodedPos):
        originalName = self.encodedNames[encodedPos].split(ENCODED_NAMES.SEPARETOR)[0]
        return self.localNames.index(originalName)

    def getTimeCost(self, currentLocal, routeLen, currentTime, timeSpent):
        desiredTime = self.getDesiredTime(currentLocal, routeLen)
        actualTime = currentTime+timeSpent
        timeCost = actualTime - desiredTime
        return np.abs(timeCost)

    def getAvailablePlacesNumber(self, route):
        shipped = len(set(route).intersection(set(self.origens)))
        landed = len(set(self.destinations).intersection(set(route)))
        return self.places + landed - shipped

    def getLocalProbabilities(self, currentLocal, possibleChoices, currentTime, currentRoute):
        localFactors = []
        for i in possibleChoices:
            pheromone, distance, timeSpent = self.pheromonesDistrib[self.decodeInd(currentLocal), self.decodeInd(i)]
            timeCost = self.getTimeCost(currentLocal, len(currentRoute), currentTime, timeSpent)
            # timeDesiredProximity = np.exp(0)
            timeDesiredProximity = np.exp(-timeCost)
            remainingDest = self.countRemaining(currentRoute+[i])
            remainingDestFactor = np.exp(-(remainingDest/len(self.destinations)))
            futurePlaces = self.getAvailablePlacesNumber(currentRoute+[i])
            attractivity = (distance != 0 and futurePlaces >= 0) and (1/distance)*timeDesiredProximity*remainingDestFactor
            localFactors.append(
                (pheromone**self.alpha) * (attractivity**self.beta)
            )
        localFactors = np.array(localFactors) + 0.001
        return localFactors/localFactors.sum()

    def countRemaining(self, route):
        notClosed = set()
        for local in route:
            if local in self.origens:
                indexes = np.array(self.origens) == local
                notClosed = notClosed.union(set(np.array(self.destinations)[indexes]))
            if local in notClosed:
                notClosed.remove(local)
        return len(set(self.origens) - set(route)) + len(notClosed)

    def getRouteCost(self, route):
        routeCost = 0
        time = 0
        timeCostFactor = 1
        for i in range(len(route)-1):
            currentLocal = route[i]
            nextLocal = route[(i+1) % len(route)]
            timeCost = self.getTimeCost(currentLocal, i, self.startTime, time)
            timeCostFactor += timeCost/ANT_CNFG.TIME_THRESHOLD if timeCost > ANT_CNFG.TIME_THRESHOLD else 0
            _ , distance, timeSpent = self.pheromonesDistrib[self.decodeInd(currentLocal), self.decodeInd(nextLocal)]
            time += timeSpent
            routeCost += distance
        places = self.getAvailablePlacesNumber(route)
        if self.countRemaining(route) != 0 or places < 0:
            return np.inf
        return routeCost*timeCostFactor

    def getPossibleChoices(self, currentRoute):
        possibleChoices = list(self.origens)
        for local in currentRoute:
            if local in possibleChoices:
                if local in self.origens:
                    possibleChoices = possibleChoices + [
                        self.destinations[i] for i in range(len(self.origens)) 
                        if self.decodeInd(self.origens[i]) == self.decodeInd(local)
                    ]
        possibleChoices  = list(set(possibleChoices) - set(currentRoute))
        return np.unique(possibleChoices).tolist()

    def getCurrentTime(self, currentRoute):
        time = 0
        for i in range(len(currentRoute)-1):
            currentLocal = currentRoute[i]
            nextLocal = currentRoute[(i+1) % len(currentRoute)]
            _,_, timeSpent = self.pheromonesDistrib[self.decodeInd(currentLocal), self.decodeInd(nextLocal)]
            time += timeSpent
        return self.startTime + time

    def getTimeList(self, currentRoute):
        time = self.startTime
        timeList = [time]
        for i in range(len(currentRoute)-1):
            currentLocal = currentRoute[i]
            nextLocal = currentRoute[(i+1) % len(currentRoute)]
            _,_, timeSpent = self.pheromonesDistrib[self.decodeInd(currentLocal), self.decodeInd(nextLocal)]
            time += timeSpent
            timeList.append(time)
        return timeList

    def getDesiredTime(self, currentLocal, routeLen):
        if(currentLocal == 0):
            return self.endTime if routeLen>1 else self.startTime
        for askedPoint in self.askedPoints:
            encDestIndex = self.encodedNames.index(askedPoint[ASKED_POINT_FIELDS.DESTINY])
            encOrigIndex = self.encodedNames.index(askedPoint[ASKED_POINT_FIELDS.ORIGIN])
            if currentLocal == encDestIndex:
                return askedPoint[ASKED_POINT_FIELDS.ASKED_END_AT]
            elif currentLocal == encOrigIndex:
                return askedPoint[ASKED_POINT_FIELDS.ASKED_START_AT]

    def chooseNextLocal(self, currentRoute):
        currentLocal = currentRoute[-1]
        currentTime = self.getCurrentTime(currentRoute)
        possibleChoices = self.getPossibleChoices(currentRoute)
        prob = self.getLocalProbabilities(currentLocal, possibleChoices, currentTime, currentRoute)
        if(prob.__len__()):
            return np.random.choice(possibleChoices, p=prob)

    def updateBestRoute(self, routes, routeCosts):
        bestRoute = np.argmin(routeCosts)
        if routeCosts[bestRoute] < self.bestSolution[1]:
            self.bestSolution = routes[bestRoute], routeCosts[bestRoute]
        self.bestSolutionRecord.append(self.bestSolution[1])

    def calculateDeltaPheromone(self, routes, routeCosts):
        deltaPheromone = np.zeros(2*[self.numLabels])
        for route, cost in zip(routes, routeCosts):
            for i in range(len(route)):
                vertex1, vertex2 = self.decodeInd(route[i]), self.decodeInd(route[(i+1) % len(route)])
                index = (vertex1, vertex2)
                deltaPheromone[index] += self.Q/cost
        return deltaPheromone
        
    def updatePheromone(self, deltaPheromone):
        for i in range(self.numLabels):
            for j in range(self.numLabels):
                pheromone = self.pheromonesDistrib[i, j][0]
                self.pheromonesDistrib[i, j][0] = (
                    1-self.evaporationRate)*pheromone + deltaPheromone[i, j]

    def buildRoute(self, route):
        while self.countRemaining(route) >0 and len(route) < self.maxNodeNumber:
            nextLocal = self.chooseNextLocal(route)
            if(nextLocal is None):
                break
            route.append(nextLocal)
        route.append(self.garage)
        return route

    def mountRoutes(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            routes = list(executor.map(self.buildRoute, [[self.garage] for _ in range(self.maxNodeNumber)]))
            routeCosts = list(executor.map(self.getRouteCost, [route for route in routes]))
        return routes, routeCosts

    def run(self, numInt=100):
        for i in range(numInt):
            # print(f"--------- ANT_ITERATION {i} --------- ")
            routes, routeCosts = self.mountRoutes()
            self.updateBestRoute(routes, routeCosts)
            deltaPheromone = self.calculateDeltaPheromone(routes, routeCosts)
            self.updatePheromone(deltaPheromone)