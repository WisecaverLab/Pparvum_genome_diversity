#!/depot/jwisecav/apps/envs/env.genomics/bin/python
import sys 
import os  
import ete3
from ete3 import Tree
from ete3 import Tree, TreeStyle
from ete3 import PhyloTree

###############################################
# mpr_tree.py 
# Jen Wisecaver
# 20220330
# input: a tree in newick format
# output: a midpoint rooted tree in newick format
################################################

file = sys.argv[1]

tredir = os.path.dirname(os.path.realpath(file))
og = file.split('/')[-1].split('.')[0]
otre = tredir + '/'+ og + '.mpr.tree'

t = PhyloTree(file, sp_naming_function=None)
R = t.get_midpoint_outgroup()
t.set_outgroup(R)

t.write(outfile = otre)

