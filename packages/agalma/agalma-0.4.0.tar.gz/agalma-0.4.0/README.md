Agalma is developed by the [Dunn Lab](http://dunnlab.org) at Brown University.

See [TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md)
for an example of how to use Agalma with a sample dataset. Please consult the
FAQ and Troubleshooting sections below if you have any questions or problems.


#Overview of Agalma

Agalma is a set of analysis pipelines for phylogenomic analyses. It builds alignments of homologous genes and preliminary species trees from genomic and transcriptome data. Agalma includes support for transcriptome assembly (paired-end Illumina data), and can 
also import gene predictions from other sources (eg, assembled non-Illumina 
transcriptomes or gene models from annotated genomes). Please carefully read 
the details on Data requirements before proceeding with your analyses.

Agalma provides a completely automated analysis workflow, and records rich 
diagnostics. You can then evaluate these 
diagnostics to spot problems and examine the success of your analyses, the 
quality of the orignal data, and the appropriateness of the default parameters. 
You can then rerun subsets of the pipelines with optimized parameters as needed.

The main functionality of this workflow is to:

* assess read quality with the FastQC package
* remove clusters in which one or both reads have Illumina adapters
  (resulting from small inserts)
* remove clusters where one or both reads is of low mean quality
* assemble and annotate rRNA sequences based on a subassembly of the data
* remove clusters in which one or both reads map to rRNA sequences
* create a larger subassembly of the dataset to profile expression of
  transcripts and assess the distribution of sequencing effort
* create HTML reports that summarize the diagnostics collected during analyses 
  of each transcriptome
* load the assembled sequences into a database
* load gene predictions from other sources into the database
* identify homologous sequences across multiple species based on sequence 
  similarity
* create nucleotide and protein alignments for each set of homologous sequences
* build gene trees for each set of aligned homologous sequences
* identify orthologs through topological analysis of the gene trees
* create nucleotide and protein alignments for each set of orthologs
* construct and analyze supermatrices of orthologs to build species phylogenies

The workflow is optimized to reduce RAM and computational
requirements, as well as the disk space used. It logs detailed stats about
computer resource utilization to help you understand what type of computational
resources you need.

Agalma is built on top of BioLite, a bioinformatics framework written in
Python/C++ that automates the collection and reporting of diagnostics, tracks
provenance, and provides lightweight tools for building out customized analysis
pipelines.

Agalma is named after a clade of siphonophores. Siphonophores are our favorite
animals. Please visit [siphonophores.org](http://siphonophores.org) and 
[creaturecast.org](http://creaturecast.org) to learn more about them.


#Quick Install

These instructions describe how to install the latest release of Agalma.  We
have tested Agalma on OS X 10.9, Ubuntu 14.04, and CentOS 6.5 (with Python 2.7
installed).  It may not work on earlier versions of these operating systems
without customization. It likely works on other operating systems as well,
though we have not tested them.

For more information on dependencies, other operating systems, installation from 
other sources, and installation of development versions, please see the 
[INSTALL](https://bitbucket.org/caseywdunn/agalma/src/master/INSTALL.md) file.

These instructions require pip, the Python package manager. If you don't have
pip, you may be able to install it with `easy_install`:

    sudo easy_install pip

or with your OS package manager, e.g. on **Ubuntu**:

    sudo apt-get install -y python-pip python-dev


##Install dependencies

Agalma has many dependencies on external programs. We recommend installing them
using [Bioinformatics Brew](http://bib.bitbucket.org), a cross-platform package
manager for bioinformatics tools. Once BiB is installed, run:

    bib install -f biolite-tools/0.4.0 blast/2.2.29+ bowtie/1.0.0 bowtie2/2.1.0 fastqc/0.10.1 gblocks/0.91b jellyfish/1.1.11 mafft/7.130 mcl/12-135 parallel/20130922 raxml/7.7.6 rsem/1.2.9 samtools/0.1.19 sratoolkit/0.2.3.4-2 transdecoder/r2012-08-15 trinity/r2013_08_14

To use alternate phylogeny pipelines, you may also need to run:

    bib install -f macse/0.9b1 oma/0.99u.3

On **Ubuntu**, pre-install matplotlib and these dev packages:

    sudo apt-get install -y python-matplotlib libxml2-dev libxslt1-dev
    sudo cpan -i FindBin URI::Escape


##Install Agalma

Install Agalma with pip:

    sudo pip install agalma

On **OS X** you must run:

    export CFLAGS=-Qunused-arguments
    export CPPFLAGS=-Qunused-arguments
    sudo -E pip install agalma

The `export` commands are due to a known bug in Apple's most recent command
line tools ([StackOverflow post](http://stackoverflow.com/questions/22313407)).


##Test Agalma

After installing, run the built-in test:

    mkdir ~/tmp
    cd ~/tmp
    agalma test

This will check to see that your installation works. It runs through a series 
of test analyses on some very small data sets. This takes about 24
minutes on a 2 core 2 GHz Ubuntu machine (ie, an [C3 Large Amazon EC2 
general purpose Ubuntu instance](http://aws.amazon.com/ec2/instance-types/)).

Once the test completes without error, run the 
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md).
This  will familiarize you with the use of Agalma and clarify best practices.


#Data Requirements

The data requirements for raw transcriptome reads that are to be assembled 
by Agalma are:

* Input data must be in FASTQ format.
* The quality scores must be encoded with an ASCII offset of 33. Older Illumina 
  files may use an offset of 64 or 63, in which case they would need to be 
  transformed to 33.
* Data are paired, with one file for the forward reads and one for the reverse
  reads. Each file must have a paired read in the other file, and they must
  be in the exact same order.
* FASTQ headers are in Casava 1.6 or Casava 1.8 format. A definition and
  example of each is shown below.

  Casava 1.6 FASTQ header:

    @HWI-ST625:3:1:1330:2071#0/1
    @<instrument>:<lane>:<tile>:<x-pos>:<y-pos>#<index number>/<read>

  Casava 1.8 FASTQ header:

    @HWI-ST625:73:C0JUVACXX:7:1101:1403:1923 1:N:0:TGACCA
    @<instrument>:<run number>:<flowcell ID>:<lane>:<tile>:<x-pos>:<y-pos> <read>:<is filtered>:<control number>:<indexsequence>

* Reads that did not pass the Illumina filter must be removed already. If the
  files from the sequencing center include reads that did not pass filter, they
  can be removed with the following command (assuming a Casava 1.8+ header):

    grep -A 3 '^@.*[^:]*:N:[^:]*:' in.fastq | grep -v '^\-\-$' > out.fastq
  
* The pipeline does not trim sequences, i.e. remove a particular region of each
  read. If you have low quality ends, these should be trimmed before feeding
  the data to the pipeline. Likewise, if you need to remove inline indices or
  other sequences do it before you pass the data to the pipeline.

#Using Agalma

All of your interactions with Agalma will be through the command line program `agalma`. This program can execute a
variety of commands.  To see the available commands, just type `agalma` without
any arguments:

    agalma

    usage: agalma COMMAND [ARGS]

    This is a wrapper script for the various components that come
    with agalma, a suite of tools for de novo assembly and annotation
    of transcriptomes from paired-end sequence data. The following
    commands are available:

    ...

    Meta-pipelines:
      preassemble    [sanitize, insert_size, remove_rrna]
      transcriptome  [preassemble, assemble, postassemble]
    
    ...
    
    To print a help message for a specific command, use:
      agalma COMMAND -h


As indicated by the help message, you can get help on particular commands with
the ` -h` flag. For example, the following shows all the options available for
the transcriptome pipeline:

    agalma transcriptome -h

The following sections briefly describe the most important commands in a
typical analysis.


##Registering your data in the 'catalog'

BioLite maintains a 'catalog' stored in an SQLite database of metadata
associated with your raw Illumina data, including:

* A unique ID that you make up to reference this data set.
* Paths to the FASTQ files containing the raw forward and reverse reads.
* The species name, NCBI ID, and ITIS ID.
* The sequencing center where the data was collected.

You can insert a new catalog entry with the command:

    agalma catalog insert -h
 
    usage: catalog insert [-h] [-i ID] [-p [PATHS [PATHS ...]]] [-s SPECIES]
                          [-n NCBI_ID] [-d ITIS_ID] [-e EXTRACTION_ID]
                          [-l LIBRARY_ID] [-b LIBRARY_TYPE] [-t TISSUE]
                          [-q SEQUENCER] [-c SEQ_CENTER] [--note NOTE]
                          [--sample_prep SAMPLE_PREP]

By default, this will use the first four fields of the Illumina header in
`PATH1` as the catalog ID. You can manually override this by specifying `--id
ID`.

We strongly suggest that you specify all fields if they are available. This 
doesn't have to be done at once - the insert command acts like an update for subsequent 
calls on an existing catalog ID. That is, if you do a subsequent insert with an 
existing catalog ID, that catalog record will be updated with any new 
information you have specified.

Enter the [NCBI_ID](http://www.ncbi.nlm.nih.gov/taxonomy) for your species, if 
one exists. If not, then leave it blank. Enter the 
[ITIS_ID](http://www.itis.gov) for your species, if 
it exists. If not, then enter the ITIS id for the least inclusive clade that 
includes your species (eg, genus). Entering both of these IDs at the outset 
provides a chance to double check the validity and spelling of your species 
name, and facilitates downstream analyses.

You can view all of your entries with:

    agalma catalog all

When executing BioLite pipelines, you can simply use the catalog ID rather than
typing the full paths to the raw data.

##Overview of the transcriptome assembly pipeline


    transcriptome
    |- preassemble
    |  |- sanitize
    |  |- insert_size
    |  +- remove_rrna
    |- assemble
    |- postassemble
    +- report

Each of the component pipelines is described in the sections below.

The top-level `transcriptome` pipeline will prepare your raw RNA-Seq data
for assembly, then assemble it using a range of subsets and kmer sizes.

Once you have entered your dataset in the catalog, you can run the entire
pipeline with:

    agalma transcriptome -i CATALOG_ID -o OUTDIR

The current working directory will be used for temporary files (some of them as
large as your input data), and all output that will be kept permanently will be
written to the specified `OUTDIR`.

If the pipeline fails at any stage, you can correct the problem and restart the
pipeline from that stage with:

    agalma transcriptome --restart --stage N

Diagnostics will be logged to a tab-separated text file called
'diagnostics.txt' in the working directory. Once the pipeline completes, this
text file is merged into the global diagnostics SQLite database, which you can
browse with the diagnostics command:

    agalma diagnostics -h
    usage: diagnostics [-h]
                       {list,all,id,run,merge,delete,hide,unhide,programs} ...
 
For example, to view a listing of all past runs, use no options:

    agalma diagnostics list

To view the detailed diagnostics for a particular run, use:

    agalma diagnostics run RUN_ID

You can also run the pipeline components individually. The restarting and
diagnostics features exists in all the pipelines described below. To see all of
the parameters available for a given pipeline, including the default values,
use the `-h` option. This will also display a full list of the stages in the
pipeline with short descriptions of each.

##sanitize

This pipeline filters low quality reads (default: 28), reads with adapter
sequences, and reads with highly skewed base composition. The output of the
pipeline includes two FASTQ files with the 'sanitized' postfix. 

To run a dataset with `CATALOG_ID` through the entire sanitize pipeline, use:

    agalma sanitize -i CATALOG_ID -o OUTDIR

##insert_size

This pipeline uses a small subassembly and bowtie mapping to estimate the mean
and variance of the insert size of your input data. Once these have been
estimated and logged in the global diagnostics database, future pipeline runs
on the same catalog ID that will automatically use the estimates when calling
oases and bowtie.

##remove_rrna

After sanitizing your raw data and estimating its insert size, you can assemble
a subset of the data to identify and exclude reads that map to known ribosomal
RNA. The output of the pipeline includes two FASTQ files with the '.norrna'
postfix.

To reduce computation time, Agalma provides a set of curated rRNA sequences 
that includes only metazoan sequences.  If you are working with another clade 
of organisms, please refer to the FAQ for instructions on how to configure your 
system.

##assemble

The assemble pipeline performs another filtering stage at a higher quality
threshold (default: 33). Then it runs Trinity assembler to generate the 
transcriptome assembly.

##postassemble

This pipeline cleans the assembled transcripts to remove any rRNA or vector
sequences. Vector sequences could include untrimmed adapters or plasmids (we
sometimes find sequences in our data for the protein expression vectors used to
manufacture the sample preparation enzymes).  The longest likely coding region 
per transcript is identified and annotated using blastp against SwissProt. Raw 
reads are mapped back to the transcripts to estimate coverage and assign TPKM 
values. The TPKM values are used downstream to choose exemplar transcripts 
(those with the highest TPKM). Finally, transcripts are annotated with blastx 
hits against SwissProt. The `agalma blastdb` command will install a complete, 
single-file copy of SwissProt for this purpose. To reduce computation time, it 
is also possible to use a filtered SwissProt database that includes a narrower 
subset of species, such as only metazoan or viridiplantae sequences (see [Subsetting
swissprot](https://bitbucket.org/caseywdunn/agalma/wiki/Subsetting%20swissprot)
in the wiki).

If you plan to use gene predictions from other sources (eg, assembled
non-Illumina transcriptomes or gene models from annotated genomes) in
downstream analyses in Agalma (e.g. the phylogeny pipeline), these predictions
need to be run through the postassemble pipeline to generate translations. See
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md) for 
an example of how to use Agalma with gene predictions from other sources.

##report

This tool generates HTML reports of datasets that have been processed with an
Agalma pipeline, using a dataset's `CATALOG_ID` to search the global
diagnostics database:

    agalma report --id CATALOG_ID

By default, this will output the HTML files and subdirectories in the current
working directory. Or you can output them to a specific OUTDIR with:

    agalma report --id CATALOG_ID --outdir OUTDIR


Subsequent phylogenetic analyses require that all gene sequences to be considered
are loaded into the local Agalma database.  The `load` command takes care of this 
process.

##load

This pipeline parses assembled sequences and loads them into Agalma's database.
Annotations for sequences that were assembled by Agalma or for gene predictions
from other sources are also parsed.

##Overview of the phylogeny pipeline

Once assemblies for multiple species are loaded into the local Agalma database, 
a phylogenomic analysis will ecompass the following pipelines

    +  homologize
    |- multalign
    |- genetree
    |- treeprune
    |- multalign
    +- genetree

##homologize

This pipeline identifies homologous sequences across datasets that have
been loaded into the Agalma database. It performs an all-by-all BLAST search at a
stringent threshold, and the hits which match above a given score are used as
edges between two transcripts which then form a graph. The graph is broken into
clusters (i.e., connected components) that contain homologous gene sequences.

##multalign

This pipeline applies sampling and length filters to each cluster of homologous
sequences.  Then, it performs multiple sequence alignment for each cluster using
MAFFT (L-INS-i algorithm).  Finally, the alignments are cleaned up with Gblocks.  

Alternatively, clusters can be aligned using MACSE, a translation aware multiple 
sequence aligner that accounts for frameshifts and stop codons.  To do this, use the 
`multalignx` pipeline.  For further details, please read `agalma multalignx -h`  

##genetree

This pipeline builds gene trees for each set of homologous sequences. It builds
a maximum likelihood phylogenetic tree with RAxML.

##treeprune

This pipeline prunes each gene tree to include only one representative sequence
per taxon when sequences form a monophyloetic group (here called 'monophyly
masking'). It then prunes the monophyly-masked tree into maximally inclusive
subtrees with no more than one sequence per taxon (here called 'paralogy
pruning'). The pruned trees are then re-entered as clusters in the Agalma
database.

##multalign

In the second pass, this pipeline performs multiple alignment on the clusters
generated from the pruned trees. 

##supermatrix

This pipeline concatenates the multiple alignments together into a supermatrix, 
with one sequence per taxon. It also creates a supermatrix with a given proportion
of gene occupancy. 

##speciestree

Finally, the `speciestree` pipeline is used to build a maximum likelihood species 
tree from the supermatrix.

#Running a pipeline without the catalog

It is possible to run the transcriptome pipeline without first cataloging the 
data, though we strongly discourage this. To bypass the catalog and specify the 
paths to your forward and reverse FASTQ files, use:

    agalma transcriptome -f FASTQ1 FASTQ2 -o OUTDIR

Without an ID, the pipeline will use the default 'NoID' when writing
diagnostics. If you use the `-i` and `-f` options together, the ID doesn't have
to exist in the catalog, but will be used for naming the diagnostics.

#Updating and uninstalling

Agalma is under active development. This means that new updates are not always 
compatiable with analyses that have already been run. We make every effort to 
avoid changes to the catalog database structure, so there is usually not a need 
to re-catalog data when you install a new version. However, you may need to 
rerun already completed analyses if you want to generate new reports or use 
existing data with new versions of pipelines.

To uninstall after installing from the source tarball, run the command:

    make uninstall

from the source directory where you built and installed Agalma.

#Troubleshooting

Please read the entire README.md file prior to use, and then again if you 
encounter any problems. Unfortunately we cannot support all operating systems, 
all types of data (eg old Illumina file formats), or integration with other 
tools that are not already part of the core Agalma pipeline (such as external 
programs for filtering reads). We are very grateful for bugs you report and 
suggestions on clarifying the documentation, but please understand that we 
cannot help you use Agalma in ways that we have not yet tested or on 
operating systems we do not provide details for (including older versions of 
those operating systems).

##Reporting problems

If you have successfully run the
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md),
your data meet all the specified criteria, you are using Agalma as described,
and you have reread the entire README.md, but still encounter a problem, please
submit the issue to us with the 
[issue tracker](https://bitbucket.org/caseywdunn/agalma/issues). 
This will require a Bitbucket account. When reporting a bug, attach the
diagnostics file generated by the failed analysis and provide a detailed
description of the problem.

Please do not e-mail us directly with bugs. The issue tracker allows everyone
to see what bugs have been flagged so that the same issue isn't raised
repeatedly. If you have the same problem as someone else, feel free to add a
comment to the existing issue. The issue tracker allows us to track problems
much more efficiently than we can with e-mail and will also help us get to your
bug more quickly.

##Problems using Agalma

Before you tackle your own data, it is essential that you walk through the 
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md).
This will validate your installation, and familiarize you with how the tool is
intended to be used.

Once you have successfully run the tutorial to completion, review the section 
on Data requirements. Make sure your data satisfy all the of these requirements.

When you analyze your own data, adhere as closely as possible to the tutorial. 
Make use of the catalog, and don't skip pipelines.

When the above advice are followed, the most common problems we see fall into 
the following categories.

###Poor data quality

If there are problems with a sequencing run, many of the reads may be of low 
quality, or the tail end of all reads are of low quality. If the tail of all 
reads is low quality, many of them may fall the Agalma quality filters. Though 
it may still be possible to use poor quality data with Agalma, we cannot 
provide support for this. 

Take a look at your read quality with FastQC or a similar tool. If the read
ends are of low quality, trim them prior to cataloging and analyzing them with
Agalma.  Be sure that your trimming tool does not eliminate some reads from one
paired file and other reads from the other paired file. Fixed-length trim (eg,
lop off everything after the 80th nucleotide for all reads) is usually an
appropriate way to deal with trimming. 

###Incompatible data

Agalma has been extensively tested with paired reads of length 100bp from the
Illumina HiSeq 2000 platform. It has only had minimal to no testing with other
types of data, including single-end data, shorter read pair data (especially
shorter than 45bp) and data from other sequencing technologies.

###Insufficient system resources

If you run out of RAM or disk space, Agalma will fail. Depending on the
way your system is configured, you may or may not receive a clear error message
indicating this as the cause of the failure. To check available disk space
on a Unix system, use the `df` command. To check available RAM, you can run
`top` in another terminal while an Agalma pipeline is running.

These analyses are computationally intensive, and can therefore take some time. 

#Frequently Asked Questions (FAQ)

###Do you have plans to implement feature X?

Our current priorities for Agalma are to rigorously test and optimize a core 
phylogenomics workflow. Agalma is very modular, and once we are satisfied with 
the core functionality we will add additional pipelines that use alternative 
methods for particular steps, such as orthology evaluation.

###Can I add new features to Agalma?

Please do! We encourage you to fork the repository, implement your new feature, 
and, once it is working, send us a pull request so that we can incorporate it 
into the master branch. Please take a look at the 
[BioLite documentation](https://bitbucket.org/caseywdunn/biolite/src/master/BioLiteManual.pdf) 
to better understand our development model. In most cases it makes sense to 
implement new features as their own pipelines.

###Can I skip pipelines?

We strongly advice you to avoid skipping pipelines and follow the instructions
in the
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md)
as closely as possible. Otherwise, it is likely that Agalma will not work
properly, or will generate unexpected errors.

###Can I skip stages within pipelines?

Yes, you can skip stages within pipelines when absolutely necessary (eg, skip
exemplar selection in postassemble with transcriptomes not generated within
agalma), or when restarting particular pipelines and you do not need to
repeat certain stages.  Notice that stages within pipelines are 
numbered starting with 0.  So skiping stage 0 actually skips the first stage of
the pipeline.  You can see all the stages (with their respective numbers) for
a pipeline typing 

    agalma COMMAND -h

###I am not working with Metazoa, how can I configure the databases needed by Agalma?

Agalma installs automatically the sample of curated rRNA sequences to:

    /usr/local/share/agalma

and the optimized databases to:

    /usr/local/share/agalma/blastdb

You can customize your databases depending on the clade of organisms you 
are working on, and configure the paths to these databases in your configuration
file located at:

    /usr/local/share/agalma/agalma.cfg

##How to create a new diagnostics database with the catalog from a previous database?

You can copy your catalog to a new diagnostics database. From your old database, do

    catalog export "*" >catalog.sh

This creates a shell script with catalog commands. Then setup your BioLite config 
to point to a new diagnostics database and run the shell commands:

    sh catalog.sh

This will populate the new database.

###Can I run a bootstrap phylogenetic analysis? 

Yes, all the options avalaible in RAxML are available in Agalma. These options 
can be passed as optional arguments to the `genetree` and `speciestree` pipelines 
with the flag `--raxml_flags`.  For example, for a rapid bootstrap analysis, you would 
need to type:
 
    --raxml_flags "-x random_number  -# number_of_replicates"

Note that the quotes are necessary.

###I am getting an exception error, what should I do?

Sometimes you can get expection errors from 3rd party software that Agalma uses
extensively (e.g. BLAST). Although these errors could be actual bugs in those
programs, we have run extensive testing and it is unlikely you will run into
bugs if you use Agalma as indicated here and in the 
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md).
There are a couple of things you can do to check why the error may have
happened:

* Take a look at the files that are generated at each stage of the pipeline
and make sure your files are not empty. If they are empty, make sure your data
meet the requirements in Agalma, and make sure you are following the
instructions in the
[TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md)
to run Agalma.
* Make sure you are using the versions of the 3rd party software that come with BioLite; see the BioLite
[INSTALL](https://bitbucket.org/caseywdunn/biolite/src/master/INSTALL.md)
instructions.


#Citing

The `agalma cite` command should print an up-to-date list of citations, including the citation for Agalma:

Dunn CW, Howison M, Zapata F. 2013. Agalma: an automated phylogenomics
workflow. BMC Bioinformatics **14**(1): 330.
[doi:10.1186/1471-2105-14-330](http://dx.doi.org/10.1186/1471-2105-14-330)

BioLite is still under development, and is an experimental tool that should be
used with care.  Please cite:

Howison M, Sinnott-Armstrong NA, Dunn CW. 2012. [BioLite, a lightweight
bioinformatics framework with automated tracking of diagnostics and
provenance](https://www.usenix.org/conference/tapp12/biolite-lightweight-bioinformatics-framework-automated-tracking-diagnostics-and).
In *Proceedings of the 4th USENIX Workshop on the Theory and Practice of
Provenance (TaPP '12)*, 14-15 June 2012, Boston, MA, USA.

Agalma and BioLite makes use of many other programs that do much of the heavy
lifting of the analyses. Please be sure to credit these essential components as
well. 


#Funding

This software has been developed with support from the following US National
Science Foundation grants:

PSCIC Full Proposal: The iPlant Collaborative: A Cyberinfrastructure-Centered
Community for a New Plant Biology (Award Number 0735191)

Collaborative Research: Resolving old questions in Mollusc phylogenetics with
new EST data and developing general phylogenomic tools (Award Number 0844596)

Infrastructure to Advance Life Sciences in the Ocean State (Award Number
1004057)

The Brown University [Center for Computation and Visualization](http://www.brown.edu/Departments/CCV/) has been instrumental to the development of Agalma.


#License

Copyright (c) 2012-2014 Brown University. All rights reserved.

Agalma is distributed under the GNU General Public License version
3. For more information, see LICENSE or visit:
[http://www.gnu.org/licenses/gpl.html](http://www.gnu.org/licenses/gpl.html)

