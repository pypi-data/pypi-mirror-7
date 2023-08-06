#!python
#cython: boundscheck=False
#cython: wraparound=False

'''
Created on Jun 4, 2014

@author: holtjma
'''

import math
import os
import time

import numpy as np
cimport numpy as np

from multiprocessing.pool import ThreadPool
from threading import RLock

def testLoopingTimes(unsigned long numBits):
    #cdef np.ndarray[np.int64_t, ndim=1, mode='c'] vals = np.random.randint(2, size=numBits)
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] vals = np.zeros(dtype='<u1', shape=(numBits, ))
    vals[:] = np.random.randint(2, size=numBits)[:]
    cdef np.uint8_t [:] vals_view = vals
    
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] counts = np.zeros(dtype='<u8', shape=(2, ))
    cdef np.uint64_t [:] counts_view = counts
    cdef unsigned long c0 = 0, c1 = 0
    
    cdef double st, et
    
    st = time.time()
    for x in range(0, numBits):
        if vals_view[x]:
            c1 += 1
        else:
            c0 += 1
    et = time.time()
    print c0, c1, et-st
    
    st = time.time()
    for x in range(0, numBits):
        counts_view[vals_view[x]] += 1
    et = time.time()
    
    print counts, et-st
    

def testThreading():
    myPool = ThreadPool(8)
    
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] ret = np.zeros(dtype='<u8', shape=(8, ))
    cdef np.uint64_t [:] ret_view = ret
    cdef unsigned long pointer = <unsigned long> &ret_view[0]
    rlock = RLock()
    
    tups = []
    for x in range(0, 8):
        tups.append((x, pointer, rlock))
    
    myPool.map(threadedFunc, tups)
    print ret
    
def threadedFunc(tup):
    cdef unsigned long id = tup[0]
    cdef unsigned long pointer = tup[1]
    rlock = tup[2]
    
    cdef np.uint64_t * arr = <np.uint64_t *>pointer
    cdef unsigned long x
    
    arr[id] = 0
    rlock.acquire()
    with nogil:
        for x in range(0, 10**9):
            arr[id] += id
            arr[id] = arr[id] % 7
    rlock.release()

def calculateNumRuns(char * fn):
    cdef unsigned long runs = 1
    
    cdef np.ndarray[np.int8_t, ndim=1, mode='c'] arr = np.load(fn, 'r+')
    cdef np.int8_t [:] arr_view = arr
    
    cdef unsigned long x
    for x in range(1, arr.shape[0]):
        if arr_view[x] != arr_view[x-1]:
            runs += 1
    
    return runs

def shiftQualityByBWT(char * inputQualFN, char * bwtDir, char * outputQualFN):
    cdef unsigned long nvc = 6
    
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] bwt = np.load(bwtDir+'/msbwt.npy', 'r+')
    cdef np.uint8_t [:] bwt_view = bwt
    
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] totalCounts
    cdef np.uint64_t [:] totalCounts_view
    
    cdef unsigned long x
    
    if os.path.exists(bwtDir+'/totalCounts.npy'):
        totalCounts = np.load(bwtDir+'/totalCounts.npy')
        totalCounts_view = totalCounts
    else:
        totalCounts = np.zeros(dtype='<u8', shape=(nvc, ))
        totalCounts_view = totalCounts
        for x in range(0, bwt.shape[0]):
            totalCounts_view[bwt_view[x]] += 1
        np.save(bwtDir+'/totalCounts.npy', totalCounts)
    
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] offsets = np.cumsum(totalCounts)-totalCounts
    cdef np.uint64_t [:] offsets_view = offsets
    
    cdef np.ndarray[np.int8_t, ndim=1, mode='c'] inputQuals = np.load(inputQualFN, 'r+')
    cdef np.int8_t [:] inputQuals_view = inputQuals
    cdef np.ndarray[np.int8_t, ndim=1, mode='c'] outputQuals = np.lib.format.open_memmap(outputQualFN, 'w+', '<i1', (bwt.shape[0], ))
    cdef np.int8_t [:] outputQuals_view = outputQuals
    cdef np.uint8_t symbol
    
    for x in range(0, bwt.shape[0]):
        symbol = bwt_view[x]
        outputQuals_view[offsets_view[symbol]] = inputQuals_view[x]
        offsets_view[symbol] += 1

