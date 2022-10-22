import sys 
import os  

###############################################
# parse_orthofinder.py 
# Jen Wisecaver
# 20220330 
# input: an Orthogroups.txt file
# output: lists of orthogroup ids for tree building 
################################################

infile = sys.argv[1]
maxzeros = int(sys.argv[2])
maxcount = int(sys.argv[3])

baseout = os.path.dirname(os.path.realpath(infile)) + '/Orthogroups_list'

fi = open(infile)
myDict = {}

filecount = 1
ogcount = 0

for line in fi:
    
    genecounts =  line.rstrip().split('\t')
    og = genecounts.pop(0)
    total = genecounts.pop(-1)
    #print(og,total)
    
    if og == 'Orthogroup':
        continue
        
    genecounts = list(map(int, genecounts))
    zeros = genecounts.count(0)
        
    if zeros <= maxzeros:
        ogcount += 1
        
        if filecount not in myDict:
            myDict[filecount] = set()
            
        myDict[filecount].add(og)
        
        if ogcount >= maxcount:
            ogcount = 0 
            filecount += 1

fi.close()

for filecount in myDict:
    #print(filecount,len(myDict[filecount]))
    outfile = baseout + str(filecount) + '.txt'
    fo = open(outfile, 'w')
    
    for og in myDict[filecount]:
        fo.write(og + '\n')
    
    fo.close()