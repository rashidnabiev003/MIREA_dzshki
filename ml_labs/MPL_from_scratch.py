import numpy as np
import sys


class MLP(object):
    def __init__(self,
                 n_hidden=10,
                 alpha=0,
                 beta=0,
                 epoch=100,
                 eta=0.01,
                 shuffle=False,
                 minibatch_size=1,
                 seed=None,
                 activation='sigmoid'):

        self.n_hidden = n_hidden
        self.alpha = alpha
        self.beta = beta
        self.epoch = epoch
        self.eta = eta
        self.shuffle = shuffle
        self.minibatch_size = minibatch_size
        self.random = np.random.RandomState(seed)
        self.activation = activation

    def _onehot(self, y, n_classes):
        onehot = np.zeros((n_classes, y.shape[0]))
        for idx, val in enumerate(y.astype(int)):
            onehot[val, idx] = 1.
        return onehot

    @staticmethod
    def _sigmoid(z):
        return 1. / (1. + np.exp(-np.clip(z, -250, 250)))

    @staticmethod
    def _ReLU(self, z):
        return max(0, z)

    def _forward(self, X):
        z_h = np.dot(X, self.w_h) + self.b_h
        a_h = self._sigmoid(z_h)
        z_out = np.dot(a_h, self.w_out) + self.b_out
        a_out = self._sigmoid(z_out)
        return z_h, a_h, z_out, a_out

    def _compute_cost(self, y_enc, output):
        # regularization
        l2_term = (self.alpha * (np.sum(self.w_h ** 2) + np.sum(self.w_out ** 2)))
        l1_term = np.abs(self.beta * (np.sum(self.w_h) + np.sum(self.w_out)))
        # cross-entropy loss
        cost = -np.sum(y_enc * np.log(output) + (1 - y_enc) * np.log(1 - output)) + l2_term + l1_term
        return cost

    def predict(self, X):
        z_h, a_h, z_out, a_out = self._forward(X)
        y_pred = np.argmax(z_out, axis=1)
        return y_pred

    def fit(self, X_train, y_train, X_valid, y_valid):
        n_output = np.unique(y_train).shape[0]
        n_features = X_train.shape[1]

