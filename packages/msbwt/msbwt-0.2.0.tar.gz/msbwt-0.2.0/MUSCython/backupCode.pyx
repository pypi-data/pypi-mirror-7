def createMsbwtFromSeqs(bwtDir, unsigned int numProcs, logger):
    '''
    This function assumes the strings are all uniform length and that that uniform length is the
    values stored in offsetFN
    @param seqFNPrefix - the prefix of the sequence files
    @param offsetFN - a file containing offset information, should just be one value for this func
    @param numProcs - number of processes to use
    @param logger - a logger to dump output to
    '''
    #timing metrics, only for logging
    cdef double st, et, stc, etc, totalStartTime, totalEndTime
    st = time.time()
    totalStartTime = st
    stc = time.clock()
    
    #hardcoded values
    cdef unsigned int numValidChars = 6
    
    #clear anything that may already have been associated with our directory
    clearAuxiliaryData(bwtDir)
    
    #construct pre-arranged file names, God forbid we ever change these...
    bwtFN = bwtDir+'/msbwt.npy'
    seqFNPrefix = bwtDir+'/seqs.npy'
    offsetFN = bwtDir+'/offsets.npy'
    
    #offsets is really just storing the length of all string at this point
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] offsets = np.load(offsetFN, 'r+')
    cdef unsigned long seqLen = offsets[0]
    
    #finalSymbols stores the last real symbols in the strings (not the '$', the ones right before)
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] finalSymbols = np.load(seqFNPrefix+'.1.npy', 'r+')
    cdef np.uint8_t [:] finalSymbols_view = finalSymbols
    cdef unsigned long numSeqs = finalSymbols.shape[0]
    
    logger.warning('Beta version of Cython creation')
    logger.info('Preparing to merge '+str(numSeqs)+' sequences...')
    logger.info('Generating level 1 insertions...')
    
    #1 - load <DIR>/seqs.npy.<seqLen-2>.npy, these are the characters before the '$'s
    #    use them as the original inserts storing <insert position, insert character, sequence ID>
    #    note that inserts should be stored in a minimum of 6 files, one for each character
    initialInsertsFN = bwtDir+'/inserts.initial.npy'
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] initialInserts = np.lib.format.open_memmap(initialInsertsFN, 'w+', '<u8', (numSeqs, 3))
    cdef np.uint64_t [:, :] initialInserts_view = initialInserts
    
    #some basic counting variables
    cdef unsigned long i, c, columnID, c2
    
    #this will still the initial counts of symbols in the final column of our strings
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] initialFmDeltas = np.zeros(dtype='<u8', shape=(numValidChars, ))
    cdef np.uint64_t [:] initialFmDeltas_view = initialFmDeltas
    
    with nogil:
        for i in range(0, numSeqs):
            #index to insert, symbol, sequence
            initialInserts_view[i][0] = i
            initialInserts_view[i][1] = finalSymbols_view[i]
            initialInserts_view[i][2] = i
            inc(initialFmDeltas_view[finalSymbols_view[i]])
    
    #fmStarts is basically an fm-index offset, fmdeltas tells us how much fmStarts should change each iterations
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] fmStarts = np.zeros(dtype='<u8', shape=(numValidChars, numValidChars))
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] fmDeltas = np.zeros(dtype='<u8', shape=(numValidChars, numValidChars))
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] fmEnds = np.zeros(dtype='<u8', shape=(numValidChars, numValidChars))
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] nextFmDeltas
    fmDeltas[0][:] = initialFmDeltas[:]
    
    #figure out the files we insert in each iteration
    insertionFNDict = {}
    nextInsertionFNDict = {}
    for c in range(0, numValidChars):
        #create an initial empty region for each symbol
        #np.lib.format.open_memmap(bwtDir+'/state.'+str(c)+'.0.npy', 'w+', '<u1', (0, ))
        #np.memmap(bwtDir+'/state.'+str(c)+'.0.npy', '<u1', 'w+', shape=(0, ))
        
        #create an empty list of files for insertion
        insertionFNDict[c] = []
        nextInsertionFNDict[c] = []
        
    #add the single insertion file we generated earlier
    insertionFNDict[0].append(initialInsertsFN)
    
    etc = time.clock()
    et = time.time()
    logger.info('Finished init in '+str(et-st)+' seconds.')
    logger.info('Beginning iterations...')
    
    #2 - go back one column at a time, building new inserts
    for columnID in range(0, seqLen):
        st = time.time()
        stc = time.clock()
        
        #first take into accoun the new fmDeltas coming in from all insertions
        fmStarts = fmStarts+(np.cumsum(fmDeltas, axis=0)-fmDeltas)
        fmEnds = fmEnds+np.cumsum(fmDeltas, axis=0)
        
        #clear out the next fmDeltas
        nextFmDeltas = np.zeros(dtype='<u8', shape=(numValidChars, numValidChars))
        
        for c in range(0, numValidChars):
            currentSymbolFN = bwtDir+'/state.'+str(c)+'.'+str(columnID)+'.npy'
            nextSymbolFN = bwtDir+'/state.'+str(c)+'.'+str(columnID+1)+'.npy'
            nextSeqFN = seqFNPrefix+'.'+str((columnID+2) % seqLen)+'.npy'
            tup = (c, np.copy(fmStarts[c]), np.copy(fmDeltas[c]), np.copy(fmEnds[c]), insertionFNDict[c], currentSymbolFN, nextSymbolFN, bwtDir, columnID, nextSeqFN)
            ret = iterateMsbwtCreate(tup)
            
            #update the fmDeltas
            nextFmDeltas = nextFmDeltas + ret[0]
            
            #update our insertions files
            for c2 in range(0, numValidChars):
                if ret[1][c2] == None:
                    #no new file
                    pass
                else:
                    nextInsertionFNDict[c2].append(ret[1][c2])
        
        #remove the old insertions and old state files
        for c in insertionFNDict:
            for fn in insertionFNDict[c]:
                try:
                    os.remove(fn)
                except:
                    logger.warning('Failed to remove \''+fn+'\' from file system.')
            
            if len(insertionFNDict[c]) > 0:
                try:
                    rmStateFN = bwtDir+'/state.'+str(c)+'.'+str(columnID)+'.npy'
                    os.remove(rmStateFN)
                except:
                    logger.warning('Failed to remove\''+rmStateFN+'\' from file system.')
        
        #copy the fmDeltas and insertion filenames
        fmDeltas[:] = nextFmDeltas[:]
        insertionFNDict = nextInsertionFNDict
        nextInsertionFNDict = {}
        for c in range(0, numValidChars):
            nextInsertionFNDict[c] = []
        
        etc = time.clock()
        et = time.time()
        logger.info('Finished iteration '+str(columnID+1)+' in '+str(et-st)+' seconds('+str(etc-stc)+' clock)...')
    
    logger.info('Creating final output...')
    
    #finally, join all the subcomponent
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] tempBWT
    cdef np.uint8_t [:] tempBWT_view
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] finalBWT
    cdef np.uint8_t [:] finalBWT_view
    
    cdef unsigned long totalLength = 0
    for c in range(0, numValidChars):
        #tempBWT = np.load(bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy', 'r')
        stateFN = bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy'
        if os.path.exists(stateFN):
            tempBWT = np.memmap(stateFN, '<u1', 'r')
            totalLength += tempBWT.shape[0]
    
    #prepare the final structure for copying
    cdef unsigned long finalInd = 0
    cdef unsigned long tempLen
    finalBWT = np.lib.format.open_memmap(bwtFN, 'w+', '<u1', (totalLength, ))
    finalBWT_view = finalBWT
    
    for c in range(0, numValidChars):
        stateFN = bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy'
        if os.path.exists(stateFN):
            #tempBWT = np.load(bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy', 'r+')
            tempBWT = np.memmap(stateFN, '<u1', 'r+')
        else:
            continue
        tempBWT_view = tempBWT
        tempLen = tempBWT.shape[0]
        
        with nogil:
            for i in range(0, tempLen):
                finalBWT_view[finalInd] = tempBWT_view[i]
                inc(finalInd)
    
    #finally, clear the last state files
    tempBWT = None
    for c in range(0, numValidChars):
        for fn in insertionFNDict[c]:
            try:
                os.remove(fn)
            except:
                logger.warning('Failed to remove \''+fn+'\' from file system.')
        
        try:
            if os.path.exists(bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy'):
                os.remove(bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy')
        except:
            logger.warning('Failed to remove \''+bwtDir+'/state.'+str(c)+'.'+str(seqLen)+'.npy'+'\' from file system.')
    
    logger.info('Final output saved to \''+bwtFN+'\'.')
    totalEndTime = time.time()
    logger.info('Finished all iterations in '+str(totalEndTime-totalStartTime)+' seconds.')
            
def iterateMsbwtCreate(tup):
    '''
    This function will perform the insertion iteration for a single symbol grouping
    '''
    #extract our inputs from the tuple
    cdef np.uint8_t idChar
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] fmIndex
    cdef np.uint64_t [:] fmIndex_view
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] fmEndex
    cdef np.uint64_t [:] fmEndex_view
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] prevFmDelta
    cdef np.uint64_t [:] prevFmDelta_view
    cdef unsigned long column
    (idChar, fmIndex, prevFmDelta, fmEndex, insertionFNs, currentSymbolFN, nextSymbolFN, bwtDir, column, nextSeqFN) = tup
    fmIndex_view = fmIndex
    fmEndex_view = fmEndex
    prevFmDelta_view = prevFmDelta
    
    #hardcoded
    cdef unsigned int numValidChars = 6
    
    #this stores the number of symbols we find in our range
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] fmDeltas = np.zeros(dtype='<u8', shape=(numValidChars, numValidChars))
    cdef np.uint64_t [:, :] fmDeltas_view = fmDeltas
    
    #the input partial BWT for suffixes starting with 'idChar'
    #cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] currentBwt = np.load(currentSymbolFN, 'r+')
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] currentBwt
    if os.path.exists(currentSymbolFN):
        currentBwt = np.memmap(currentSymbolFN, '<u1', 'r+')
    else:
        currentBwt = np.zeros(dtype='<u1', shape=(0, ))
    cdef np.uint8_t [:] currentBwt_view = currentBwt
    
    #the output partial BWT for suffixes starting with 'idChar'
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] nextBwt
    cdef np.uint8_t [:] nextBwt_view
    
    #currentBWT + inserts = nextBWT
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] inserts
    cdef np.uint64_t [:, :] inserts_view
    
    #counting variables
    cdef unsigned long currIndex, insertLen, insertIndex, prevIndex, totalNewLen
    cdef unsigned long i, j
    cdef np.uint8_t c, symbol, nextSymbol
    
    #These values contain the numpy arrays for the new inserts, created below
    outputInserts = []
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] outputInsertPointers = np.zeros(dtype='<u8', shape=(numValidChars, ))
    cdef np.uint64_t [:] outputInsertPointers_view = outputInsertPointers
    cdef np.uint64_t * outputInsert_p
    
    #these indices will be used for knowing where we are in the outputs
    cdef np.ndarray[np.uint64_t, ndim=1, mode='c'] outputInsertIndices = np.zeros(dtype='<u8', shape=(numValidChars, ))
    cdef np.uint64_t [:] outputInsertIndices_view = outputInsertIndices
    cdef np.uint64_t ind
    
    #these are temp array used to extract pointers
    cdef np.ndarray[np.uint64_t, ndim=2, mode='c'] newInsertArray
    cdef np.uint64_t [:, :] newInsertArray_view
    
    #the symbols we are noting as being inserted next
    cdef np.ndarray[np.uint8_t, ndim=1, mode='c'] currSeqs = np.load(nextSeqFN, 'r+')
    cdef np.uint8_t [:] currSeqs_view = currSeqs
    
    retFNs = [None]*numValidChars
    
    if len(insertionFNs) == 0:
        #we don't need to do anything except rename our file
        #print str(idChar)+', No change'
        if os.path.exists(currentSymbolFN):
            os.rename(currentSymbolFN, nextSymbolFN)
    else:
        #first we need to count how big the new iteration is
        totalInsertionCounts = np.sum(prevFmDelta)
        #nextBwt = np.zeros(dtype='<u1', shape=(currentBwt.shape[0]+totalInsertionCounts, ))
        totalNewLen = currentBwt.shape[0]+totalInsertionCounts
        #nextBwt = np.lib.format.open_memmap(nextSymbolFN, 'w+', '<u1', (totalNewLen, ))
        #nextBwt = np.memmap(nextSymbolFN, '<u1', 'w+', shape=(totalNewLen, ))
        if os.path.exists(currentSymbolFN):
            #extend the file
            fp = open(currentSymbolFN, 'r+')
            #fp.write('\x00'*totalInsertionCounts)
            fp.seek(totalNewLen-1)
            fp.write('\x00')
            fp.close()
            nextBwt = np.memmap(currentSymbolFN, '<u1', 'r+')
        else:
            nextBwt = np.memmap(currentSymbolFN, '<u1', 'w+', shape=(totalNewLen, ))
        nextBwt_view = nextBwt
        
        #allocate a numpy array for each new insert file
        for c in range(0, numValidChars):
            if prevFmDelta[c] == 0:
                #nothing to insert from c
                outputInserts.append(None)
            else:
                #add the insert to our return
                newInsertFN = bwtDir+'/inserts.'+str(c)+str(idChar)+'.'+str(column+1)+'.npy'
                retFNs[c] = newInsertFN
                
                #create the insert file, store pointers
                newInsertArray = np.lib.format.open_memmap(newInsertFN, 'w+', '<u8', (prevFmDelta[c], 3))
                newInsertArray_view = newInsertArray
                outputInserts.append(newInsertArray)
                outputInsertPointers_view[c] = <np.uint64_t> &(newInsertArray_view[0][0])
                outputInsertIndices_view[c] = prevFmDelta[c]*3
        
        #now build the iteration, we'll start at zero obviously
        #prevIndex = 0
        #currIndex = 0
        prevIndex = totalNewLen
        currIndex = currentBwt.shape[0]
        
        #go through each file, one at a time
        #for fn in insertionFNs:
        for fn in insertionFNs[::-1]:
            #load the actual inserts
            inserts = np.load(fn, 'r+')
            inserts_view = inserts
            insertLen = inserts.shape[0]
            
            with nogil:
                #go through each insert
                for i in range(0, insertLen):
                    #get the position of the new insert
                    #insertIndex = inserts_view[i][0]
                    insertIndex = inserts_view[insertLen-i-1][0]
                    
                    #just copy up to that position
                    '''
                    for j in range(prevIndex, insertIndex):
                        symbol = currentBwt_view[currIndex]
                        nextBwt_view[j] = symbol
                        
                        inc(fmIndex_view[symbol])
                        inc(currIndex)
                    '''
                    for j in range(prevIndex-1, insertIndex, -1):
                        currIndex -= 1
                        symbol = currentBwt_view[currIndex]
                        nextBwt_view[j] = symbol
                        fmEndex_view[symbol] -= 1
                    
                    #now we actually write the value from the insert
                    #symbol = inserts_view[i][1]
                    symbol = inserts_view[insertLen-i-1][1]
                    nextBwt_view[insertIndex] = symbol
                    
                    #nextSymbol = currSeqs_view[inserts_view[i][2]]
                    nextSymbol = currSeqs_view[inserts_view[insertLen-i-1][2]]
                    inc(fmDeltas_view[symbol][nextSymbol])
                    #prevIndex = insertIndex+1
                    prevIndex = insertIndex
                    
                    #now we need to add the information for our next insertion
                    outputInsert_p = <np.uint64_t *> outputInsertPointers_view[symbol]
                    outputInsertIndices[symbol] -= 3
                    ind = outputInsertIndices[symbol]
                    #outputInsertIndices[symbol] += 3
                    
                    #finally, store the values
                    #outputInsert_p[ind] = fmIndex_view[symbol]
                    #inc(fmIndex_view[symbol])
                    fmEndex_view[symbol] -= 1
                    outputInsert_p[ind] = fmEndex_view[symbol]
                    outputInsert_p[ind+1] = nextSymbol
                    #outputInsert_p[ind+2] = inserts_view[i][2]
                    outputInsert_p[ind+2] = inserts_view[insertLen-i-1][2]
                
        with nogil:
            #at the end we need to copy all values that come after the final insert
            '''
            for j in range(prevIndex, totalNewLen):
                symbol = currentBwt_view[currIndex]
                nextBwt_view[j] = symbol
                
                inc(fmIndex_view[symbol])
                inc(currIndex)
            '''
            for j in range(prevIndex, 0, -1):
                #currIndex -= 1
                symbol = currentBwt_view[j-1]
                nextBwt_view[j-1] = symbol
                #fmEndex_view[symbol] -= 1
        
        os.rename(currentSymbolFN, nextSymbolFN)
                
    #print currentBwt
    #print nextBwt
    ret = (np.copy(fmDeltas), retFNs)
    return ret