def gatherStats(char * qualFN, unsigned long strLen):
    cdef np.ndarray[np.int8_t, ndim=1, mode='c'] quals = np.load(qualFN, 'r+')
    cdef np.int8_t [:] quals_view = quals
    
    cdef unsigned long numSeqs = quals.shape[0]/strLen
    cdef unsigned long x, y
    
    cdef dict dupDict = {}
    cdef unsigned long dupCount = 0
    
    cdef unsigned long runSymbols = 0
    
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] symbolCounts = np.zeros(dtype='<u8', shape=(35, ))
    cdef np.uint64_t [:] symbolCounts_view = symbolCounts
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] deltaCounts = np.zeros(dtype='<u8', shape=(5, ))
    cdef np.uint64_t [:] deltaCounts_view = deltaCounts
    
    cdef dict counter = {}
    
    for x in range(0, numSeqs):
        sig = quals[strLen*x:strLen*(x+1)].tostring()
        sig1 = sig[0:strLen/2]
        sig2 = sig[strLen/2:]
        
        if dupDict.has_key(sig1):
            dupCount += 1
        else:
            dupDict[sig1] = x
            
            symbolCounts[quals_view[x*strLen]] += 1
            for y in range(1, strLen/2):
                if abs(quals_view[x*strLen+y] - quals_view[x*strLen+y-1]) <= 2:
                    deltaCounts_view[quals_view[x*strLen+y] - quals_view[x*strLen+y-1]+2] += 1
                    runSymbols += 1
                else:
                    symbolCounts[quals_view[x*strLen+y]] += 1
            
            if True or x < 1000:
                for y in range(2, strLen/2):
                    key = (quals[x*strLen+y-1:x*strLen+y+1]-quals[x*strLen+y-2:x*strLen+y]).tostring()
                    counter[key] = counter.get(key, 0)+1
                    
        if dupDict.has_key(sig2):
            dupCount += 1
        else:
            dupDict[sig2] = x
            
            symbolCounts[quals_view[x*strLen+strLen/2]] += 1
            for y in range(strLen/2+1, strLen):
                if abs(quals_view[x*strLen+y] - quals_view[x*strLen+y-1]) <= 2:
                    deltaCounts_view[quals_view[x*strLen+y] - quals_view[x*strLen+y-1]+2] += 1
                    runSymbols += 1
                else:
                    symbolCounts[quals_view[x*strLen+y]] += 1
            
            if True or x < 1000:
                for y in range(strLen/2+2, strLen):
                    key = (quals[x*strLen+y-1:x*strLen+y+1]-quals[x*strLen+y-2:x*strLen+y]).tostring()
                    counter[key] = counter.get(key, 0)+1
    
    print dupCount, numSeqs, 1.0*dupCount/numSeqs, runSymbols, quals.shape[0], 1.0*runSymbols/quals.shape[0]
    print symbolCounts
    print deltaCounts
    
    cdef double repSymbols = np.sum(symbolCounts)+np.sum(deltaCounts)
    cdef double bits = repSymbols*math.log(repSymbols, 2)
    
    print bits
    for x in range(0, symbolCounts.shape[0]):
        if symbolCounts_view[x] > 0:
            bits -= symbolCounts_view[x]*math.log(symbolCounts_view[x], 2)
    for x in range(0, deltaCounts.shape[0]):
        if deltaCounts_view[x] > 0:
            bits -= deltaCounts_view[x]*math.log(deltaCounts_view[x], 2)
    print bits
    print bits/quals.shape[0]
    
    #bits += 64*dupCount
    print 64*dupCount
    print 64.0*dupCount/(strLen/2*dupCount)
    
    totalDoubles = 0
    for val in counter:
        totalDoubles += counter[val]
    for val in sorted(counter, key=counter.get)[-100:]:
        print [z.encode('hex') for z in val], counter[val], 1.0*counter[val]/totalDoubles