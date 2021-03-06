'''
Created on 11.07.2015

@author: Gabriel Krummenacher
@author: Matthew Rocklin
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import dask
from sklearn.svm import SVC
from sklearn import cross_validation
from dask.compose import daskify, value
from dask.async import get_sync

D = daskify

def train_test(reg_param, train_idx, test_idx, X, y):
    svm = SVC(C=reg_param)
    svm.fit(X[train_idx, :], y[train_idx])
    return svm.score(X[test_idx, :], y[test_idx])

d = 10
n = 100
y = np.sign(np.random.randn(n))
X = np.random.randn(n, d)
reg_params = np.logspace(-2, 2, 5)
n_folds = 4

kf_test = cross_validation.KFold(n, n_folds=n_folds)
score_params = list()
test_scores = []
for model_sel_idx, test_idx in kf_test:
    X_train = X[model_sel_idx]
    y_train = y[model_sel_idx]

    for reg_param in reg_params:
        kf = cross_validation.KFold(len(model_sel_idx), n_folds=n_folds)
        scores = [D(train_test)(reg_param, train_idx, val_idx, X_train, y_train)
                  for train_idx, val_idx in kf]
        score = D(sum)(scores) / n_folds
        score_params.append([score, reg_param])

    best_param = D(max)(score_params)[1]

    test_scores += [D(train_test)(best_param, model_sel_idx, test_idx, X, y)]

test_score = D(sum)(test_scores) / n_folds

print test_score.compute()
