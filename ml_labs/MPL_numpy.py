from typing import Dict, List, Any

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

        if self.activation == 'sigmoid':
            a_h = self._sigmoid(z_h)
        elif self.activation == 'relu':
            a_h = self._ReLU(z_h)

        z_out = np.dot(a_h, self.w_out) + self.b_out

        if self.activation == 'sigmoid':
            a_out = self._sigmoid(z_out)
        elif self.activation == 'relu':
            a_out = self._ReLU(z_out)

        return z_h, a_h, z_out, a_out

    def _compute_cost(self, y_enc, output):
        # regularization
        self.l2_term = (self.alpha * (np.sum(self.w_h ** 2) + np.sum(self.w_out ** 2)))
        self.l1_term = np.abs(self.beta * (np.sum(self.w_h) + np.sum(self.w_out)))
        # cross-entropy loss
        cost = -np.sum(y_enc * np.log(output) + (1 - y_enc) * np.log(1 - output)) + self.l2_term + self.l1_term
        return cost

    def predict(self, X):
        z_h, a_h, z_out, a_out = self._forward(X)
        y_pred = np.argmax(z_out, axis=1)
        return y_pred

    def fit(self, X_train, y_train, X_valid, y_valid):
        n_output = np.unique(y_train).shape[0]
        n_features = X_train.shape[1]
        self.reg = self.l1_term + self.l2_term

        #input weights
        self.b_h = np.zeros(self.n_hidden)
        self.w_h = self.random.normal(loc=0.0, scale=0.1, size=(n_features, self.n_hidden))

        #output weights
        self.b_out = np.zeros(n_output)
        self.w_out = np.random.normal(loc=0.0, scale=0.1, size=(self.n_hidden, n_output))

        #epoch plot
        epoch_len = len(str(self.epoch))
        self.eval = {'cost':[], 'train_acc':[], 'valid_acc':[]}
        y_train_enc = self._onehot(y_train, n_output)


        for i in range(self.epoch):
            indices = np.arange(X_train.shape[0])

            if self.shuffle:
                self.random.shuffle(indices)

            for start_index in range(0 - indices.shape[0] -\
                                   self.minibatch_size +\
                                   1, self.minibatch_size):
                batch_indx = indices[start_index:start_index +\
                             self.minibatch_size]

                z_h, a_h, z_out, a_out = self._forward(X_train[batch_indx])

                # back prop

                act_out = a_out - y_train_enc[batch_indx]
                act_derivative_h = a_h * (1 - a_h)

                act_h = np.dot(act_out, self.w_out.T) * act_derivative_h

                grad_w_h = np.dot(X_train[batch_indx].T, act_h)
                grad_b_h = np.sum(act_h, axis=0)

                grad_w_out = np.dot(a_h.T, act_out)
                grad_b_out = np.sum(act_out, axis=0)

                delta_w_h = np.sum(grad_w_h + self.reg * self.w_h)
                delta_b_h = grad_b_h
                self.w_h -= self.eta * delta_w_h
                self.b_h -= self.eta * delta_b_h

                delta_w_out = np.sum(grad_w_out + self.reg * self.w_out)
                delta_b_out = grad_b_out
                self.w_out -= self.eta * delta_w_out
                self.b_out -= self.eta * delta_b_out

            z_h, a_h, z_out, a_out = self._forward(X_train)

            cost = self._compute_cost(y_train_enc, a_out)
            y_train_pred = self.predict(X_train)
            y_valid_pred = self.predict(X_valid)
            train_acc = ((np.sum(y_train == y_train_pred)).astype(np.float) / X_train.shape[0])
            valid_acc = ((np.sum(y_valid == y_valid_pred)).astype(np.float) / X_valid.shape[0])

            #metric
            sys.stderr.write('\r%0*d/%d | Costs: %.2f''| Train accuracy/valid accuracy: %.2f%%/%.2f%%'
                            %
                            (epoch_len, i + 1, self.epoch,
                            cost,
                            train_acc*100, valid_acc*100))
            sys.stderr.flush()

            self.eval['cost'].append(cost)
            self.eval['train_acc'].append(train_acc)
            self.eval['valid_acc'].append(valid_acc)

        return self





