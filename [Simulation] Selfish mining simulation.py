#-*- coding: utf-8 -*-

from fractions import Fraction
import sys
import random
import copy
import numpy as np
import matplotlib.pyplot as plt



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
Detective mining simulation function Based on a state machine
alpha : the selfish mining pool's mining power
delta : the detevtive mining pool's mining power
Therefore, (1-alpha-delta) : honest mining pools' mining power
blocks : The number of blocks will be generated conceptually

"""

def detectiveMining(alpha, delta, gamma, blocks):
    
    # gamma is an always fair value
    # for example, 2 -> 1/2 , 3-> 1/3 ... etc
    
    #leakage_ratio = delta/(1-alpha)
    dist = [alpha, delta, (1-alpha-delta)]
    
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
    

    for i in range(0, blocks):        
        
        miner = randomIdx(dist)
        # debug
        # print(miner)
        
        # State -1 means State 0' for simplicity
        if state == -1 :
            if miner == 0:
                block[0] += 2
                state = 0
                
                # miners should select a block among fork chains
            if miner == 1:
                select = randomIdx([gamma, (1-gamma)])
                if select == 0:
                    block[0] += 1
                    block[1] += 1
                    state = 0
                else:
                    block[1] += 1
                    block[2] += 1
                    state = 0
                
            if miner == 2:
                select = randomIdx([gamma, (1-gamma)])
                if select == 0:
                    block[0] += 1
                    block[2] += 1
                    state = 0
                else:
                    block[2] += 2
                    state = 0                
        
        elif state == 0 :
            if miner == 0:
                block[0] += 0
                state = 1
                
            if miner == 1:
                block[1] += 1
                state = 0
                
            if miner == 2:
                block[2] += 1
                state = 0
                
            
        elif state == 1 :
            if miner == 0:
                block[0] += 0
                state = 2
                
            if miner == 1:
                block[0] += 1
                block[1] += 1
                state = 0

            if miner == 2:
                block[2] += 0
                state = -1
                
        elif state == 2 :
            if miner == 0:
                block[0] += 0
                state = 3
                    
            if miner == 1:
                block[0] += 2
                block[1] += 1
                state = 0
    
            if miner == 2:
                block[0] += 2
                state = 0        
                
            
        # State > 2
        else:
            if miner == 0:
                block[0] += 0
                state += 1                
                
            if miner == 1:
                block[0] += state
                block[1] += 1
                state = 0
                
            if miner == 2:
                # State is decreased but the block will be a profit of the selfish miner
                block[0] += 1
                state -= 1

    # If the selfish miner has a private chain, then it should be taken in the result
    if state > 0:
        block[0] += state
            
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
    
    # debug
    # print('[+] A blocks finished')
    return (relativeRevenue)


"""
Selfish mining simulation function Based on a state machine
alpha : the selfish mining pool's mining power
Therefore, (1-alpha) : honest mining pools' mining power
blocks : The number of blocks will be generated conceptually

It is the case when there is no detective miners.

"""

def selfishMining(alpha, gamma, blocks):
    rate = detectiveMining(alpha, 0, gamma, blocks)
    return [rate[0], rate[2]]


# main function for module test    
if __name__=='__main__':
    
    # alpha = 0.48
    # delta = 0.48
    # gamma = 0.5
    # blocks = 10000
    
    # rate = selfishMining(0.3, 0.5, 1000)
    # rate = detectiveMining(alpha, delta, gamma, blocks)
    # print(rate)
    
    density = 10
    A, B = np.meshgrid(np.linspace(0, 0.5, density), np.linspace(0, 1, density))
    selfish_profit = np.zeros((density, density))
    honest_profit = np.zeros((density, density))
    

    blocks = 10000

    for i in range(0, density) :
        print('[+] blocks')
        for j in range(0, density) :
            rate = selfishMining(A[i,j], B[i,j], blocks)            
            # rate = bwhReduction(A[i,j], B[i,j], blocks, 1)
            selfish_profit[i,j] = rate[0]
            honest_profit[i,j] = rate[1]

    plt.contourf(A, B, selfish_profit, cmap=plt.cm.gray)
    plt.colorbar()
    plt.xlabel('Selfish mining hashrate')
    plt.ylabel('Network coefficient hashrate')    
    plt.savefig('Selfish mining.png', dpi=1000)    
    plt.show()
    
