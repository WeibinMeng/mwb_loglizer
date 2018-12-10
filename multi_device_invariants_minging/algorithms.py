#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2018-10-22 13:32
# * Last modified : 2018-12-10 12:51
# * Filename      : algorithms.py
# * Description   :
'''
  Changed from Shilin He (github: https://github.com/logpai/loglizer)
'''
# **********************************************************
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import numpy as np
from itertools import combinations
import evaluation as ev
import math


class LogAnomalyDetectionAlgorithm(object):
    def __init__(self, name):
        self.name = name

    def fit(event_count_matrix, params):
        pass

    def predict(event_count_matrix, params):
        pass

    def predict_for_analyze(event_count_matrix, params, start_time_ms):
        pass

    def __str__(self):
        return self.name


class MiningInvariants(LogAnomalyDetectionAlgorithm):
    def __init__(self):
        super(MiningInvariants, self).__init__('Mining Invariants')

    def fit(self, event_count_matrix, params):
        self.invar_list = self.invariant_search(event_count_matrix, params)

    def predict(self, event_count_matrix, params):
        valid_col_list = []
        valid_invar_list = []
        for cols, scalars, confidence in self.invar_list:
            valid_col_list.append(list(cols))
            valid_invar_list.append(list(scalars))
        prediction = []
        for rowid, row in enumerate(event_count_matrix):
            label = 0
            disobey = 0
            for i, cols in enumerate(valid_col_list):
                sum_of_invar = 0
                for j, c in enumerate(cols):
                    sum_of_invar += valid_invar_list[i][j] * row[c]
                if abs(sum_of_invar) > 1e-7:
                    #print("row {} break invariant of {} {}".format(rowid, valid_col_list[i], valid_invar_list[i]))
                    print("row {} break invariant of {} {}".format(rowid, valid_col_list[i], valid_invar_list[i]))
                    label = 1
                    disobey += 1
            print("row {} disobey {} rules".format(rowid, disobey))
            prediction.append(label)
        print ('len(prediction)',len(prediction))
        return prediction

    def predict_for_analyze(self, event_count_matrix, params, start_time_ms):
        valid_col_list = []
        valid_invar_list = []
        for cols, scalars, confidence in self.invar_list:
            valid_col_list.append(list(cols))
            valid_invar_list.append(list(scalars))
        prediction = []
        anomalies = []
        for rowid, row in enumerate(event_count_matrix):
            label = 0
            violations = []
            for i, cols in enumerate(valid_col_list):
                sum_of_invar = 0
                col_value = []
                for j, c in enumerate(cols):
                    sum_of_invar += valid_invar_list[i][j] * row[c]
                    col_value.append(row[c])
                if abs(sum_of_invar) > 1e-7:
                    label = 1
                    violations.append({
                        'window_index': rowid,
                        'columns': tuple(cols),
                        'templates': (cols[0] + 1, cols[1] + 1),
                        'values': tuple(col_value),
                        'rules': tuple(valid_invar_list[i])
                    })
            prediction.append(label)
            if label == 1:
                print("row {} disobey {} rules: ".format(rowid, len(violations)))
                for v in violations:
                    print("row {} template {} value {} break invariant of {}".format(v['window_index'], v['templates'], v['values'], v['rules']))
                                    #print("row {} col {} value {} break invariant of {}".format(v['window_index'], v['columns'], v['values'], v['rules']))
                begin_ms = start_time_ms + rowid * params['step_size'] * 3600 * 1000
                end_ms = begin_ms + params['step_size'] * 3600 * 1000
                v0 = violations[0]
                anomalies.append({'range': [begin_ms, end_ms], 'message': 'Templates{} count{} violates rule{}'.format(v0['templates'], v0['values'], v0['rules'])})
        print ('len(prediction)',len(prediction))
        analyze_result = {
            'anomalies': anomalies,
            'algorithm': self.name
        }
        return prediction, analyze_result

    def compute_eigenvector(self, event_count_matrix):
        FLAG_contain_zero = False
        count_zero = 0
        dot_result = np.dot(event_count_matrix.T, event_count_matrix)
        u, s, v = np.linalg.svd(dot_result)
        min_vec = v[-1, :]
        for i in min_vec:
            if np.fabs(i) < 1e-6:
                count_zero += 1
        if count_zero != 0:
            # print("0 exits and discard the following vector: ")
            FLAG_contain_zero=True
        min_vec = min_vec.T
        return min_vec, FLAG_contain_zero

    def check_invar_validity(self, event_count_matrix, params, selected_columns, both_nonzero_map):
        sub_matrix = event_count_matrix[:, selected_columns]
        inst_num = event_count_matrix.shape[0]
        both_nonzero = np.sum(both_nonzero_map)
        validity = False
        # print ('selected matrix columns are', selected_columns)
        min_theta, FLAG_contain_zero = self.compute_eigenvector(sub_matrix)
        abs_min_theta = [np.fabs(it) for it in min_theta]
        if FLAG_contain_zero:
            return validity, []
        for i in params['scale_list']:
            min_index = np.argmin(abs_min_theta)
            scale = float(i) / min_theta[min_index]
            scaled_theta = np.array([round(item * scale) for item in min_theta])
            scaled_theta[min_index] = i
            scaled_theta = scaled_theta.T
            if 0 in np.fabs(scaled_theta):
                continue
            dot_submat_theta = np.dot(sub_matrix, scaled_theta)
            count_nonzero = 0
            for i, j in enumerate(dot_submat_theta):
                if (np.fabs(j) > 1e-8) and both_nonzero_map[i]:
                    count_nonzero += 1
            if count_nonzero <= (1 - params['threshold']) * both_nonzero:
                validity = True
                selected_templates = (selected_columns[0]+1,selected_columns[1]+1)
                #print('A valid invariant is found and the corresponding columns are ',scaled_theta, selected_columns)
                print('A valid invariant is found and the corresponding templates are ',scaled_theta, selected_templates)
                break
        return validity, scaled_theta

    def invariant_search(self, event_count_matrix, params):
        num_samples, num_features = event_count_matrix.shape
        invar_list = []
        valid_cols = []
        for col in range(num_features):
            if np.sum(event_count_matrix[:,col]) != 0:
                valid_cols.append(col)
        num_valid_cols = len(valid_cols)
        print('tot templates: {}  valid templates: {}'.format(num_features, num_valid_cols))

        nonzero_map = (event_count_matrix != 0)
        col_nonzero = np.sum(nonzero_map, axis=0)

        both_nonzero_min_support = 4
        both_nonzero_min_fraction = 0.5

        for i in range(num_valid_cols):
            for j in range(i + 1, num_valid_cols):
                c1, c2 = valid_cols[i], valid_cols[j]
                both_nonzero_map = nonzero_map[:,c1] & nonzero_map[:,c2]
                both_nonzero = np.sum(both_nonzero_map)
                either_nonzero = np.sum(nonzero_map[:,c1] | nonzero_map[:,c2])
                if both_nonzero < both_nonzero_min_support or (both_nonzero / either_nonzero) < both_nonzero_min_fraction:
                    continue
                validity, scaled_theta = self.check_invar_validity(event_count_matrix, params, [c1, c2], both_nonzero_map)
                if validity:
                    invar_list.append(((c1, c2), tuple(scaled_theta), both_nonzero / num_samples))
        invar_list.sort(key=lambda x : x[2], reverse=True)
        return invar_list


