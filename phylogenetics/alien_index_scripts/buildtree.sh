#! /usr/local/bin/bash

GENE=$1

# extract full length sequences
cd $CWD

module load bioinfo
module load HMMER
module load RAxML
module load FastTree
module load perl

PROGRAM="perl $CWD/scripts/extract_sequences.pl"
IN="$CWD/tree-out/fasta"

echo -e "$PROGRAM -q $QUERY -s $GENE -h $PARSEDIR -d $DB -o $IN -x $MAXSEQ -e $MAXEVALUE\n" 
time $PROGRAM -q $QUERY -s $GENE -h $PARSEDIR -d $DB -o $IN -x $MAXSEQ -e $MAXEVALUE

IN="$CWD/tree-out/fasta"
OUT="$CWD/tree-out/mafft"

cd $IN
if [ ! -f "${IN}/${GENE}.fa" ]; then 
    echo -e "WARNING : no fasta file for $GENE\n"	
	exit 3
fi

COUNT=`grep ">" ${IN}/${GENE}.fa | wc -l`
NL=$'\n'
COUNT=${COUNT%$NL}

echo -e "$COUNT sequences in ${IN}/${GENE}.fa\n"	

# align sequences
if [[ "$COUNT" -ge "$MINSEQ" ]]; then
	echo -e "COMMAND: $MAFFT $MAFFTOPT ${IN}/${GENE}.fa > ${OUT}/${GENE}.aln\n"
	time $MAFFT $MAFFTOPT ${IN}/${GENE}.fa > ${OUT}/${GENE}.aln
else 
    echo -e "Skipping $GENE : retained hits $COUNT < minimum $MINSEQ\n"
    exit 0
fi

IN="$CWD/tree-out/mafft"
OUT="$CWD/tree-out/trimal"

cd $IN
if [ ! -f "${IN}/${GENE}.aln" ]; then 
    echo -e "WARNING : no alignment file for $GENE\n"	
	exit 3
fi

# trim sequences
echo -e "COMMAND: $TRIMAL -in ${IN}/${GENE}.aln -out ${OUT}/${GENE}.aln.trim $TRIMOPT\n"
time $TRIMAL -in ${IN}/${GENE}.aln -out ${OUT}/${GENE}.aln.trim $TRIMOPT

# build trees
PRE="$CWD/tree-out/mafft"
IN="$CWD/tree-out/trimal"
OUT="$CWD/tree-out/tree"

cd $IN
if [ ! -f "${IN}/${GENE}.aln.trim" ]; then 
    echo -e "WARNING : no trimmed alignment file for $GENE\n"	
	exit 3
fi

# build trees
PRENUM=`grep ">" $PRE/${GENE}.aln | wc -l`
NEWNUM=`grep ">" $IN/${GENE}.aln.trim | wc -l`
PRELEN=`perl $CWD/scripts/aln_len.pl $PRE/${GENE}.aln`
NEWLEN=`perl $CWD/scripts/aln_len.pl $IN/${GENE}.aln.trim`

echo -e "FLAG: $GENE alignment length pre trimming = $PRELEN"
echo -e "FLAG: $GENE alignment length post trimming = $NEWLEN"
echo -e "FLAG: $GENE seq count pre trimming = $PRENUM"
echo -e "FLAG: $GENE seq count post trimming = $NEWNUM\n"

if [[ "$NEWLEN" -lt "$MINLEN" ]]; then
	echo -e "Skipping $GENE : trimmed alignment length $NEWLEN < minimum $MINLEN\n"
	exit 0
fi

if [[ "$TREETYPE" == 'raxml' ]]; then
	
	echo -e "COMMAND: $RAXML -s ${GENE}.aln.trim -n ${GENE}.out $RAXMLOPT\n"
	$RAXML -s ${GENE}.aln.trim -n ${GENE}.out $RAXMLOPT
	mv *.${GENE}.out $OUT

	cd $OUT
	mv RAxML_bipartitions.${GENE}.out RAxML_bipartitions.${GENE}.contree

	echo -e "python $CWD/scripts/create_itol_tree.py RAxML_bipartitions.${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $RXSUPPORT $TAXDIR\n"
	python $CWD/scripts/create_itol_tree.py RAxML_bipartitions.${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $RXSUPPORT $TAXDIR

fi

if [[ "$TREETYPE" == 'iqtree' ]]; then
	
	echo -e "COMMAND: $IQTREE -s $IN/${GENE}.aln.trim $IQTREEOPT -pre $OUT/${GENE} -nt 1\n"
	$IQTREE -s $IN/${GENE}.aln.trim $IQTREEOPT -pre $OUT/${GENE} -nt 1

	cd $OUT

	echo -e "python $CWD/scripts/create_itol_tree.py ${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR\n"
	python $CWD/scripts/create_itol_tree.py ${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR

fi

if [[ "$TREETYPE" == 'both' ]]; then
	
	echo -e "COMMAND: $IQTREE -s $IN/${GENE}.aln.trim $IQTREEOPT -pre $OUT/${GENE} -nt 1\n"
	$IQTREE -s $IN/${GENE}.aln.trim $IQTREEOPT -pre $OUT/${GENE} -nt 1

	cd $OUT

	echo -e "python $CWD/scripts/create_itol_tree.py ${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR\n"
	python $CWD/scripts/create_itol_tree.py ${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $IQSUPPORT $TAXDIR

	cd $IN
	echo -e "COMMAND: $RAXML -s ${GENE}.aln.trim -n ${GENE}.out $RAXMLOPT\n"
	$RAXML -s ${GENE}.aln.trim -n ${GENE}.out $RAXMLOPT
	mv *.${GENE}.out $OUT

	cd $OUT
	mv RAxML_bipartitions.${GENE}.out RAxML_bipartitions.${GENE}.contree

	echo -e "python $CWD/scripts/create_itol_tree.py RAxML_bipartitions.${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $RXSUPPORT $TAXDIR\n"
	python $CWD/scripts/create_itol_tree.py RAxML_bipartitions.${GENE}.contree $CWD/scripts $ITOLDIR $ITOLID $COLORSCHEME $RXSUPPORT $TAXDIR

fi
