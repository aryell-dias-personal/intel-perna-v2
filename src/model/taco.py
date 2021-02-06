import sys
import numpy as np
from joblib import Parallel, delayed
from src.model.team import AntTeam

class TeamAntColonyOptimization(object):
    def __init__(self, agents, evaluation, n_teams=150, rho=0.5, q0=0.5, alpha=1, beta=5):
        self.__q0 = q0
        self.__rho = rho
        self.__beta = beta
        self.__alpha = alpha
        self.__best_solution = []
        self.__best_solution_track_times = []
        self.__best_evaluation = sys.maxsize, sys.maxsize, sys.maxsize
        self.__teams = [ AntTeam(agents, evaluation) for _ in range(n_teams) ]

    def optimize(self, loader, stop_criterion):
        track = []
        n = loader.dimension + 1

        while not stop_criterion(self.__best_evaluation):
            self.__build_solutions(loader)
            self.__update_best_solution()

            loader.localPheromoneUpdate(self.__rho, self.__teams)
            loader.globalPheromoneUpdate(self.__rho, self.__best_solution, self.__best_evaluation) 
            track.append(self.__best_evaluation)

        return self.__best_solution, self.__best_evaluation, self.__best_solution_track_times, track

    def __build_solutions(self, loader):
        def function(team):
            team.build_solution(loader, self.__q0, self.__alpha, self.__beta)
        Parallel(n_jobs=1, require='sharedmem')(
            delayed(function)(team)
            for team in self.__teams
        )

    def __update_best_solution(self):
        for team in self.__teams:
            distanceEvaluation, timeEvaluation, notVisitedRate = team.evaluation
            bestDistanceEvaluation, bestTimeEvaluation, bestNotVisitedRate = self.__best_evaluation
            if timeEvaluation < bestTimeEvaluation or \
                (timeEvaluation == bestTimeEvaluation and \
                    ((notVisitedRate < bestNotVisitedRate) or \
                        (notVisitedRate == bestNotVisitedRate and \
                            distanceEvaluation < bestDistanceEvaluation))):
                self.__best_evaluation = team.evaluation
                self.__best_solution_track_times = team.solution_track_times
                self.__best_solution = team.solution

