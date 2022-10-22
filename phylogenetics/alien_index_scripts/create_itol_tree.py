import sys
import re
import os
import glob
import textwrap
import subprocess
from collections import OrderedDict

import ete3
from ete3 import Tree
from ete3 import Tree, TreeStyle
from ete3 import PhyloTree

def runCMD(cmd):
    val = subprocess.Popen(cmd, shell=True).wait()

    if val == 0:
        pass
    else:
        print ('command failed')
        print (cmd)
        sys.exit(1)

#Create function for returning the lineage string for a given taxonomy id
def taxdump(taxid):
    root = ''
    taxlist = []
    
    while root == '':
        if taxid == '':
            root = '1'
        elif taxid == '1':
            root = '1'
        else: 
            taxlist.append(taxid)
            taxid = taxnodes[taxid]
            
    return taxlist

###############################
###############################
###############################

# Specify starting variables here
treefile = sys.argv[1]
scriptsdir = sys.argv[2]
itolproject = sys.argv[3]
itolid = sys.argv[4]
colorscheme = sys.argv[5]
support_threshold = sys.argv[6]

taxdir = sys.argv[7]
nodefile = taxdir + '/nodes.dmp'
mergedfile = taxdir + '/merged.dmp'

uploader = scriptsdir + '/iTOL_uploader.pl'
downloader = scriptsdir + '/iTOL_downloader.pl'

lineages_colors_file = scriptsdir + '/lineage_colors.dmp'

query = re.sub('\.\w+$', '', treefile)

print('Creating itol tree for query: ', query)
ofil1 = query + '.itolcolor.txt'
ofil2 = query + '.itolfont.txt'

###############################
###############################
###############################

#Initialize the taxonomy dictionary
taxnodes = {}
fi = open(nodefile)
for line in fi:
    line = line.rstrip('\n').split('\t')
    node, parent = line[0], line[2]
    taxnodes[node] = parent
fi.close()

fi = open(mergedfile)
for line in fi:
    line = line.rstrip('\n').split('\t')
    node, newnode = line[0], line[2]
    taxnodes[node] = taxnodes[newnode]
fi.close()


#Read in the lineages colors file and store in dictionaries 
orderDict = {}
colorDict = {}
lineages = {}
fi = open(lineages_colors_file)

for line in fi:
    line = line.rstrip('\n').split('\t')
    
    if line[3] == colorscheme:
        order, taxid_list, name, color = line[0], line[5], line[4], line[2]
        #print(order, name, color, taxid_list)
        orderDict[name] = int(order)
        colorDict[name] = color
        
        for taxid in taxid_list.split(','):
            #print(taxid, name)
            lineages[taxid] = name
            
fi.close()

# Write the itol header information for the colorstrip dataset.
# This file will tell itol how to color the tree

fo1 = open(ofil1,"w+")

fo1.write('''DATASET_COLORSTRIP
#In colored strip datasets, each ID is associated to a color box/strip and can have an optional label. Color can be specified in hexadecimal, RGB or RGBA notation. When using RGB or RGBA notation, you cannot use COMMA as the dataset separator

#lines starting with a hash are comments and ignored during parsing

#=================================================================#
#                    MANDATORY SETTINGS                           #
#=================================================================#
#select the separator which is used to delimit the data below (TAB,SPACE or COMMA).This separator must be used throughout this file (except in the SEPARATOR line, which uses space).

#SEPARATOR TAB
#SEPARATOR COMMA
SEPARATOR SPACE

#label is used in the legend table (can be changed later)
DATASET_LABEL Taxonomy

#dataset color (can be changed later)
COLOR #000000

#=================================================================#
#                    OPTIONAL SETTINGS                            #
#=================================================================#

#If COLOR_BRANCHES is set to 1, branches of the tree will be colored according to the colors of the strips above the leaves.
#When all children of a node have the same color, it will be colored the same, ie. the color will propagate inwards towards the root.
COLOR_BRANCHES 1

#each dataset can have a legend, which is defined below
#for each row in the legend, there should be one shape, color and label
#shape should be a number between 1 and 5:
#1: square
#2: circle
#3: star
#4: right pointing triangle
#5: left pointing triangle

LEGEND_TITLE Taxonomy
''')

shapeline = "LEGEND_SHAPES ";
colorline = "LEGEND_COLORS ";
labelline = "LEGEND_LABELS ";

for name in OrderedDict(sorted(orderDict.items(), key=lambda x: x[1])):
    #print(name, orderDict[name], colorDict[name])
    shapeline = shapeline + ' 1'
    colorline = colorline + ' ' + colorDict[name]
    labelline = labelline + ' ' + name

fo1.write(shapeline + '\n' + colorline + '\n' + labelline + '\n')
fo1.write('''    
#=================================================================#
#     all other optional settings can be set or changed later     #
#           in the web interface (under 'Datasets' tab)           #
#=================================================================#

#width of the colored strip
STRIP_WIDTH 50

#left margin, used to increase/decrease the spacing to the next dataset. Can be negative, causing datasets to overlap.
#MARGIN 5

#border width; if set above 0, a border of specified width (in pixels) will be drawn around the color strip 
#BORDER_WIDTH 2

#border color; used when BORDER_WIDTH is above 0
#BORDER_COLOR #969696

#always show internal values; if set, values associated to internal nodes will be displayed even if these nodes are not collapsed. It could cause overlapping in the dataset display.
#SHOW_INTERNAL 1

#Internal tree nodes can be specified using IDs directly, or using the 'last common ancestor' method described in iTOL help pages

#=================================================================#
#       Actual data follows after the DATA keyword                #
#=================================================================#
DATA

''')



