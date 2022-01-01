import json 
from outlier_detector.detectors import OutlierDetector # Dixon's Q Test for small-sample outlier detection
from datetime import datetime
import numpy as np 

def save_outliers(outliers_list): 
    path = '../data/interim/outliers.json'
    with open(path) as json_file:
        outliers = json.load(json_file)
    
    if list(outliers_list[0].keys()) == ['Sample ID', 'Session', 'Element']: 
        outliers["sample_session_element"] += outliers_list
    elif list(outliers_list[0].keys()) == ['Sample ID', 'Session']: 
        outliers["sample_session"] += outliers_list
    elif list(outliers_list[0].keys()) == ['Sample ID']: 
        outliers["sample"] += outliers_list

    for key in outliers.keys(): 
        outliers[key] = list({frozenset(item.items()) : item for item in outliers[key]}.values())

    with open(path, 'w') as json_file:
        json.dump(outliers, json_file, indent=4)
    
    return outliers

def get_outliers(): 
    path = '../data/interim/outliers.json'
    with open(path) as json_file:
        outliers = json.load(json_file)
    
    return outliers

def detect_outliers_Dixons_Q(elements, data): 
    outlier_records = []

    for element in elements: 
        outlier_indexes = dixon_test(data[element])[2]

        if outlier_indexes: 
            outliers = data.iloc[outlier_indexes]
            for row in outliers.iterrows(): 
                outlier_record = {}   
                outlier_record["Sample ID"] = row[1]["sample_id"]
                outlier_record["Session"] = row[1]["date"]
                outlier_record["Element"] = element

                outlier_records.append(outlier_record)

    return outlier_records

def remove_outliers(outliers, data): 
    for outlier in outliers["sample"]: 
        data.drop(
                data[
                    data["sample_id"] == outlier["Sample ID"]
                    ].index, \
                inplace=True)

    for outlier in outliers["sample_session"]: 
        data.drop(
                data[
                    (data["sample_id"] == outlier["Sample ID"]) & \
                    (data["date"]      == outlier["Session"])
                    ].index, \
                inplace=True)

    for outlier in outliers["sample_session_element"]: 
        data.loc[
                (data["sample_id"] == outlier["Sample ID"]) & \
                (data["date"]      == outlier["Session"]), \
                outlier["Element"]
                ] = np.NaN
    
    return data

def dixon_test(data, left=True, right=True, confidence_level=95):
    """
    Keyword arguments:
        data = A ordered or unordered list of data points (int or float).
        left = Q-test of minimum value in the ordered list if True.
        right = Q-test of maximum value in the ordered list if True.
        q_dict = 
            
    Returns a list of 2 values for the outliers, or None.
    E.g.,
       for [1,1,1] -> [None, None]
       for [5,1,1] -> [None, 5]
       for [5,1,5] -> [1, None]
    """
    assert(left or right), 'At least one of the variables, `left` or `right`, must be True.'
    assert(len(data) >= 3), 'At least 3 data points are required'
    assert(confidence_level in [90, 95, 99]), 'Confidence level has critical values tabulated'

    """
    Create dictionary of Q-values for a given confidence level, where the dict. keys are sample sizes N and 
    the associated values are the corresponding critical Q values. E.g.,{3: 0.97, 4: 0.829, 5: 0.71, 6: 0.625, ...}
    """
    
    q90 = [0.941, 0.765, 0.642, 0.56, 0.507, 0.468, 0.437, 
           0.412, 0.392, 0.376, 0.361, 0.349, 0.338, 0.329, 
           0.32, 0.313, 0.306, 0.3, 0.295, 0.29, 0.285, 0.281, 
           0.277, 0.273, 0.269, 0.266, 0.263, 0.26
           ]

    q95 = [0.97, 0.829, 0.71, 0.625, 0.568, 0.526, 0.493, 0.466, 
           0.444, 0.426, 0.41, 0.396, 0.384, 0.374, 0.365, 0.356, 
           0.349, 0.342, 0.337, 0.331, 0.326, 0.321, 0.317, 0.312, 
           0.308, 0.305, 0.301, 0.29
           ]

    q99 = [0.994, 0.926, 0.821, 0.74, 0.68, 0.634, 0.598, 0.568, 
           0.542, 0.522, 0.503, 0.488, 0.475, 0.463, 0.452, 0.442, 
           0.433, 0.425, 0.418, 0.411, 0.404, 0.399, 0.393, 0.388, 
           0.384, 0.38, 0.376, 0.372
           ]

    Q90 = {n:q for n,q in zip(range(3,len(q90)+3), q90)}
    Q95 = {n:q for n,q in zip(range(3,len(q95)+3), q95)}
    Q99 = {n:q for n,q in zip(range(3,len(q99)+3), q99)}

    if confidence_level==90: 
        q_dict = Q90
    elif confidence_level==95:
        q_dict = Q95
    elif confidence_level==99:
        qdict = Q99
    
    n_of_nan = sum([1 for value in data if np.isnan(value)])
    data = [np.inf if np.isnan(value) else value for value in data]
    sdata = sorted(data)
    sort_index = [index for index, value in sorted(enumerate(data), key=lambda x: x[1])]
    if n_of_nan != 0:
        sort_index = sort_index[:-n_of_nan]

    Q_mindiff, Q_maxdiff = (0,0), (0,0)
    
    if left:
        Q_min = (sdata[1] - sdata[0]) 
        try:
            Q_min /= (sdata[-1] - sdata[0])
        except ZeroDivisionError:
            pass
        Q_mindiff = (Q_min - q_dict[len(data)], sort_index[0])
        
    if right:
        Q_max = abs((sdata[-2] - sdata[-1]))
        try:
            Q_max /= abs((sdata[0] - sdata[-1]))
        except ZeroDivisionError:
            pass
        Q_maxdiff = (Q_max - q_dict[len(data)], sort_index[-1])

    if not Q_mindiff[0] > 0 and not Q_maxdiff[0] > 0:
        outlier_indexes = [None, None]
    
    elif Q_mindiff[0] == Q_maxdiff[0]: 
        outlier_indexes = [Q_mindiff[1], Q_maxdiff[1]]
        
    elif Q_mindiff[0] > Q_maxdiff[0]:
        outlier_indexes = [Q_mindiff[1], None]
    
    else:
        outlier_indexes = [None, Q_maxdiff[1]]

    outlier_indexes = list(filter(None, outlier_indexes))
    
    outliers = []
    for index in outlier_indexes:
        outlier = data.pop(index)
        outliers.append(outlier)
    
    return data, outliers, outlier_indexes