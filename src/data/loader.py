import numpy as np
from src.helpers.constants import MATRIX_FIELDS

class Loader(object):
    def __init__(self, matrix):
        self.__matrix = matrix

    def __len__(self):
        return self.dimension

    @property
    def dimension(self):
        return len(self.__matrix[MATRIX_FIELDS.LOCAL_NAMES])

    @property
    def matrix(self):
        return np.array(self.__matrix[MATRIX_FIELDS.ADJACENCY_MATRIX])

    @property
    def nodes(self):
        return list(range(0, self.dimension))