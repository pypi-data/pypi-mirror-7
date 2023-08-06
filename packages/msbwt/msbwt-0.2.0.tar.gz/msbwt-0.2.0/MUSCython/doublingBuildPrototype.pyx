#!python
#cython: boundscheck=False
#cython: wraparound=False

import binascii
import math
import multiprocessing
import numpy as np
cimport numpy as np
import os
import time

from cython.operator cimport preincrement as inc

import MSBWTGenCython as MSBWTGen

def doublingBuild(char * bwtDir, logger, ramOnly=False):
    
    MSBWTGen.clearAuxiliaryData(bwtDir)
    
    ###########################################
    #Section for init to X-mer, currently X = 1
    ###########################################
    #this value determines how we seed the merge k-mer wise
    cdef unsigned int currK = 10
    
    st = time.time()
    stc = time.clock()
    
    logger.info('Counting '+str(currK)+'-mers...')
    
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] seqs = np.load(bwtDir+'/seqs.npy', 'r+')
    cdef np.uint8_t [:] seqs_view = seqs
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] offsets = np.load(bwtDir+'/offsets.npy', 'r+')
    cdef np.uint64_t [:] offsets_view = offsets
    
    #cdef dict tc = {}
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] tc = np.zeros(dtype='<u8', shape=(6**currK, ))
    cdef np.uint64_t [:] tc_view = tc
    cdef unsigned long binMod = 6**currK
    cdef unsigned long x, y, z
    cdef unsigned long currBin
    cdef unsigned long seqLen
    
    for x in xrange(0, offsets.shape[0]-1):
        #initialize the code
        currBin = 0
        seqLen = offsets_view[x+1]-offsets_view[x]
        for y in xrange(0, currK):
            #currBin = 6*currBin+getCharOfSeq(seqs_view, offsets_view, x, y)
            currBin = 6*currBin+seqs_view[offsets_view[x]+(y % seqLen)]
            
        #now for each value, we do this
        for y in xrange(currK, currK+offsets_view[x+1]-offsets_view[x]):
            #first save this
            #tc[currBin] = tc.get(currBin, 0)+1
            tc_view[currBin] += 1
            
            #calculate next bin
            currBin = (6*currBin+seqs_view[offsets_view[x]+(y % seqLen)]) % binMod
    
    #TODO: is 4 billion enough? is 2^16 enough characters? can we do dynamics with cython?
    #print len(tc), 6**currK
    
    logger.info('Initializing '+str(currK)+'-mer array...')
    
    #the string number, aka which read it is, we only need one of these
    seqIDType = '<u4'
    cdef np.ndarray[np.uint32_t, ndim=1, mode='c'] seqID 
    if ramOnly:
        seqID = np.zeros(dtype=seqIDType, shape=(seqs.shape[0], ))
    else:
        seqID = np.lib.format.open_memmap(bwtDir+'/seqID.npy', 'w+', seqIDType, (seqs.shape[0], ))
    cdef np.uint32_t [:] seqID_view = seqID
    
    #the offset of the symbol into the string, we only need one of these
    offseqType = '<u2'
    cdef np.ndarray[np.uint16_t, ndim=1, mode='c'] offseq 
    if ramOnly:
        offseq = np.zeros(dtype=offseqType, shape=(seqs.shape[0], ))
    else:
        offseq = np.lib.format.open_memmap(bwtDir+'/offseq.npy', 'w+', offseqType, (seqs.shape[0], ))
    cdef np.uint16_t [:] offseq_view = offseq
    
    #relates the position of the symbol from the input to it's output, only one again
    revDictType = '<u8'
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] revDict
    if ramOnly:
        revDict = np.zeros(dtype=revDictType, shape=(seqs.shape[0], ))
    else:
        revDict = np.lib.format.open_memmap(bwtDir+'/revDict.npy', 'w+', revDictType, (seqs.shape[0], ))
    cdef np.uint64_t [:] revDict_view = revDict
    
    #array indicating the end of k-mer groups, 1 indicates an end, still should only need one
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] endsWrite 
    if ramOnly:
        endsWrite = np.zeros(dtype='<u1', shape=(seqs.shape[0]/8+1, ))
    else:
        endsWrite = np.lib.format.open_memmap(bwtDir+'/ends'+str(currK)+'.npy', 'w+', '<u1', (seqs.shape[0]/8+1, ))
    cdef np.uint8_t [:] endsWrite_view = endsWrite
    
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] endsRead
    cdef np.uint8_t [:] endsRead_view
    
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] tempEnds
    
    cdef unsigned long fmTot = 0
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] fm = np.zeros(dtype='<u8', shape=(6**currK, ))
    cdef np.uint64_t [:] fm_view = fm
    
    cdef unsigned long binType
    
    #we have to skip the all of the starting empty bins so we don't try to set fm_view[-1] and get thrown errors
    cdef unsigned long minBin = 0
    while tc_view[minBin] == 0:
        minBin += 1
    
    #for binType in sorted(tc.keys()):
    for binType in xrange(minBin, binMod):
        fm_view[binType] = fmTot
        fmTot += tc_view[binType]
        setBit(endsWrite_view, fmTot-1)
        
    #create an additional array we will use for ping-ponging
    if not ramOnly:
        np.lib.format.open_memmap(bwtDir+'/ends'+str(2*currK)+'.npy', 'w+', '<u1', (seqs.shape[0]/8+1, ))
    else:
        endsRead = np.zeros(dtype='<u1', shape=(seqs.shape[0]/8+1, ))
    
    cdef unsigned long i = 0
    cdef unsigned long fmi
    for x in xrange(0, offsets.shape[0]-1):
        #initialize the code
        currBin = 0
        seqLen = offsets_view[x+1]-offsets_view[x]
        for y in xrange(0, currK):
            currBin = 6*currBin+seqs_view[offsets_view[x]+(y % seqLen)]
            
        #now for each value, we do this
        for y in xrange(0, offsets_view[x+1]-offsets_view[x]):
            #pull the fm value and increment it
            fmi = fm_view[currBin]
            fm_view[currBin] += 1
            
            #write the appropriate values out
            seqID_view[fmi] = x
            offseq_view[fmi] = y
            revDict_view[i] = fmi
            inc(i)
            
            #calculate next bin
            currBin = (6*currBin+seqs_view[offsets_view[x]+((y+currK) % seqLen)]) % binMod
    
    etc = time.clock()
    et = time.time()
    
    logger.info('Finished init in '+str(et-st)+' seconds ('+str(etc-stc)+' clock).')
    
    ###########################################
    #End Init
    ###########################################
    
    #doubling loop
    cdef bint changesMade = True
    cdef unsigned long rangeStart, rangeDelta
    cdef unsigned long ind, pInd
    cdef unsigned long prevRevDict
    
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] pairsRevDict
    cdef np.uint64_t [:] pairsRevDict_view
    cdef np.ndarray[np.uint32_t, ndim=1, mode='c'] pairsSeqID
    cdef np.uint32_t [:] pairsSeqID_view
    cdef np.ndarray[np.uint16_t, ndim=1, mode='c'] pairsOffseq
    cdef np.uint16_t [:] pairsOffseq_view
    
    #TODO: can we make this unsigned?, i don't know how to force numpy to do it
    cdef np.ndarray[np.int64_t, ndim=1, mode='c'] npargsort
    cdef np.int64_t [:] npargsort_view
    cdef unsigned long writePos
    
    while changesMade:
        changesMade = False
        
        if ramOnly:
            tempEnds = endsRead
            
            endsRead = endsWrite
            endsRead_view = endsRead
            
            endsWrite = tempEnds
            endsWrite_view = endsWrite
        else:
            endsRead = np.load(bwtDir+'/ends'+str(currK)+'.npy', 'r+')
            endsRead_view = endsRead
            endsWrite = np.load(bwtDir+'/ends'+str(2*currK)+'.npy', 'r+')
            endsWrite_view = endsWrite
        
        logger.info('Beginning iteration '+str(2*currK)+'...')
        
        i = 0
        while i < seqs.shape[0]:
            #mark our start and seach for the tail marker (aka 1)
            rangeStart = i
            while getBit(endsRead_view, i) == 0:
                inc(i)
            
            #we only act at the end of a range
            rangeDelta = i+1-rangeStart
            setBit(endsWrite_view, i)
            
            #now handle the range, create aux arrays for the subrange
            pairsRevDict = np.zeros((rangeDelta, ), revDictType)
            pairsRevDict_view = pairsRevDict
            pairsSeqID = np.zeros((rangeDelta, ), seqIDType)
            pairsSeqID_view = pairsSeqID
            pairsOffseq = np.zeros((rangeDelta, ), offseqType)
            pairsOffseq_view = pairsOffseq
            
            #copy the values for sorting
            for y in xrange(0, rangeDelta):
                pInd = rangeStart+y
                ind = getIndexOfSeq(offsets_view, seqID[pInd], offseq[pInd]+currK)
                pairsRevDict_view[y] = revDict[ind]
                pairsSeqID_view[y] = seqID[pInd]
                pairsOffseq_view[y] = offseq[pInd]
            
            #argsort it up
            npargsort = np.argsort(pairsRevDict)
            npargsort_view = npargsort
            prevRevDict = pairsRevDict_view[npargsort_view[0]]
            
            #go through the sorted
            for x in xrange(0, npargsort.shape[0]):
                ind = npargsort_view[x]
                if x == ind:
                    #no changes here
                    pass
                else:
                    #make sure we loop again later
                    changesMade = True
                    
                    #update all of the things to be correct
                    writePos = rangeStart+x
                    seqID_view[writePos] = pairsSeqID_view[ind]
                    offseq_view[writePos] = pairsOffseq_view[ind]
                    revDict_view[getIndexOfSeq(offsets_view, pairsSeqID_view[ind], pairsOffseq_view[ind])] = writePos
                
                #check if we need to write out a 1, indicating the end of a k-mer bin
                for z in xrange(prevRevDict, pairsRevDict_view[ind]):
                    if getBit(endsRead_view, z):
                        setBit(endsWrite_view, rangeStart+x-1)
                        break
                
                prevRevDict = pairsRevDict_view[ind]
            
            #increment one past the end of the group
            inc(i)
            
            #skip a bunch of repeat 1's which are indicative of ranges of length 1, which are already completed
            #it would indicate a k-mer that is unique (remember the k is doubling with each iteration)
            #while i < seqs.shape[0] and endsRead_view[i] == 1:
            while i < seqs.shape[0] and getBit(endsRead_view, i):
                setBit(endsWrite_view, i)
                inc(i)
        
        if not ramOnly:
            os.rename(bwtDir+'/ends'+str(currK)+'.npy', bwtDir+'/ends'+str(4*currK)+'.npy')
            
        currK *= 2
        
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] msbwt = np.lib.format.open_memmap(bwtDir+'/msbwt.npy', 'w+', '<u1', (seqs.shape[0], ))
    cdef np.uint8_t [:] msbwt_view = msbwt
    #cdef unsigned long seqLen
    for x in xrange(0, seqs.shape[0]):
        if offseq_view[x] == 0:
            seqLen = offsets_view[seqID_view[x]+1]-offsets_view[seqID_view[x]]
            msbwt_view[x] = getCharOfSeq(seqs_view, offsets_view, seqID_view[x], seqLen-1)
        else:
            msbwt_view[x] = getCharOfSeq(seqs_view, offsets_view, seqID_view[x], offseq_view[x]-1)
    
cdef np.uint8_t getCharOfSeq(np.uint8_t [:] seqs_view, np.uint64_t [:] offsets_view, unsigned long seqID, unsigned long index):
    return seqs_view[getIndexOfSeq(offsets_view, seqID, index)]
    
cdef unsigned long getIndexOfSeq(np.uint64_t [:] offsets_view, unsigned long seqID, unsigned long index):
    #cdef unsigned long l = offsets_view[seqID+1]-offsets_view[seqID]
    #cdef unsigned long i = index % l
    return offsets_view[seqID]+(index % (offsets_view[seqID+1]-offsets_view[seqID]))
    
cdef void setBit(np.uint8_t [:] bitArray, unsigned long index):
    #cdef unsigned long trueIndex = index / 8
    bitArray[index / 8] |= (0x1 << (index % 8))
    
cdef bint getBit(np.uint8_t [:] bitArray, unsigned long index):
    #cdef unsigned long trueIndex = index / 8
    return (bitArray[index / 8] & (0x1 << (index % 8)))