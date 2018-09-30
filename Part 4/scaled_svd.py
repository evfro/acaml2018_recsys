import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import norm as spnorm
from polara import SVDModel


def scale_matrix(matrix, scaling, axis, implicit=False):
    '''Function to scale either rows or columns of the sparse rating matrix'''
    if scaling == 1: # no scaling (standard SVD case)
        return matrix
    
    if implicit:
        norms = np.sqrt(matrix.getnnz(axis=axis)) # compute Euclidean norm as if values are binary
    else:
        norms = spnorm(matrix, axis=axis, ord=2) # compute Euclidean norm

    scaling_matrix = diags(np.power(norms, scaling-1, where=norms!=0))
    
    if axis == 0: # scale columns
        return matrix.dot(scaling_matrix)
    if axis == 1: # scale rows
        return scaling_matrix.dot(matrix)


class ScaledSVD(SVDModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_scaling = 1
        self.col_scaling = 1
        self.method = 'ScaledSVD'

    def get_training_matrix(self, *args, **kwargs):
        svd_matrix = super().get_training_matrix(*args, **kwargs)
        svd_matrix = scale_matrix(svd_matrix, self.row_scaling, 1)
        svd_matrix = scale_matrix(svd_matrix, self.col_scaling, 0)
        return svd_matrix