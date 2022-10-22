#!/usr/bin/env python
from datetime import date
import requests

today = date.today()
today = today.strftime("%b-%d-%Y")


##### Get list of KEGG orthology IDs (KOs) ##### 
ko_list_url = 'http://rest.kegg.jp/list/ko'
koDict = {}

ko_desc_file = 'KEGG_KO_DESC_' + today + '.txt'
fo = open(ko_desc_file, 'w')

resp = requests.get(ko_list_url)
for line in resp.text.split('\n'):
    #print(line)
    col = line.split('\t')
    if len(col) != 2:
        continue
        
    ko = line.split('\t')[0].split(':')[1]
    koDesc = line.split('\t')[1]
    #print(ko,koDesc)
    koDict[ko] = koDesc
    fo.write(ko + '\t' + koDesc + '\n')
    
#print(koDict['K00004'])
fo.close()

 
##### Get list of KEGG modules (MODs) ##### 
mod_list_url = 'http://rest.kegg.jp/list/module'
modDict = {}

mod_desc_file = 'KEGG_MODULE_DESC_' + today + '.txt'
fo = open(mod_desc_file, 'w')

resp = requests.get(mod_list_url)
for line in resp.text.split('\n'):
    #print(line)
    col = line.split('\t')
    if len(col) != 2:
        continue
        
    mod = line.split('\t')[0].split(':')[1]
    modDesc = line.split('\t')[1]
    #print(mod,modDesc)
    modDict[mod] = modDesc
    
    fo.write(mod + '\t' + modDesc + '\n')

#print(modDict['M00004'])
fo.close()


##### Get list of KEGG pathways (PATHs) ##### 
path_list_url = 'http://rest.kegg.jp/list/pathway'
pathDict = {}

path_desc_file = 'KEGG_PATHWAY_DESC_' + today + '.txt'
fo = open(path_desc_file, 'w')

resp = requests.get(path_list_url)
for line in resp.text.split('\n'):
    #print(line)
    col = line.split('\t')
    if len(col) != 2:
        continue
        
    path = line.split('\t')[0].split(':')[1]
    pathDesc = line.split('\t')[1]
    #print(path,pathDesc)
    pathDict[path] = pathDesc
    
    fo.write(path + '\t' + pathDesc + '\n')

#print(pathDict['map00040'])
fo.close()


#####  Link KOs to PATHs and MODs ##### 
# example link ko to path: http://rest.kegg.jp/link/ko/map00010
# example link ko to mod: http://rest.kegg.jp/link/ko/M00939
# example link mod to path: http://rest.kegg.jp/link/module/map00010
ko2pathDict = {}
path2koDict = {}

for path in pathDict:
    if path not in path2koDict:
        path2koDict[path] = set()
        
    #print(path)
    ko2path_url = "http://rest.kegg.jp/link/ko/" + path
    #print(ko2path_url)
    
    resp = requests.get(ko2path_url)
    for line in resp.text.split('\n'):
        #print(line)

        col = line.split('\t')
        if len(col) != 2:
            continue
        
        path = col[0].split(':')[1]
        ko = col[1].split(':')[1]
        #print(path, ko)
        
        if ko not in ko2pathDict:
            ko2pathDict[ko] = set()
        
        ko2pathDict[ko].add(path)
        path2koDict[path].add(ko)


ko2path_file = 'KEGG_KO_to_PATHWAY_' + today + '.txt'
fo = open(ko2path_file, 'w')

for ko in ko2pathDict:
    pathways = ','.join(ko2pathDict[ko])
    fo.write(ko + '\t' + pathways + '\n')

fo.close()


path2ko_file = 'KEGG_PATHWAY_to_KO_' + today + '.txt'
fo = open(path2ko_file, 'w')

for path in path2koDict:
    kos = ','.join(path2koDict[path])
    fo.write(path + '\t' + kos + '\n')

fo.close()


ko2modDict = {}
mod2koDict = {}

for mod in modDict:
    if mod not in mod2koDict:
        mod2koDict[mod] = set()
        
    #print(mod)
    ko2mod_url = "http://rest.kegg.jp/link/ko/" + mod
    #print(ko2mod_url)
    
    resp = requests.get(ko2mod_url)
    for line in resp.text.split('\n'):
        #print(line)

        col = line.split('\t')
        if len(col) != 2:
            continue
        
        mod = col[0].split(':')[1]
        ko = col[1].split(':')[1]
        #print(mod, ko)
        
        if ko not in ko2modDict:
            ko2modDict[ko] = set()
        
        ko2modDict[ko].add(mod)
        mod2koDict[mod].add(ko)


ko2mod_file = 'KEGG_KO_to_MODULES_' + today + '.txt'
fo = open(ko2mod_file, 'w')

for ko in ko2modDict:
    modules = ','.join(ko2modDict[ko])
    fo.write(ko + '\t' + modules + '\n')

fo.close()


mod2ko_file = 'KEGG_MODULE_to_KO_' + today + '.txt'
fo = open(mod2ko_file, 'w')

for mod in mod2koDict:
    kos = ','.join(mod2koDict[mod])
    fo.write(mod + '\t' + kos + '\n')

fo.close()

#####  Get KEGG BRITE pathway heirarchy ##### 
# List of all brite heirarchies: http://rest.kegg.jp/list/brite
path2briteDict = {}

brite_url = 'http://rest.kegg.jp/get/br:br08901'
resp = requests.get(brite_url)

catA = ''
catB = ''

for line in resp.text.split('\n'):
    if len(line) == 0:
        continue
        
    if line[0] == '+' or line[0] == '!' or line[0] == '#':
        continue
    #print(line)
    
    if line[0] == 'A':
        catA = line[1:]
        #print(catA)
    
    if line[0] == 'B':
        catB = line[3:]
        #print(catB)
        
    if line[0] == 'C':
        path = 'map' + line[5:10]
        if catA == 'Organismal Systems' or catA == 'Human Diseases' or catA == 'Drug Development':
            continue
        if catB == 'Global and overview maps':
            continue
        
        #print(path,catA,catB)
        path2briteDict[path] = [catA, catB]
    
outfile = 'KEGG_KO_ALL_PARENTS_' + today + '.txt'
fo = open(outfile, 'w')

for ko in koDict:
    catSetA = set()
    catSetB = set()
    #print(ko)
    fo.write(ko + ':')
        
    if ko in ko2modDict:
        for mod in ko2modDict[ko]:
            #print('\t',mod)
            fo.write('\t' + mod)

    if ko in ko2pathDict:
        for path in ko2pathDict[ko]:
            if path in path2briteDict:
                catSetA.add(path2briteDict[path][0])
                catSetB.add(path2briteDict[path][1])
                #print('\t',path)
                fo.write('\t' + path)
    
    for cat in catSetB:
        #print('\t',cat)
        fo.write('\t' + cat)

    for cat in catSetA:
        #print('\t',cat)
        fo.write('\t' + cat)
    
    fo.write('\n')
        
fo.close()

