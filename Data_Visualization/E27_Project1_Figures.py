# Use Matplotlib to make some graphs for E27 Project 1

import csv
import copy
import numpy as np
import matplotlib.pyplot as plt

FLY_DATA = 'fly_data.txt'           # fly centroids only
FLY_NUM_DATA = 'fly_num_data.txt'   # fly num: fly centroids

def read_data_from_txt(txt_filename):   # returns list
    data_list = []
    with open(txt_filename, 'rb') as datafile:
        for i in datafile:
            data_list.append(i.strip('\n'))
    return data_list

def clean_up(l):
    x_data = []
    y_data = []
    for val in l:
        val = val.strip('[').strip(']').strip(' ') .split()
        val[0] = float(val[0])
        val[1] = float(val[1])
        x_data.append(val[0])
        y_data.append(val[1])
    return x_data, y_data
    
def special_clean(num,l):
    # bug in num = 1 case
    x_data = []
    y_data = []
    append_flag = False
    for val in l:
        if (num < 10) and (str(num) == val[0]):
            append_flag = True
        if (num != 1) and (str(num) == val[:2]):
            append_flag = True
        if append_flag:
            val = val.strip(']').split()
            if '[' in val:
                del val[val.index('[')]
            val[1] = float(val[1])
            val[2] = float(val[2])
            x_data.append(val[1])
            y_data.append(val[2])
            append_flag = False
    return x_data, y_data  
    
def graph(x,y):
    plt.plot(x,y,'r-')
    plt.show()
    
def graph_of_all_data():
    # read all data points
    all = read_data_from_txt(FLY_DATA)
    
    # put data in the right form to graph
    x_points, y_points = clean_up(all)
    
    # plot all data points
    graph(x_points,y_points)
    
def graph_of_fly(fly_num):
    # read all data points
    all = read_data_from_txt(FLY_NUM_DATA)
    
    # get all points for certain fly
    x_points,y_points = special_clean(fly_num,all)
    
    # plot
    graph(x_points,y_points)
        
def main():
    # graph of all data points
    #graph_of_all_data()
    
    # graph of individual fly
    graph_of_fly(0)
    graph_of_fly(5)
    graph_of_fly(10)
    graph_of_fly(14)

main()