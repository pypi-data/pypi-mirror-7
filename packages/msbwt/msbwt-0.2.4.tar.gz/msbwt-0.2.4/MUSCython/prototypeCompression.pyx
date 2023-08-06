
import copy
import math
import multiprocessing

import numpy as np
cimport numpy as np

#TODO: what if we initialize the dictionary to have all runs up to length RLE_avg, might make things smaller for most cases

def compressMSBWT(char * inputBwtDir, char * outputBwtDir, unsigned long numProcs=1, bint alwaysReset=True, logger=None):
    '''
    Header format is as follows
    1st Byte = 8-bit integer, x, such that our bins are of 2**x, binBits in the following code segment
    [2-9] bytes = 64 bit MSB integer, y, indicating the total number of bases
    
    '''
    #figure out logging stuff now, then begin the actual compressing
    cdef bint logging = (logger != None)
    if logging:
        logger.info('Compressing \''+inputBwtDir+'\' to \''+outputBwtDir+'\'...')
    
    #helper vars
    cdef unsigned long x
    
    #input
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] uncompressed = np.load(inputBwtDir+'/msbwt.npy', 'r+')
    cdef np.uint8_t [:] uncompressed_view = uncompressed
    cdef unsigned long uncompLen = uncompressed.shape[0]
    
    #bin info
    cdef unsigned long binBits = 13
    cdef unsigned long binSize = 2**binBits
    
    #output file
    if logging:
        logger.info('Writing header...')
    fp = open(outputBwtDir+'/comp_msbwt.dat', 'w+')
    fp.write(chr(binBits))
    for x in range(0, 64, 8):
        fp.write(chr((uncompLen >> (56-x)) & 0xFF))
    
    #output byte offsets
    cdef unsigned long numBins = math.ceil(1.0*uncompressed.shape[0]/binSize)
    cdef unsigned long offsetSize = numBins+1
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] offsetArray = np.lib.format.open_memmap(outputBwtDir+'/comp_offsets.npy', 'w+', '<u8', (offsetSize, ))
    cdef np.uint64_t [:] offsetArray_view = offsetArray
    offsetArray_view[offsetSize-1] = uncompLen
    cdef unsigned long totalOffset = 9
    
    #iterate through each full bin
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] compressedBin
    myDict = None
    if numProcs <= 1 or (not alwaysReset):
        #do every full sized bin
        for x in range(0, uncompressed.shape[0]/binSize):
            if x & 0x3FF == 0 and logging:
                logger.info('Writing bin '+str(x)+'...')
            (compressedBin, myDict) = compressBin((uncompressed[x*binSize:(x+1)*binSize], binSize, myDict))
            fp.write(compressedBin.tostring())
            offsetArray_view[x] = totalOffset
            totalOffset += compressedBin.shape[0]
            
            if alwaysReset:
                myDict = None
    else:
        #this also does every full sized bin
        x = 0
        mp = multiprocessing.Pool(numProcs)
        cIter = compressIterator(uncompressed, uncompLen, binSize)
        ret = mp.imap(compressBin, cIter)
        for (compressedBin, myDict) in ret:
            if x & 0x3FF == 0 and logging:
                logger.info('Writing bin '+str(x)+'...')
            fp.write(compressedBin.tostring())
            offsetArray_view[x] = totalOffset
            totalOffset += compressedBin.shape[0]
            x += 1
        mp.close()
        myDict = None
            
    #check for a small bin at the very end
    cdef unsigned long startFinalBin = (uncompressed.shape[0] >> binBits) << binBits
    if startFinalBin < uncompressed.shape[0]:
        if logging:
            logger.info('Writing final bin...')
        (compressedBin, myDict) = compressBin((uncompressed[startFinalBin:uncompLen], uncompLen-startFinalBin, myDict))
        fp.write(compressedBin.tostring())
        offsetArray_view[offsetArray.shape[0]-2] = totalOffset
        totalOffset += compressedBin.shape[0]
    
    #write the final bin which is basically a total length of everything
    offsetArray_view[offsetArray.shape[0]-1] = totalOffset
    
    if logging:
        logger.info('Finished!')
    fp.close()
    
    if myDict != None:
        return len(myDict)
    else:
        return 0
    
#cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] compressBin(np.uint8_t [:] uncompressed_view, unsigned long uncompLen):
def compressBin(tup):
    #extract the tuple
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] uncompressed = tup[0]
    cdef np.uint8_t [:] uncompressed_view = uncompressed
    cdef unsigned long uncompLen = tup[1]
    passedDict = tup[2]
    
    # Build the dictionary.
    cdef unsigned long dict_size = 6
    cdef unsigned long x
    cdef dict dictionary = {}
    for x in range(0, dict_size):
        dictionary[(x, )] = x
    
    if passedDict != None:
        dictionary = passedDict
    
    cdef unsigned long bitsPerSymbol = 1
    cdef unsigned long numPatterns = 2
    while numPatterns < dict_size:
        numPatterns *= 2
        bitsPerSymbol += 1
    
    cdef unsigned long currByte = 0
    cdef long currByteUse = 0
    
    cdef tuple w = ()
    cdef tuple wc
    cdef unsigned long c
    
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] result = np.empty(dtype='<u1', shape=(uncompLen, ))
    cdef unsigned long resultLength = 0
    
    for x in range(0, uncompLen):
        c = uncompressed_view[x]
        wc = w+(c, )
        if wc in dictionary:
            w = wc
        else:
            currByte += (dictionary[w] << currByteUse)
            currByteUse += bitsPerSymbol
            while currByteUse >= 8:
                result[resultLength] = currByte & 0xFF
                resultLength += 1
                currByte = currByte >> 8
                currByteUse -= 8
            
            # Add wc to the dictionary.
            dictionary[wc] = dict_size
            dict_size += 1
            
            if dict_size > numPatterns:
                numPatterns *= 2
                bitsPerSymbol += 1
            
            w = (c, )
 
    # Output the code for w.
    currByte += (dictionary[w] << currByteUse)
    currByteUse += bitsPerSymbol
    while currByteUse > 0:
        result[resultLength] = currByte & 0xFF
        resultLength += 1
        currByte = currByte >> 8
        currByteUse -= 8
    
    return (result[0:resultLength], dictionary)

def compressIterator(np.ndarray uncompressed, unsigned long uncompressedLen, unsigned long binSize):
    cdef unsigned long x
    for x in range(0, uncompressedLen/binSize):
        yield (uncompressed[x*binSize:(x+1)*binSize], binSize, None)


def decompressMSBWT(char * inputBwtDir, char * outputBwtDir, numProcs=1, logger=None):
    #figure out logging stuff now, then begin the actual decompressing
    cdef bint logging = (logger != None)
    if logging:
        logger.info('Decompressing \''+inputBwtDir+'\' to \''+outputBwtDir+'\'...')
    
    #helper vars
    cdef unsigned long x, y, z
    
    #input
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] compressed = np.memmap(inputBwtDir+'/comp_msbwt.dat', dtype='<u1', mode='r+')
    cdef np.uint8_t [:] compressed_view = compressed
    
    #bin info
    cdef unsigned long binBits = compressed_view[0]
    cdef unsigned long binSize = 2**binBits
    
    cdef unsigned long uncompLen = 0
    for x in range(1, 9):
        uncompLen = uncompLen << 8
        uncompLen += compressed_view[x]
    
    #output file
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] uncompressed = np.lib.format.open_memmap(outputBwtDir+'/msbwt.npy', 'w+', '<u1', (uncompLen, ))
    cdef np.uint8_t [:] uncompressed_view = uncompressed
    
    #output byte offsets
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] offsetArray = np.load(inputBwtDir+'/comp_offsets.npy', 'r+')
    cdef np.uint64_t [:] offsetArray_view = offsetArray
    cdef unsigned long totalSymbols = 0
    
    #iterate through each full bin
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] decompressedBin
    cdef np.uint8_t [:] decompressedBin_view
    if numProcs <= 1:
        for x in range(0, offsetArray.shape[0]-1):
            if x & 0x3FF == 0 and logging:
                logger.info('Writing bin '+str(x)+'...')
            decompressedBin = decompressBin((compressed[offsetArray_view[x]:offsetArray_view[x+1]], binSize))
            decompressedBin_view = decompressedBin
            z = x*binSize
            for y in range(0, binSize):
                uncompressed_view[z] = decompressedBin_view[y]
                z += 1 
            #uncompressed[x*binSize:(x+1)*binSize] = decompressedBin[:]
    else:
        x = 0
        mp = multiprocessing.Pool(numProcs)
        cIter = decompressIterator(compressed, offsetArray_view, offsetArray.shape[0], binSize)
        ret = mp.imap(decompressBin, cIter)
        for decompressedBin in ret:
            if x & 0x3FF == 0 and logging:
                logger.info('Writing bin '+str(x)+'...')
            decompressedBin_view = decompressedBin
            z = x*binSize
            for y in range(0, binSize):
                uncompressed_view[z] = decompressedBin_view[y]
                z += 1
            #uncompressed[x*binSize:(x+1)*binSize] = decompressedBin[:]
            x += 1
        mp.close()
            
    #check for a small bin at the very end
    #cdef unsigned long startFinalBin = offsetArray_view[offsetArray.shape[0]-1]
    #if (offsetArray.shape[0]*binSize) < uncompressed.shape[0]:
    if logging:
        logger.info('Writing final bin...')
    cdef unsigned long finalStart = offsetArray[offsetArray.shape[0]-1]
    cdef unsigned long lastBinSize = uncompLen-(offsetArray.shape[0]-1)*binSize
    decompressedBin = decompressBin((compressed[finalStart:], lastBinSize))
    decompressedBin_view = decompressedBin
    z = (offsetArray.shape[0]-1)*binSize
    for y in range(0, lastBinSize):
        uncompressed_view[z] = decompressedBin_view[y]
        z += 1
    #uncompressed[(offsetArray.shape[0]-1)*binSize:] = decompressedBin[:]
    
    if logging:
        logger.info('Finished!')
    
