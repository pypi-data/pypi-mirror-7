# Installation

These are advanced instructions for installing directly from the tarball or for
installing a development version from the git repository. See the Quick Install
section of the README for instructions on how to install a release version
using pip, the Python package manager.

After installing Agalma, run the built-in test:

    mkdir ~/tmp
    cd ~/tmp
    agalma test

See [TUTORIAL](https://bitbucket.org/caseywdunn/agalma/src/master/TUTORIAL.md)
for an example of how to use Agalma with a sample dataset.

## Reference List of Dependencies

Python modules:

* [biolite](https://bitbucket.org/caseywdunn/biolite), the release version or 
  development branch must match that of Agalma

Third-party tools called from Agalma, which need to be in your PATH:

* [biolite-tools 0.4.0](https://bitbucket.org/caseywdunn/biolite)
* [Blast 2.2.28+](http://blast.ncbi.nlm.nih.gov/)
* [Bowtie 1.0.0](http://bowtie-bio.sourceforge.net/)
* [Bowtie2 2.1.0](http://bowtie-bio.sourceforge.net/bowtie2/)
* [FastQC 0.10.1](http://www.bioinformatics.babraham.ac.uk/projects/fastqc/) 
* [Gblocks 0.91b](http://molevol.cmima.csic.es/castresana/Gblocks.html)
* [jellyfish 1.1.11](http://www.cbcb.umd.edu/software/jellyfish/)
* [MAFFT 7.130](http://mafft.cbrc.jp/alignment/software/)
* [mcl 12-135](http://micans.org/mcl)
* [GNU parallel 20130922](http://savannah.gnu.org/projects/parallel)
* [RAxML 7.7.6](http://sco.h-its.org/exelixis/web/software/raxml/)
* [RSEM 1.2.9](http://deweylab.biostat.wisc.edu/rsem/)
* [samtools 0.1.19](http://samtools.sourceforge.net/)
* [SRA Toolkit](http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=std)
* [transdecoder r2012-08-15](http://transdecoder.sourceforge.net/)
* [Trinity r2013-08-14](http://trinityrnaseq.sourceforge.net/)  
  Note: Agalma only works with version r2013-08-14. If you install manually, you must link Butterfly/Butterfly.jar, Inchworm/bin/inchworm, Chrysalis/Chrysalis, Chrysalis/QuantifyGraph, trinity-plugins/jellyfish/bin/jellyfish and util/partition_chrysalis_graphs_n_reads.pl into your PATH.

Optional tools used by alternate phylogeny pipelines:

* [MACSE 0.9b1](http://mbb.univ-montp2.fr/macse/)  
  Note: if you install manually, make sure the MACSE jar file is in your PATH.
* [OMA 0.99u.3](http://omabrowser.org/standalone)


## Installing dependencies

Agalma relies on BioLite for many core functions. Please see the BioLite
[INSTALL](https://bitbucket.org/caseywdunn/biolite/src/master/INSTALL.md) file
for instructions on how to install BioLite. Use the method (eg, git or tarball)
and version that matches your Agalma installation strategy.

We recommend installing the required third-party tools using [Bioinformatics
Brew](http://bib.bitbucket.org), a cross-platform package manager for
bioinformatics tools. Once BiB is installed, run:

    bib install -f biolite-tools/0.4.0 blast/2.2.29+ bowtie/1.0.0 bowtie2/2.1.0 fastqc/0.10.1 gblocks/0.91b jellyfish/1.1.11 mafft/7.130 mcl/12-135 parallel/20130922 raxml/7.7.6 rsem/1.2.9 samtools/0.1.19 sratoolkit/0.2.3.4-2 transdecoder/r2012-08-15 trinity/r2013_08_14

For the optional tools, run:

    bib install -f macse/0.9b1 oma/0.99u.3


## Installing Agalma from the tarball

Agalma uses the standard `distutils` method of installation:

    tar xf agalma-0.4.0.tar.gz
    cd agalma-0.4.0
    python setup.py install

During the install stage, the installer will download a zip file containing
BLAST databases that have been optimized for Agalma.

For an alternate install path, specify a prefix with:

    python setup.py install --prefix=...


## Installing Agalma form the git repo

Same as with the tarball, except clone the repo instead of downloading the tarball:

    git clone https://bitbucket.org/caseywdunn/agalma.git
    cd agalma
    python setup.py install

If you edit the code in the repository, or pull a new version, then run the following 
to update the installation:

    python setup.py install


## Generating a tarball from the git repo

First, regenerate the BLAST databases that are packaged with Agalma using the
scripts in the `dev` subdirectory:

    mkdir -p agalma/blastdb
    cd dev
    bash build-nt-rrna.sh
    bash build-swissprot.sh
    bash build-univec.sh

This will download a subset of the current GenBank (nt) database with only titles
containing "rrna", the current release of SwissProt, and the current release of
UniVec. The SwissProt database is parsed into a FASTA file that includes the OG
(Organelle) field in the description line.

The databases are packaged in their own download with:

    cd agalma
    zip -9r ../agalma-blastdb-X.X.X.zip blastdb
    cd ..

Then create a source distribution for Agalma with `distutils`:

    python setup.py sdist

