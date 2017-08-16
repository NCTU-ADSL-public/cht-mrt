#! -*- coding:utf-8 -*-
import csv
from file_path_name import *
import argparse
from datetime import datetime


def preprocess_mrt_station():
    mrt_station_csv_name = './data/mrt_station_entrance_new.csv'
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
    return mrt_station_data


def generate_route():
    route_file = open(mrt_route_name, 'r')
    content = route_file.readlines()
    data_list = list()
    for record in content:
        record = record.decode('big5').encode('utf-8').replace('\r\n', '')
        record = record.split(',')
        data_list.append(record)
    route_list = list()
    temp_dict = dict()
    for i,data in enumerate(data_list):
        if i%3 == 0:
            temp = data[0].split('-')
            temp_dict['outset'] = temp[0]
            temp_dict['destination'] = temp[1]
        elif i%3 == 1:
            for j,station in enumerate(data):
                if not station:
                    temp_dict['up_direction']= data[:j]
                    break
            else:
                temp_dict['up_direction'] = data

        elif i%3 == 2:
            for j,station in enumerate(data):
                if not station:
                    temp_dict['down_direction']= data[:j]
                    break
            else:
                temp_dict['down_direction'] = data
            route_list.append(temp_dict)
            temp_dict = dict()
    return route_list

def get_mrt_data(name):
    mrt_name = source_data_path + name
    mrt_file = open(mrt_name, 'r')
    content = mrt_file.readlines()
    data_list = list()
    for record in content:
        record = record.decode('big5').encode('utf-8').replace('\r\n', '')
        record = record.split(',')
        data_list.append(record)
    return data_list


def get_top_k_outset(data_list, k=None):
    # print('top ' + str(k) + ' hot outset:')
    result_dict = dict()
    for data in data_list:
        if result_dict.has_key(data[3]):
            result_dict[data[3]] += 1
        else:
            result_dict[data[3]] = 1

    new_key_list = sorted(result_dict, key=result_dict.__getitem__, reverse=True)
    new_value_list = sorted(result_dict.values(), reverse=True)
    # for i in range(0, len(new_key_list)):
    #     print(str(new_key_list[i])+' '+str(new_value_list[i]))
    return (new_key_list[:k], new_value_list[:k])


def get_top_k_destination(data_list, k=None):
    # print('top ' + str(k) + ' hot destination:')
    result_dict = dict()
    for data in data_list:
        if result_dict.has_key(data[4]):
            result_dict[data[4]] += 1
        else:
            result_dict[data[4]] = 1

    new_key_list = sorted(result_dict, key=result_dict.__getitem__, reverse=True)
    new_value_list = sorted(result_dict.values(), reverse=True)
    # for i in range(0, len(new_key_list)):
    #     print(str(new_key_list[i])+' '+str(new_value_list[i]))
    return (new_key_list[:k], new_value_list[:k])


def match_od(data_list, out, des):
    result = list()
    for i,data in enumerate(data_list):
        if (data[3] == out) and (data[4] == des):
            result.append(i)
    return result

def match_route(route_list, out, des):
    for i,route in enumerate(route_list):
        o = -1
        d = -1
        for station in route['up_direction']:
            if station == out:
                o = out
            if station == des:
                d = des
            if (o!=-1) and (d!=-1):
                return i
    else:
        return -1

def match_station():
    pass

def group_data_by_hour(data_list):
    data_list_by_hour = list()
    for i in range(18):
        data_list_by_hour.append(list())
    for record in data_list:
        temp_date = datetime.fromtimestamp(float(record[1]))
        try:
            data_list_by_hour[temp_date.hour-6].append(record)
        except:
            continue
    return data_list_by_hour


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mrt_file_name", type=str, help='(mrt_yyyymmdd.csv)', default=mrt_file_name)
    args = parser.parse_args()

    route_list = generate_route()
    route_num = dict()
    for i in range(len(route_list)):
        route_num[str(i)] = 0

    mrt_file_name = args.mrt_file_name
    data_list = get_mrt_data(mrt_file_name)
    data_list_by_hour = group_data_by_hour(data_list)

    for day, data_list in enumerate(data_list_by_hour):
        out_list, out_v_list = get_top_k_outset(data_list)
        des_list, des_v_list = get_top_k_destination(data_list)
        result_dict = dict()
        for out in out_list:
            for des in des_list:
                result_dict[out+'-'+des] = len(match_od(data_list, out, des))


        new_key_list = sorted(result_dict, key=result_dict.__getitem__, reverse=True)
        new_value_list = sorted(result_dict.values(), reverse=True)
        # print('path')
        # for i in range(len(new_key_list)):
        #     print(str(new_key_list[i])+' '+str(new_value_list[i]))

        # path
        path_output_file = open('mrt_analysis/path_' + mrt_file_name.split('.')[0] + '_' + str(day+6) + '_output.csv', 'w')
        csv_writer = csv.writer(path_output_file, delimiter=',')
        for i in range(len(new_key_list)):
            csv_writer.writerow([new_key_list[i], new_value_list[i]])

        out_output_file = open('mrt_analysis/out_' + mrt_file_name.split('.')[0] + '_' + str(day+6) + '_output.csv', 'w')
        csv_writer = csv.writer(out_output_file, delimiter=',')
        for i in range(len(out_list)):
            csv_writer.writerow([out_list[i], out_v_list[i]])

        des_output_file = open('mrt_analysis/des_' + mrt_file_name.split('.')[0] + '_' + str(day+6) + '_output.csv', 'w')
        csv_writer = csv.writer(des_output_file, delimiter=',')
        for i in range(len(des_list)):
            csv_writer.writerow([des_list[i], des_v_list[i]])