def decompressBin(tup):
    #extract inputs
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] compressed = tup[0]
    cdef np.uint8_t [:] compressed_view = compressed
    cdef unsigned long knownLength = tup[1]
    
    # Build the dictionary.
    cdef unsigned long dict_size = 6
    cdef unsigned long numSymbols = dict_size
    
    cdef np.ndarray[np.uint16_t, ndim=1, mode='c'] lookupList = np.empty(dtype='<u2', shape=(dict_size+knownLength, ))
    cdef np.uint16_t [:] lookupList_view = lookupList
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] symbolList = np.empty(dtype='<u1', shape=(dict_size+knownLength, ))
    cdef np.uint8_t [:] symbolList_view = symbolList
    
    cdef unsigned long x
    for x in range(0, dict_size):
        lookupList_view[x] = x
        symbolList_view[x] = x
    
    cdef unsigned long bitsPerSymbol = 1
    cdef unsigned long numPatterns = 2
    while numPatterns < dict_size:
        numPatterns *= 2
        bitsPerSymbol += 1
    
    #print compressed
    cdef unsigned long currByte = compressed_view[0]
    cdef unsigned long compressedIndex = 1
    cdef long currByteUse = 8
    
    cdef list w = [currByte & (0xFF >> (8-bitsPerSymbol))]
    currByteUse -= bitsPerSymbol
    currByte = currByte >> bitsPerSymbol
    
    cdef list result = copy.deepcopy(w)
    cdef unsigned long prevK = w[0]
    
    #for k in compressed:
    while len(result) < knownLength:
        while currByteUse < bitsPerSymbol:
            #currByte += (compressed.pop(0) << currByteUse)
            currByte += ((<unsigned long>compressed_view[compressedIndex]) << currByteUse)
            compressedIndex += 1
            currByteUse += 8
        
        k = currByte & (0xFFFFFF >> (24-bitsPerSymbol))
        currByteUse -= bitsPerSymbol
        currByte = currByte >> bitsPerSymbol
        
        #if k in dictionary:
            #entry = dictionary[k]
        if k < dict_size:
            entry = []
            z = k
            while z >= numSymbols:
                entry.insert(0, symbolList[z])
                z = lookupList[z]
            entry.insert(0, symbolList[z])
            
        elif k == dict_size:
            entry = w + [w[0]]
        else:
            raise ValueError('Bad compressed k: %s' % k)
        result += entry
 
        # Add w+entry[0] to the dictionary.
        #dictionary[dict_size] = w + entry[0:1]
        #symbolList.append(entry[0])
        #lookupList.append(prevK)
        symbolList[dict_size] = entry[0]
        lookupList[dict_size] = prevK
        dict_size += 1
        
        if dict_size >= numPatterns:
            numPatterns *= 2
            bitsPerSymbol += 1
 
        w = entry
        prevK = k
    
    #print 'dict_size', dict_size
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] ret = np.array(result, dtype='<u1')[0:knownLength]
    return ret

def decompressIterator(np.ndarray compressed, np.uint64_t [:] offsetArray_view, unsigned long offsetArrayLen, unsigned long binSize):
    cdef unsigned long x
    for x in range(0, offsetArrayLen-1):
        yield (compressed[offsetArray_view[x]:offsetArray_view[x+1]], binSize)