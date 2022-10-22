#!/bin/bash
#SBATCH --job-name=builttree_hgt1
#SBATCH --account=jwisecav
#SBATCH --mail-type=END,FAIL
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --time=24:00:00     
#SBATCH --output=slurm-out/%x.o%j
#SBATCH --error=slurm-out/%x.e%j

module load conda-env/env.genomics
module load hmmer 
module load mafft
module load iqtree
module load trimal

cd tree-out/mafft/
#mafft --reorder --bl 30 --op 1.0 --maxiterate 1000 --retree 1 --genafpair --quiet --thread 40 ../fasta/HGT1.fa > HGT1.aln
mafft --reorder --bl 30 --op 1.0 --maxiterate 1000 --retree 1 --genafpair --quiet --thread 8 ../fasta/HGT1_cropped.fa > HGT1_cropped.aln

cd ../trimal
#trimal -in ../mafft/HGT1.aln -out HGT1.aln.trim -gappyout
trimal -in ../mafft/HGT1_cropped.aln -out HGT1_cropped.aln.trim -gappyout

cd ../tree
# iqtree -s ../mafft/HGT1.aln -alrt 1000 -bb 1000 -pre HGT1 -nt AUTO -ntmax 128
iqtree -s ../mafft/HGT1_cropped.aln -alrt 1000 -bb 1000 -pre HGT1_cropped -nt AUTO -ntmax 128
iqtree -s ../trimal/HGT1_cropped.aln.trim -alrt 1000 -bb 1000 -pre HGT1_cropped_trimmed -nt AUTO -ntmax 128

ITOLDIR='Batch'
ITOLID='sfL3xRILcKAzkQxPgd9WOw'	
TAXDIR="../../dbs"
COLORSCHEME='haptophyte_euk'
IQSUPPORT=95

# python ../../scripts/create_itol_tree.py HGT1.contree ../../scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR
python ../../scripts/create_itol_tree.py HGT1_cropped.contree ../../scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR
python ../../scripts/create_itol_tree.py HGT1_cropped_trimmed.contree ../../scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR
