# Copyright 2013 Cloudera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import struct

import numpy as np
from sklearn.base import BaseEstimator

import impala.blob
import impala.util


# TO CREATE A NEW ESTIMATOR:
#
# 1. Subclass ImpalaEstimator
#
# 2. Override _uda_name() to return the name of the registered UDA for this
# estimator
#
# 3. Override _parameter_list() to return a string that is a comma-separated
# list of the expected parameter values to add to the end of the UDA call.  No
# parameters means you should return an empty string ''.
#
# 4. Override _decode_coef() to set self.coef_ using the binary data returned
# from the estimator.

class ImpalaEstimator(BaseEstimator):
    
    def __init__(self):
        pass
    
    def _iterate_estimator(self, cursor, model_store, prev_key, next_key,
                          data_query, label_column):
        if not isinstance(prev_key, basestring):
            raise ValueError("prev_key must be string type")
        if not isinstance(next_key, basestring):
            raise ValueError("prev_key must be string type")
        if not model_store.has_key(prev_key):
            raise ValueError("prev_key (%s) not found in the model store" % prev_key)
        if model_store.has_key(next_key):
            raise ValueError("next_key (%s) already in the model store" % next_key)
        
        # these are only defined in subclasses
        uda_name = self._uda_name()
        parameter_list = self._parameter_list()
        if len(parameter_list) > 0:
            parameter_list = ', ' + parameter_list
        
        data_view = impala.util.create_view_from_query(cursor, data_query, safe=True)
        data_schema = impala.util.compute_result_schema(cursor, "SELECT * FROM %s" % data_view)
        columns = [tup[0] for tup in data_schema]
        if label_column not in columns:
            raise ValueError("%s is not a column in the provided data_query" % label_column)
        data_columns = [c for c in columns if c != label_column]
        model_value = """
                %(uda_name)s(%(model)s, %(observation)s, %(label_column)s%(parameter_list)s)
                """ % {'uda_name': uda_name,
                       'model': '%s.value' % model_store.name,
                       'observation': 'toarray(%s)' % ', '.join(['%s.%s' % (data_view, col) for col in data_columns]),
                       'label_column': label_column,
                       'parameter_list': parameter_list}
        derived_from_clause = model_store.distribute_value_to_table(prev_key, data_view)
        model_store.put(next_key, model_value, derived_from_clause)   # actual query execution here
        impala.util.drop_view(cursor, data_view)
        self.coef_ = self._decode_coef(model_store[next_key])
    
    def partial_fit(self, cursor, model_store, data_query, label_column, epoch):
        prev_epoch = epoch - 1
        self._iterate_estimator(cursor, model_store, str(prev_epoch),
                str(epoch), data_query, label_column)
    
    def fit(self, cursor, data_query, label_column):
        """Fit model.
        
        Parameters
        ----------
        
        model_store is BlobStore that contains model data.  The key
        `str(epoch - 1)` must exist.
        
        data_query is a SQL query string that produces rows that go into the
        regression.  It will be converted into a VIEW, just for this fn call.
        All columns go into the regression except for the `label_column`.
        
        label_column is the string name of the column that contains the labels.
        """
        model_store = impala.blob.BlobStore(cursor)
        model_store.send_null('0')
        for i in xrange(self.n_iter):
            epoch = i + 1
            self.partial_fit(cursor, model_store, data_query, label_column, epoch)


class LogisticRegression(ImpalaEstimator):
    
    def __init__(self, step_size=0.1, mu=0.1, n_iter=5):
        self.step_size = step_size
        self.mu = mu
        self.n_iter = n_iter
        self.coef_ = None
    
    def _uda_name(self):
        return 'logr'
    
    def _parameter_list(self):
        return ', '.join([str(self.step_size), str(self.mu)])
    
    def _decode_coef(self, coef_string):
        num_values = len(coef_string) / struct.calcsize("d")
        values = struct.unpack("%id" % num_values, coef_string)
        return np.asarray(list(values))
        

class SVM(ImpalaEstimator):
    
    def __init__(self, step_size=0.1, mu=0.1, n_iter=5):
        self.step_size = step_size
        self.mu = mu
        self.n_iter = n_iter
        self.coef_ = None
    
    def _uda_name(self):
        return 'svm'
    
    def _parameter_list(self):
        return ', '.join([str(self.step_size), str(self.mu)])
    
    def _decode_coef(self, coef_string):
        num_values = len(coef_string) / struct.calcsize("d")
        values = struct.unpack("%id" % num_values, coef_string)
        return np.asarray(list(values))
    











