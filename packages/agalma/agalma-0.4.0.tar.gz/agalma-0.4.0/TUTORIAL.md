Agalma Tutorial
===============

This tutorial has two sections. The first describes an assembly run of the
Agalma transcriptome pipeline using a sample read data set. The second
describes a run of the phylogeny pipeline on a set of sample transcriptomes.

You can create a shell script that has just the commands you need to execute
from this document with the command:
`grep '^    ' TUTORIAL.md | sed -e 's/^    //' > tutorial.sh`.

Let's start by creating an organized directory hierarchy in your home directory
for storing Agalma data:

    mkdir -p agalma/analyses
    mkdir -p agalma/data
    mkdir -p agalma/scratch

We'll also specify a path for a local BioLite database to store the catalog of data
and the diagnostics from our runs:

    export BIOLITE_RESOURCES="database=$PWD/agalma/biolite.sqlite"

Agalma distinguishes between three types of storage locations:

1. a permanent location for raw data ("data")
2. a permanent location for the final output from analyses ("analyses")
3. a temporary location for the intermediate files from analyses ("scratch")

In a production system, you would want to make sure that "analyses" and "data"
are backed up, but "scratch" doesn't need to be backed up because its files
are typically only used over the course of a single analysis and can be
regenerated.

The 'testdata' command will unpack all of the sample data sets used in the
tutorials:

* 4 subsets of paired-end Illumina HiSeq reads from the siphonophore species:
  *Agalma elegans*, *Craseoa lathetica*, *Physalia physalis*, *Nanomia bijuga*
* 2 subsets of single-end Illumina GAIIx reads from two different specimens of
  the species *Nanomia bijuga*
* 6 transcriptome subsets, from Agalma assemblies of these four siphonophore
  species, plus an extra one for *Nanomia bijuga* and a public/external one for
  the species *Nematostella vectensis*

Let's run this command to download the sample data to the "data" directory:

    cd agalma/data
    agalma testdata

You should now see the test data files in the `data` directory.


Transcriptome
-------------

Now we'll create a catalog entry in the BioLite database for the *Agalma
elegans* data set:

    agalma catalog insert --paths SRX288285_1.fq SRX288285_2.fq --species "Agalma elegans" --ncbi_id 316166 --itis_id 51383

