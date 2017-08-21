#! -*- coding:utf-8 -*-
import csv
from file_path_name import *
import argparse
from datetime import datetime


def preprocess_mrt_station():
    mrt_station_csv_name = '../data/mrt_station_entrance_new.csv'
    mrt_station_file = open(mrt_station_csv_name)
    raw_mrt_station_data = mrt_station_file.readlines()
    temp = str()
    mrt_station_data = list()
    for i in raw_mrt_station_data:
        temp_list = i.replace('\r\n', '').split(',')
        if temp_list[1]!= temp:
            temp_list[3] = float(temp_list[3])
            temp_list[4] = float(temp_list[4])
            mrt_station_data.append(temp_list)
            temp = temp_list[1]
        else:
            continue
    mrt_station_list = list()
    mrt_station_dict = dict()
    for i, record in enumerate(mrt_station_data):
        mrt_station_list.append(record[1])
        mrt_station_dict[record[1]] = i
    return (mrt_station_list, mrt_station_dict)