# Write the itol header information for the font dataset.
# This file will tell itol how to format the leaves of the tree

fo2 = open(ofil2,"w+")

fo2.write('''    
TREE_COLORS
#use this template to define branch colors and styles, colored ranges and label colors/font styles
#lines starting with a hash are comments and ignored during parsing

#=================================================================#
#                    MANDATORY SETTINGS                           #
#=================================================================#
#select the separator which is used to delimit the data below (TAB,SPACE or COMMA).This separator must be used throughout this file (except in the SEPARATOR line, which uses space).

#SEPARATOR TAB
#SEPARATOR SPACE
SEPARATOR COMMA

#Internal tree nodes can be specified using IDs directly, or using the 'last common ancestor' method described in iTOL help pages
#=================================================================#
#        Actual data follows after the DATA keyword               #
#=================================================================#
DATA
''')



# Midpoint root tree
# Collapse branches with less that the specified threshold of support
# Write both trees to file 
t = PhyloTree(treefile, sp_naming_function=None)
otre1 = query + '.mpr.tree'
upfile1 = otre1 + '_upload.cfg'
downfile1 = otre1 + '_download.cfg'

otre2 = query + '.mpr.col' + str(support_threshold) + '.tree'
upfile2 = otre2 + '_upload.cfg'
downfile2 = otre2 + '_download.cfg'

R = t.get_midpoint_outgroup()
t.set_outgroup(R)

t.write(outfile = otre1)

for node in t.traverse("postorder"):
    if node.is_leaf() == False:    
        if node.support < int(support_threshold):
            #print(node.name)
            node.delete()
    
t.write(outfile = otre2)
#print(t)

# Determine which lineage to assign each leaf based on the NCBI lineage
# Print result to itol font and color_strip files
t = PhyloTree(treefile, sp_naming_function=None)

for n in t.get_leaves():
    #print(n.name)
    if n.name.startswith('QUERY'):
        fo2.write(n.name + ',label,#e31a1c,bold,1\n')
        fo1.write(n.name + ' #1f78b4 Haptista\n')

    elif len(n.name.split('-')) == 4:
        taxid = n.name.split('-')[1]
        #print(n.name, taxid)

        lincolor = '#000000'
        linname = ''
        lineage = taxdump(taxid)
        for i in lineage:
            if str(i) in lineages:
                linname = lineages[str(i)]
                lincolor = colorDict[linname]
                #print(linname,lincolor)
                break
        fo2.write(n.name + ',label,#000000,normal,1\n')
        fo1.write(n.name + ' ' + lincolor + ' ' + linname + '\n')
        
    else:
        fo2.write(n.name + ',label,#000000,normal,1\n')
        fo1.write(n.name + ' #1f78b4 Haptista\n')


fo1.close()
fo2.close()


# Zip the midpoint rooted tree with the itol formatting files 
cmd = 'zip ' + otre1 + '.zip ' + otre1 + ' ' + ofil1 + ' ' + ofil2
runCMD(cmd)

# Zip the midpoint rooted and branch collapsed tree with the itol formatting files
cmd = 'zip ' + otre2 + '.zip ' + otre2 + ' ' + ofil1 + ' ' + ofil2
runCMD(cmd)


# create the itol uploader file for both trees
ufil = open(upfile1,"w+")
ufil.write('zipFile=' + otre1 + '.zip\n')
ufil.write('treeName=' + query + ' midpoint rooted batch upload\n')
ufil.write('projectName=' + itolproject + '\n')
ufil.write('uploadID=' + itolid + '\n')
ufil.write('treeDescription=' + query + ' midpoint rooted batch uploaded file\n')
ufil.close()

ufil = open(upfile2,"w+")
ufil.write('zipFile=' + otre2 + '.zip\n')
ufil.write('treeName=' + query + ' midpoint rooted weak branches collapsed batch upload\n')
ufil.write('projectName=' + itolproject + '\n')
ufil.write('uploadID=' + itolid + '\n')
ufil.write('treeDescription=' + query + ' midpoint rooted weak branches collapsed batch uploaded file\n')
ufil.close()


cmd = 'perl ' + uploader + ' ' + upfile1
print(cmd)
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
output = process.communicate()[0]
output = output.decode("utf-8") 
itoltree1 = output.split('\n\n')[1]

cmd = 'perl ' + uploader + ' ' + upfile2
print(cmd)
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
output = process.communicate()[0]
output = output.decode("utf-8") 
itoltree2 = output.split('\n\n')[1]


# create the itol downloader file for both trees
dfil = open(downfile1,"w+")
dfil.write('tree=' + itoltree1 + '\n')
dfil.write('outFile=' + otre1 + '.pdf\n')
dfil.write('''    
format=pdf
tree_x=300
dpi=600
display_mode=1
current_font_name=Arial
line_width=5
datasets_visible=0
current_font_size=30
bootstrap_display=1
bootstrap_type=2
bootstrap_label_size=30
''')
dfil.close()

dfil = open(downfile2,"w+")
dfil.write('tree=' + itoltree2 + '\n')
dfil.write('outFile=' + otre2 + '.pdf\n')
dfil.write('''    
format=pdf
tree_x=300
dpi=600
display_mode=1
current_font_name=Arial
line_width=5
datasets_visible=0
current_font_size=30
bootstrap_display=1
bootstrap_type=2
bootstrap_label_size=30
''')

dfil.close()

# perl downloader needs perl module LWP::Protocol::https
# I was able to install on halstead using cpanm, but doesn't seem to be visable to workbench...
cmd = 'perl ' + downloader + ' ' + downfile1
runCMD(cmd)

cmd = 'perl ' + downloader + ' ' + downfile2
runCMD(cmd)