Note in the above commands that we are specifying both the the 
[ITIS ID](http://www.itis.gov), 
which is 51383, and [NCBI ID](http://www.ncbi.nlm.nih.gov/taxonomy), which is 
316166, for this species. Specifying both ID's is highly recommended.

The catalog command automatically recognizes the Illumina CASAVA 1.8 header in
the data and assigns a catalog ID `HWI-ST625-73-C0JUVACXX-7`.

Before running a pipeline, you may want to adjust the concurrency and memory
to match your computer. System performance may lag if you allocate the 
full available memory to agalma. You should leave at least 2 GB unallocated. If,
for example, you have an 8-core machine with 24 GB of free memory, you could 
allocate all the processors and 20 GB of the memory with 
`export BIOLITE_RESOURCES="threads=8,memory=20G"`.  You can run this small 25K
read data set with less resources, for instance using only 2 threads and 4GB of
memory:

    export BIOLITE_RESOURCES="$BIOLITE_RESOURCES,threads=2,memory=4G"

Now run the full transcriptome pipeline on the test data from the scratch
directory, and specify 'analyses' as the permanent output directory, with:

    cd ../scratch
    agalma transcriptome --id HWI-ST625-73-C0JUVACXX-7 --outdir ../analyses

To generate reports for the transcriptome run, use:

    cd ..
    agalma report --id HWI-ST625-73-C0JUVACXX-7 --outdir reports/HWI-ST625-73-C0JUVACXX-7
    agalma resources --id HWI-ST625-73-C0JUVACXX-7 --outdir reports/HWI-ST625-73-C0JUVACXX-7

You will now have a report with diagnostics for all of the transcriptome stages
run above located at:

* `agalma/reports/HWI-ST625-73-C0JUVACXX-7/index.html`

Another report with detailed resource utilization will be located at:

* `agalma/reports/HWI-ST625-73-C0JUVACXX-7/profile.html`


Phylogeny
---------

This analysis builds a species tree for 5 taxa using small transcriptome
subsets, and requires roughly 7 GB of RAM and 10 minutes of runtime on an
8-core Intel Xeon E5540 node.

Let's define a default value for the output directory so that you don't have to
keep retyping the `--outdir` parameter, and also a path for the Agalma database
that will store the sequences and homology information:

    export BIOLITE_RESOURCES="$BIOLITE_RESOURCES,outdir=$PWD/analyses,agalma_database=$PWD/agalma.sqlite"

Rather than assemble all of the datasets, we are going to use the fasta 
files from already assembled transcriptomes.

First, we'll catalog our data:

    cd data
    agalma catalog insert --id SRX288285 --paths SRX288285_1.fq SRX288285_2.fq --species "Agalma elegans" --ncbi_id 316166
    agalma catalog insert --id SRX288432 --paths SRX288432_1.fq SRX288432_2.fq --species "Craseoa lathetica" --ncbi_id 316205
    agalma catalog insert --id SRX288431 --paths SRX288431_1.fq SRX288431_2.fq --species "Physalia physalis" --ncbi_id 168775
    agalma catalog insert --id SRX288430 --paths SRX288430_1.fq SRX288430_2.fq --species "Nanomia bijuga" --ncbi_id 168759
    agalma catalog insert --id JGI_NEMVEC --paths JGI_NEMVEC.fa --species "Nematostella vectensis" --ncbi_id 45351

Each assembled transcriptome has to be 'post-assembled' to create protein
translations (by longest open reading frame) and annotations for BLASTX hits
against SwissProt:

    cd ../scratch
    agalma postassemble --id SRX288285 --assembly ../data/SRX288285.fa
    agalma postassemble --id SRX288430 --assembly ../data/SRX288430.fa
    agalma postassemble --id SRX288431 --assembly ../data/SRX288431.fa
    agalma postassemble --id SRX288432 --assembly ../data/SRX288432.fa
    agalma postassemble --id JGI_NEMVEC --external

For JGI_NEMVEC, we didn't have to specify the path to the assembly because the
catalog path already points to the assembly file, but we do have to specify
that it is an external assembly with the `--external` flag. For the
transcriptomes produced by Agalma, that path in the catalog points to the read
sequences used to estimate coverage in the `postassemble`.

Next, each assembly is loaded separately into the Agalma database using the
`load` pipeline. Here is an example of loading transcriptomes for the 5 sample
data sets that were assembled with Agalma and the external assembly from JGI.
Load automatically identifies the most recent run of `postassemble` for each
catalog ID.

    agalma load --id SRX288285
    agalma load --id SRX288430
    agalma load --id SRX288431
    agalma load --id SRX288432
    agalma load --id JGI_NEMVEC

Now that you have loaded all of the data sets, call the `homologize` pipeline
on the list of run IDs for each of the load commands. A quick way to find the
the run IDs for all of the load commands you have run is to use the
`diagnostics` tool:

    export LOAD_IDS=$(agalma diagnostics list -n load | awk 'NR>1 {print $2}')
    agalma homologize --id PhylogenyTest $LOAD_IDS

You may need to adjust the load IDs if you have run other analyses, or only
want to use some of the data you have loaded, etc.  The option `--id
PhylogenyTest` specifies the analysis ID, and will be used to pass results
through several commands below. This ID should be unique for each phylogenetic
analysis.  Also note that the list $LOAD_IDS is passed directly into the 
`homologize` pipeline without specifying any flags.  Please read the help 
option `-h` if you need more information.

The `homologize` pipeline will write a collection of gene clusters back into
the Agalma database.

Now call this sequence of pipelines, inserting the analysis ID each time, to
build gene trees for each of the clusters, and finally to assemble a
supermatrix with a single concatenated sequence of genes for each taxon.

    agalma multalign --id PhylogenyTest
    agalma genetree --id PhylogenyTest
    agalma treeprune --id PhylogenyTest
    agalma multalign --id PhylogenyTest
    agalma supermatrix --id PhylogenyTest
    agalma speciestree --id PhylogenyTest --raxml_flags="-o Nematostella_vectensis"

The supermatrix will be located in:

* `agalma/analyses/PhylogenyTest/*/supermatrix-prot/supermatrix.fa`

and the phylogenetic tree in:

* `agalma/analyses/PhylogenyTest/*/RAxML_bestTree.supermatrix`

To generate reports for the phylogeny run, use:

    cd ..
    agalma report --id PhylogenyTest --outdir reports/PhylogenyTest
    agalma resources --id PhylogenyTest --outdir reports/PhylogenyTest
    agalma phylogeny_report --id PhylogenyTest --outdir reports/PhylogenyTest

You will now have a report with diagnostics for all of the phylogeny stages run
above, including images of the supermatrices and the final tree, located at:

* `agalma/reports/PhylogenyTest/index.html`

Another report with detailed resource utilization will be located at:

* `agalma/reports/PhylogenyTest/profile.html`

A line graph showing the reduction in the number of genes at each stage will
be located at:

* `agalma/reports/PhylogenyTest/PhylogenyTest.pdf`

You can view a list of all the runs from this tutorial with the 'diagnostics'
command:

    agalma diagnostics list

