### py2 ###
from __future__ import division
######
import multiprocessing as mp
import threading as td
import numpy as np
import copy

def dynamic_model(start_p, end_p, proc, type = 0, action = 0):
    if type == 0:
        cur_p = start_p + proc * (end_p - start_p)
        if action is not None:
            rate = proc - 0.5
            thre = 0.2
            change = [end_p[0]-start_p[0],end_p[1]-start_p[1]]
            # turning location adjustment
            if change[0] != 0 and change[1] != 0 and rate < thre and rate >=0 :
                cur_p = [start_p[0] + (end_p[0]-start_p[0])*(0.5+thre),start_p[1] + (end_p[1]-start_p[1])*(0.5+thre)]
                if (change[0]*change[1] > 0 and action == 1) or (change[0]*change[1] < 0 and action == 0):
                    cur_p[0] = cur_p[0] - 2*(thre-rate)*change[0]
                else:
                    cur_p[1] = cur_p[1] - 2*(thre-rate)*change[1]
            elif change[0] != 0 and change[1] != 0 and rate < 0 and rate > -thre:
                cur_p = [start_p[0] + (end_p[0]-start_p[0])*(0.5-thre),start_p[1] + (end_p[1]-start_p[1])*(0.5-thre)]
                if (change[0]*change[1] > 0 and action == 1) or (change[0]*change[1] < 0 and action == 0):
                    cur_p[1] = cur_p[1] + 2*(thre+rate)*change[1]
                else:
                    cur_p[0] = cur_p[0] + 2*(thre+rate)*change[0]
        return cur_p
    else:
        return None

# data = {cur_time, point}
# [starting_node, ending_node, starting_time, point_location, lifetime, point_flags]
# [0            , 1          , 2            , 3,            , 4       , 5     ]
# point_flags:[status(loaded),count_out,]

def updating_func(temp_update, temp_update_dict, start, end, typ, num):
    keystr = str(start)+'_'+str(end)+'_'+str(typ)
    if keystr in temp_update_dict.keys():
        temp_update[temp_update_dict[keystr]][3] += num
    else:
        temp_update_dict[keystr] = len(temp_update)
        temp_update.append([start, end, typ, num])

# work on datas
def worker(qin, qout, m, n, noj, blocksize, dis_matrix, pre_matrix, locations, junc2block):
    while True:
        task = qin.get()        
        if task is None:
            break
        cur_time = task['cur_time']
        point = task['point']
        moving_time = cur_time - point[2]
        remaining_time = point[2] + point[4] - cur_time

        # unit arrives, removed
        if point[4] < moving_time:
            qout.put((point[0], point[1], point[5][0]))

        # unit on its way
        if moving_time >= 0:
            new_flags = copy.copy(point[5])

            # get out of entrance 
            if point[0] < (m + n) and not new_flags[1]:
                new_flags[1] = True
                updating_func(temp_update, temp_update_dict, point[0], point[1], new_flags[0], -1)

            if point[1] < (2*m + 2*n) or remaining_time > 5:
                loc0 = []
                loc1 = []
                pre_point = point[1]
                timing = float(dis_matrix[point[0]][pre_point])
                direction = None
                while True:
                    loc1 = locations[pre_point]
                    next_timing = timing
                    pre_point = int(pre_matrix[point[0]][pre_point])
                    timing = float(dis_matrix[point[0]][pre_point])
                    if timing <= moving_time:
                        loc0 = locations[pre_point] 
                        if (next_timing - timing) == 10:    # unit is turning
                            order = pre_point - 2*m - 2*n - noj
                            x1 = np.mod(order, 4)
                            x2 = np.floor(order/(4*n))
                            x3 = np.floor(order/4)
                            direction = np.mod(x1+x2+x3,2)  #0 right; 1 left
                        else:
                            direction = None
                        break

                new_location = dynamic_model(loc0, loc1, (moving_time-timing)/(next_timing-timing), type = 0, action = direction)

                ''' 
                new_location = [loc0[0] + (loc1[0]-loc0[0])*(moving_time-timing)/(next_timing-timing), 
                    loc0[1] + (loc1[1]-loc0[1])*(moving_time-timing)/(next_timing-timing)]

                rate = ((moving_time-timing)/(next_timing-timing)-0.5)
                thre = 0.2
                change = [loc1[0]-loc0[0],loc1[1]-loc0[1]]
                # turning location adjustment
                if change[0] != 0 and change[1] != 0 and rate < thre and rate >=0 :
                    new_location = [loc0[0] + (loc1[0]-loc0[0])*(0.5+thre),loc0[1] + (loc1[1]-loc0[1])*(0.5+thre)]
                    if (change[0]*change[1] > 0 and direction == 1) or (change[0]*change[1] < 0 and direction == 0):
                        new_location[0] = new_location[0] - 2*(thre-rate)*change[0]
                    else:
                        new_location[1] = new_location[1] - 2*(thre-rate)*change[1]
                elif change[0] != 0 and change[1] != 0 and rate < 0 and rate > -thre:
                    new_location = [loc0[0] + (loc1[0]-loc0[0])*(0.5-thre),loc0[1] + (loc1[1]-loc0[1])*(0.5-thre)]
                    if (change[0]*change[1] > 0 and direction == 1) or (change[0]*change[1] < 0 and direction == 0):
                        new_location[1] = new_location[1] + 2*(thre+rate)*change[1]
                    else:
                        new_location[0] = new_location[0] + 2*(thre+rate)*change[0]
                '''

            
            # get into junction        
            elif remaining_time <= 5:
                block_loc = junc2block[point[1] - 2*m - 2*n]
                exitan = [(2+block_loc[1])*blocksize[0],(m-block_loc[0])*blocksize[1]]
                junc_loc = locations[point[1]]
                new_location = [exitan[0]*(5-remaining_time)/5+junc_loc[0]*remaining_time/5,
                    exitan[1]*(5-remaining_time)/5+junc_loc[1]*remaining_time/5]
                new_flags[2] = True

            qout.put({'cur_time': cur_time, 'point': [point[0], point[1], point[2], 
                new_location, point[4], new_flags]})

        # get out of junction , waiting to move
        elif point[0] >= 2*m+2*n:

            ##### NEED MORE WORK! #####
            block_loc = junc2block[point[0] - 2*m - 2*n]
            exitan = [(2+block_loc[1])*blocksize[0],(m-block_loc[0])*blocksize[1]]
            junc_loc = locations[point[0]]
            '''
            new_location = [exitan[0]*(-moving_time)/rhythm + junc_loc[0]*(1+moving_time/rhythm),
                exitan[1]*(-moving_time)/rhythm + junc_loc[1]*(1+moving_time/rhythm)]
            '''

            new_location = junc_loc
            ###########################

            new_flags = copy.copy(point[5])
            if not new_flags[1]:
                new_flags[1] = True
                updating_func(temp_update, temp_update_dict, point[0], point[1], new_flags[0], -1)

            qout.put({'cur_time':cur_time, 'point': [point[0], point[1], point[2], 
                new_location, point[4], new_flags]}) 
        
        # get out of entrance , waiting to move
        else:
            qout.put({'cur_time': cur_time, 'point': copy.copy(point)})

