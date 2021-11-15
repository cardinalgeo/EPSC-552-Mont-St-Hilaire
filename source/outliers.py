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
        od = OutlierDetector(buffer_samples=27) # max buffer size allowed
        outlier_bool = [None] * data.shape[0]
        for i, sample in enumerate(data[element]): 
            outlier_bool[i] = od.is_outlier(sample)

        if True in outlier_bool: 
            outliers = data[outlier_bool]
            for row in outliers.iterrows(): 
                outlier_record = {}   
                outlier_record["Sample ID"] = row[1]["sample_id"]
                outlier_record["Session"] = row[1]["date"].strftime("%Y-%m-%d")
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
                    (data["date"]      == datetime.strptime(outlier["Session"], "%Y-%m-%d"))
                    ].index, \
                inplace=True)

    for outlier in outliers["sample_session_element"]: 
        data.loc[
                (data["sample_id"] == outlier["Sample ID"]) & \
                (data["date"]      == datetime.strptime(outlier["Session"], "%Y-%m-%d")), \
                outlier["Element"]
                ] = np.NaN
    
    return data