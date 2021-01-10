#-*- coding: utf-8 -*-

from fractions import Fraction
import random
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import numpy as np


def randomIdx(dist):
    l = len(dist)
    r = random.random()
    for i in range(0,l):
        if r < dist[i]:
            ret = i
            break
        else:
            r = r - dist[i]
            ret = i
    
    return ret


"""
BWH attack simulation function Based on a state machine
alpha : the BWH attacker pool's mining power
beta : the victim pool's mining power
Therefore, (1-alpha-beta) : honest mining pools' mining power
blocks : the number of blocks will be generated conceptually
check : whether the punishment rule based on the research paper is adopted or not
"""


def bwhReduction(alpha, beta, blocks, check):

    # alpha : BWH attacker pool's power
    # beta : BWH victim pool's power
    b = beta
    x = alpha
    a = alpha
    
    # Optimal BWH infiltration ratio
    t = -( (b * ( (-a * b - a + 1) ** 0.5 ) + (a - 1) * b ) / (a*b + a **2 - a))
    # print(t)
    
    # Reward reduction Least punishment coefficeint
    pun = b - ( b*((1 - a - a*b)**0.5) + (a - 1)*b ) / (b + a - 1)
    pun = 1
    # print(pun)
    
    # b_a : reward to attacker by victim
    # b_b : reward to victim by victim
    b_a = pun*t*a/(b+t*a)
    b_b = 1 - b_a
    
    dist = [alpha, beta, (1-alpha-beta)]
    # bwh_dist = [(1-t)*alpha, beta, (1-alpha-beta)]
    bwh_dist = [(1-t)*alpha / (1-t*alpha), beta / (1-t*alpha), (1-alpha-beta) / (1-t*alpha)]

    # State initialization
    # State follows the state machine figure in my research paper
    state = 0
    
    # Block initialization
    # The number of block each miner gets
    block = [0,0,0]
    
    # Rate initialization
    # The proportion of block each miner gets
    rate = [0,0,0]
    
    # Relative Revenue initialization
    # The proportion of block each miner gets
    relativeRevenue = [0,0,0]    
    
    # policy coefficient
    h = b + x*t
    
    for i in range(0,blocks):
        # mining block
        miner = randomIdx(bwh_dist)
        
        if miner == 0 :
            block[0] += 1
            
        elif miner == 1 :
            block[0] += b_a
            block[1] += b_b
            
        else:
            block[2] += 1
    
    # Counting block generation late
    sum = 0
    for num in block:
        sum += num
    for i in range(0,3):
        rate[i] = block[i]/sum    
        
    # Evalutate Relative Revenue
    for i in range(0,3):
        if dist[i] == 0:
            relativeRevenue[i] == 0
        else:
            relativeRevenue[i] = rate[i]/dist[i]       
    
    return (relativeRevenue)



def bwh(alpha, beta, blocks) :
    return bwhReduction(alpha, beta, blocks, 0)


# main function for module test    
if __name__=='__main__':
    
    
    density = 100
    A, B = np.meshgrid(np.linspace(0, 0.5, density), np.linspace(0, 0.5, density))
    bwh_profit = np.zeros((density, density))
    victim_profit = np.zeros((density, density))
    honest_profit = np.zeros((density, density))    
    

    blocks = 10000

    for i in range(0, density) :
        print('[+] blocks')
        for j in range(0, density) :
            rate = bwh(A[i,j], B[i,j], blocks)            
            # rate = bwhReduction(A[i,j], B[i,j], blocks, 1)
            bwh_profit[i,j] = rate[0]
            victim_profit[i,j] = rate[1]
            honest_profit[i,j] = rate[2]

    plt.contourf(A, B, bwh_profit, cmap=plt.cm.gray)
    plt.colorbar()
    plt.xlabel('BWH attacker hashrate')
    plt.ylabel('Victim miner hashrate')    
    plt.savefig('before reduction.png', dpi=1000)    
    np.save('simulation data bwh attacker before reduction', bwh_profit)
    np.save('simulation data bwh victim before reduction', victim_profit)
    np.save('simulation data bwh honest before reduction', honest_profit)   
    
    plt.show()