# distribute tasks, update result
def supervisor(q_frame, qin, qout, time_duration, schedule, m, n, noj, dis_matrix, locations, rhythm, mp_num, q_length):
    wave = 0 
    tasks = []
    next_tasks = []
    temp_res = []
    temp_update = []
    temp_update_dict = {}
    timer = 0
    next_wave = 0
    counting = 0
    while True: 
        if len(tasks) == 0:
            if wave >= len(schedule):
                if len(temp_res) == 0: 
                    for _ in range(mp_num):
                        qin.put(None)
                    print("calculating done!")
                    break
            elif counting == 0:
                timer += time_duration
                tasks += next_tasks
                next_tasks = []

                q_frame.put([temp_res, temp_update])
                temp_res = []
                temp_update = []
                temp_update_dict = {}

                if timer >= next_wave:
                    next_wave += rhythm
                    wave += 1
                    for point in schedule[wave]:
                        data = {}
                        tasks_location = [int(point[0]),int(point[1]) + m + n]
                        if tasks_location[0] >= m + n:
                            tasks_location[0] = tasks_location[0] + m + n
                        lifetime = float(dis_matrix[tasks_location[0]][tasks_location[1]])
                        if tasks_location[1] >= 2*m + 2*n:
                            lifetime += 5
                        for i in range(int(point[3])):
                            point_flags = [int(point[4]), False, False] # loaded, on_road, finish
                            data['cur_time'] = timer
                            data['point'] = [tasks_location[0], tasks_location[1], wave*rhythm, 
                                locations[tasks_location[0]], lifetime, point_flags]
                            tasks.append(data)
                counting = len(tasks)
                for i in range(q_length):
                    qin.put(tasks.pop(0))

        try:
            new_task = qout.get(timeout=1)
            counting -= 1
            if len(tasks) > 0:
                qin.put(tasks.pop(0))
            if isinstance(new_task, list):
                updating_func(temp_update, temp_update_dict, new_task[0], new_task[1], new_task[2], 1)
            else:
                next_tasks.append({'cur_time':new_task['cur-time']+time_duration, 'point':new_task['point']})
                temp_res.append(new_task['point'])
        except Exception as e:
            print(e)
    q_frame.put(None)

def simulating(time_duration, q_frame, schedule, rhythm, m, n, noj, blocksize, dis_matrix, pre_matrix, locations, junc2block):
    q_length = 100
    qin = mp.Queue(q_length)
    qout = mp.Queue(q_length)
    mp_num = 4
    th_su = td.Thread(target=supervisor, 
        args = (q_frame, qin, qout, time_duration, schedule, m, n, noj, dis_matrix, locations, rhythm, mp_num, q_length,))
    th_su.start()

    mps = []
    for i in range(mp_num):
        m1 = mp.Process(target=worker, args=(qin, qout, m, n, noj, blocksize, 
            dis_matrix, pre_matrix, locations, junc2block))
        mps.append(m1)
        m1.start()
    th_su.join()
    for point in mps:
        point.join()