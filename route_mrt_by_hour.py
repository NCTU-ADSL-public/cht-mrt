#! -*- coding:utf-8 -*-
import csv
from file_path_name import *
import argparse
from datetime import datetime

from station_match import get_station_match

from preprocess_mrt_station import preprocess_mrt_station

def output_inter_path(mrt_file_name):
    mrt_user_csv_name = '../source/'+str(mrt_file_name)
    # mrt_station_list, mrt_station_dict = preprocess_mrt_station()
    mrt_station_list, mrt_station_dict, station_routeid_dict, route_name_match = get_station_match()
    mrt_path_file_name = mrt_file_name.split('_')
    mrt_path_file_name = mrt_path_file_name[0]+'_path_'+mrt_path_file_name[1]
    mrt_path_csv_name = '../source/'+mrt_path_file_name

    # mrt_out_put_csv_name = 'mrt_path.js'
    r_file = open(mrt_user_csv_name, 'r')
    data_list = r_file.readlines()
    path_r_file = open(mrt_path_csv_name, 'r')
    path_data_list = path_r_file.readlines()
    ans_list = list()
    temp = list()
    inter_station_list = list()
    trans_list = list()
    for i, record in enumerate(data_list):
        temp_record_list = record.decode('big5').encode('utf8').replace('\r\n', '').split(',')
        temp_path_record_list = path_data_list[i].decode('big5').encode('utf8').replace('\r\n', '').split(',')[3:-1]
        temp_record_list[1] = int(temp_record_list[1])
        temp_record_list[2] = int(temp_record_list[2])
        if not temp:
            temp = temp_record_list
            path_list = temp_path_record_list
        else:
            if (temp[0]!=temp_record_list[0]) or ((temp_record_list[1]-temp[2])>1200) or (temp[4]!=temp_record_list[3]):
                temp_path_list = list()
                for path in path_list:
                    temp_path_list.append(station_routeid_dict[path])
                if inter_station_list:
                    trans_list.append([mrt_station_dict[temp[3]], mrt_station_dict[temp[4]], inter_station_list, temp_path_list])
                ans_list.append(temp)
                temp = temp_record_list
                inter_station_list = list()
            else:
                path_list = path_list[:-1] + temp_path_record_list
                inter_station_list.append(mrt_station_dict[temp_record_list[3]])
                temp[2] = temp_record_list[2]
                temp[4] = temp_record_list[4]
    else:
        temp.append(inter_station_list)
        ans_list.append(temp)

    return (ans_list,trans_list)


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
    # data_list = get_mrt_data(mrt_file_name)
    # data_list_by_hour = group_data_by_hour(data_list)

    data_list,trans_list = output_inter_path(mrt_file_name)
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

    js_name = 'mrt_analysis/trans_data_'+mrt_file_name+'.data'
    w_file = open(js_name, 'w')
    write_content = str(trans_list)
    w_file.write(write_content)
    w_file.close()