class PCA(LogAnomalyDetectionAlgorithm):
    def __init__(self):
        super(PCA, self).__init__('PCA')

    def fit(self, event_count_matrix, params):
        self.weighted_matrix = self.weighting(event_count_matrix, params)
        self.threshold, self.C = self.get_threshold(self.weighted_matrix, params)

    def predict(self, event_count_matrix, params):
        weighted_matrix = self.weighting(event_count_matrix, params)
        inst_size, event_num = weighted_matrix.shape
        pred = []
        for i in range(inst_size):
            label = 0
            ya = np.dot(self.C, weighted_matrix[i,:])
            SPE = np.dot(ya,ya)
            if SPE > self.threshold:
                label = 1
                print('row {} SPE {} > threshold {}'.format(i, SPE, self.threshold))
            pred.append(label)
        return pred

    def predict_for_analyze(self, event_count_matrix, params, start_time_ms):
        weighted_matrix = self.weighting(event_count_matrix, params)
        inst_size, event_num = weighted_matrix.shape
        pred = []
        anomalies = []
        for i in range(inst_size):
            label = 0
            ya = np.dot(self.C, weighted_matrix[i,:])
            SPE = np.dot(ya,ya)
            if SPE > self.threshold:
                label = 1
            pred.append(label)
            if label == 1:
                begin_ms = start_time_ms + i * params['step_size'] * 3600 * 1000
                end_ms = begin_ms + params['step_size'] * 3600 * 1000
                anomalies.append({'range': [begin_ms, end_ms], 'message': 'pca test info'})
                print('row {} SPE {} > threshold {}'.format(i, SPE, self.threshold))
        analyze_result = {
            'anomalies': anomalies,
            'algorithm': self.name
        }
        return pred, analyze_result

    def weighting(self, raw_matrix, params):
        window_num, tpl_type = raw_matrix.shape
        mat = raw_matrix.copy().astype(float)
        if params['tf-idf']:
            for t in range(tpl_type):
                df = np.count_nonzero(raw_matrix[:,t])
                mat[:,t] = raw_matrix[:,t] * math.log(window_num / df)
        mean = mat.mean(axis=0)
        mat -= mean
        return mat

    def get_threshold(self, weighted_matrix, params):
        c_alpha = params['calpha']
        U, sqrt_sigma, VT = np.linalg.svd(weighted_matrix, full_matrices=False)
        print(U.shape, VT.shape)
        window_num, tpl_type = self.weighted_matrix.shape
        sigma = sqrt_sigma**2 / window_num # ??? WHY ???
        n_pc = 4
        ev_sum = np.sum(sigma)
        partial_sum = 0
        for i in range(tpl_type):
            partial_sum += sigma[i]
            if partial_sum / ev_sum >= params['fraction']:
                n_pc = i + 1
                break
        print('principal components number is %d' % (n_pc))
        phi1, phi2, phi3 = np.sum(sigma[n_pc:]), np.sum(sigma[n_pc:]**2), np.sum(sigma[n_pc:]**3)
        h0 = 1 - (2 * phi1 * phi3) / (3 * phi2**2)
        threshold = phi1 * (1 + c_alpha * math.sqrt(2 * phi2 * h0**2) / phi1 + phi2 * h0 * (h0 - 1) / phi1**2)**(1 / h0)
        P = VT[:n_pc,:]
        C = np.identity(tpl_type) - np.dot(P.T, P)
        return threshold, C

