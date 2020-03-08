### py2 ###
from __future__ import division
######
import numpy as np
import copy
import wx


def test_lor():
    new_lor = []
    new_lor += [2.5, 5, 2.5]*6*(6+6)
    new_lor += [10]*6*6*2 
    return new_lor

def test_Ts():
    new_Ts = []
    new_Ts += [0]*6
    new_Ts += [5]*6
    new_Ts += [0]*5*6
    new_Ts += [5]*5*6
    return new_Ts

def test_juncs():
    return []

# m, n: num of horizontal and vertical main roads
# noj: num of junctions
# juncs: coordinates of junctions
# Ts: entry time of nodes (entrances and junctions)
#       horizontal entrance, vertical entrance, horizontal junction, vertical junction
# lor: length of roads (equivalent time)
#       matrix; [hor_entrance, ver_entrance, hor_exit, ver_exit, junction, intersection]
def Dijkstra(gm,start):
    num_of_node = len(gm)
    res, pre, dis = [0]*num_of_node,[start]*num_of_node,[0]*num_of_node
    for i in range(num_of_node):
        dis[i] = gm[start][i]
    dis[start] = 0
    res[start] = 1
    # iter for num_of_node-1 times 
    for v in range(1,num_of_node):
        min_v = float("Inf")
        for w in range(num_of_node):
            if not res[w] and dis[w] < min_v:
                min_v = dis[w]
                k = w
        res[k] = 1
        for w in range(num_of_node):
            if not res[w] and min_v + gm[k][w] < dis[w]:
                dis[w] = min_v + gm[k][w]
                pre[w] = k
    
    return res, pre, dis

class Pathes():
    def __init__(self, existance, startp=0, endp=0, path=[], length=0):
        self.existance = existance
        if existance==1:
            self.start_point = startp
            self.end_point = endp
            self.path = copy.copy(path)
            self.length = length
        else:
            pass
    def change(self, existance, startp=0, endp=0, path=[], length=0):
        self.existance = existance
        self.start_point = startp
        self.end_point = endp
        self.path = copy.copy(path)
        self.length = length

def generate_path_rhythm(num_of_nodes, edges):
    pre_matrix = -np.ones((num_of_nodes,num_of_nodes))
    dis_matrix = np.inf * np.ones((num_of_nodes,num_of_nodes))
    res_matrix = np.zeros((num_of_nodes,num_of_nodes))
    for i in range(num_of_nodes):
        ###
        print("processing node %d" %i)
        ###
        for edge in edges[i]:
            dis_matrix[i][edge[0]] = edge[1]
        dis_matrix[i][i] = 0
        res_matrix[i][i] = 1
        # iter for num_of_node-1 times 
        for v in range(1,num_of_nodes):
            min_v = np.inf
            k = -1
            for w in range(num_of_nodes):
                if res_matrix[i][w]==0 and dis_matrix[i][w] < min_v:
                    min_v = dis_matrix[i][w]
                    k = w
            res_matrix[i][k] = 1
            if v == 1:
                pre_matrix[i][k] = i
            for edge in edges[k]:
                if res_matrix[i][edge[0]]==0 and min_v + edge[1] < dis_matrix[i][edge[0]]:
                    dis_matrix[i][edge[0]] = min_v + edge[1]
                    pre_matrix[i][edge[0]] = k
    return pre_matrix,dis_matrix

#testing
if __name__ == "__main__":
    m = 6
    n = 6
    noj = 60

    juncs = []
    #[x,y]
    for j in range(m):
        for i in range(n-1):
            juncs.append([i+0.5, j])
    for i in range(n):
            for j in range(m-1):
                juncs.append([i, j+0.5])

    Ts = []
    for i in range(m):
        Ts.append(0)
    for i in range(n):
         Ts.append(5)
    for i in range(m):
        for j in range(n-1):
            Ts.append(0)
    for i in range(n):
        for j in range(m-1):
            Ts.append(5)      

    lor = np.ones([2*m+2*n+noj+4*m*n,2*m+2*n+noj+4*m*n])
    lor = lor * 10000
    #entrance 2 intersection
    for i in range(m):
        if np.mod(i,2) == 0:
            lor[i,2*m+2*n+noj+4*i*n] = 2.5
        else:
            lor[i,2*m+2*n+noj+4*(i+1)*n-4] = 2.5
    for i in range(n):
        if np.mod(i,2) == 0:
            lor[m+i,2*m+2*n+noj+4*(m-1)*n+4*i+1] = 2.5
        else:
            lor[m+i,2*m+2*n+noj+4*i+1] = 2.5
    #intersection 2 exit
    for i in range(m):
        if np.mod(i,2) == 0:
            lor[2*m+2*n+noj+4*(i+1)*n-2,m+n+i] = 2.5
        else:
            lor[2*m+2*n+noj+4*i*n+2,m+n+i] = 2.5
    for i in range(n):
        if np.mod(i,2) == 0:
            lor[2*m+2*n+noj+4*i+3,m+n+m+i] = 2.5
        else:
            lor[2*m+2*n+noj+4*(m-1)*n+4*i+3,m+n+m+i] = 2.5
    #junction 2 intersection and inverse
    for i in range(noj):
        pos = juncs[i]
        if np.mod(pos[0]*2,2) == 1:         # junction in row
            intersec1 = [pos[1],int(pos[0]-0.5)]
            intersec2 = [pos[1],int(pos[0]+0.5)]
            if np.mod(pos[1], 2) == 0:      # odd row
                lor[2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4+2, 2*m+2*n+i] = 2.5
                lor[2*m+2*n+i, 2*m+2*n+noj+intersec2[0]*4*n+intersec2[1]*4] = 2.5 
            else:
                lor[2*m+2*n+noj+intersec2[0]*4*n+intersec2[1]*4+2, 2*m+2*n+i] = 2.5
                lor[2*m+2*n+i, 2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4] = 2.5 
        else:
            intersec1 = [int(pos[1]-0.5),pos[0]]
            intersec2 = [int(pos[1]+0.5),pos[0]]
            if np.mod(pos[0], 2) == 0:      # odd column
                lor[2*m+2*n+noj+intersec2[0]*4*n+intersec1[1]*4+3, 2*m+2*n+i] = 2.5
                lor[2*m+2*n+i, 2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4+1] = 2.5
            else:
                lor[2*m+2*n+noj+intersec1[0]*4*n+intersec1[1]*4+3, 2*m+2*n+i] = 2.5
                lor[2*m+2*n+i, 2*m+2*n+noj+intersec2[0]*4*n+intersec2[1]*4+1] = 2.5
    #intersection to intersection
    for i in range(m):
        for j in range(n):
            intersec = 2*m+2*n+noj+i*4*n+j*4
            lor[intersec,intersec+3] = 10
            lor[intersec+1,intersec+2] = 10
            lor[intersec,intersec+2] = 5
            lor[intersec+1,intersec+3] = 5

    #0
    for i in range(m):
        for j in range(n):
            if i==j:
                lor[i,j] = 0

    #recording edges
    num_of_nodes = len(lor)
    edges = [[] for _ in range(num_of_nodes)]
    for i in range(num_of_nodes):
        for j in range(num_of_nodes):
            if lor[i][j] < 10000:
                edges[i].append((j,lor[i][j]))

    pre_matrix,dis_matrix = generate_path_rythmn(num_of_nodes, edges)
    
    
    print(1)