#! -*- coding:utf8 -*-

from preprocess_mrt_station import preprocess_mrt_station
from file_path_name import *

def generate_station_match():
    station_id_list, station_id_dict = preprocess_mrt_station()
    route_file = open(mrt_route_name, 'r')
    content = route_file.readlines()
    data_list = list()
    for record in content:
        record = record.decode('big5').encode('utf-8').replace('\r\n', '')
        record = record.split(',')
        data_list.append(record)
    route_list = list()
    temp_dict = dict()
    route_id_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    route_name_match  = dict()
    station_routeid_dict = dict()
    n = 0
    for i,data in enumerate(data_list):
        if i%3 == 0:
            route_name_match[route_id_list[n]] = data[0]
            temp = data[0].split('-')
            temp_dict['outset'] = temp[0]
            temp_dict['destination'] = temp[1]
        elif i%3 == 1:
            for j,station in enumerate(data):
                if not station:
                    break
                if station_routeid_dict.has_key(station):
                    station_routeid_dict[station] += '-'
                    station_routeid_dict[station] += route_id_list[n]+str(j)
                else:
                    station_routeid_dict[station] = route_id_list[n]+str(j)
            else:
                temp_dict['up_direction'] = data
            n += 1

    out_file = open('station_match.txt', 'w')
    out_file.write(str([station_id_list, station_id_dict, station_routeid_dict, route_name_match]))
    out_file.close()

def get_station_match():
    input_file = open('station_match.txt', 'r')
    content = input_file.readline()
    content = eval(content)
    return content


if __name__ == '__main__':
    generate_station_match()