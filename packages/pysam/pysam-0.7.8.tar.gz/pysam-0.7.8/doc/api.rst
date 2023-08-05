======================================================
pysam - An interface for reading and writing SAM files
======================================================

Pysam is a python module that makes it easy to read and manipulate mapped short read sequence data stored in SAM/BAM files. 
It is a lightweight wrapper of the samtools_ C-API.

This page provides a quick introduction in using pysam followed by the API. 
See :ref:`usage` for more detailed usage instructions.

To use the module to read a file in BAM format, create a :class:`~pysam.Samfile` object::

   import pysam
   samfile = pysam.Samfile( "ex1.bam", "rb" )
   

Once a file is opened you can iterate over all of the read mapping to a specified region using :meth:`~pysam.Samfile.fetch`.
Each iteration returns a :class:`~pysam.AlignedRead` object which represents a single read along with its fields and optional tags::

   for alignedread in samfile.fetch('chr1', 100, 120):
	print alignedread

   samfile.close()

To give::

    EAS56_57:6:190:289:82	0	99	<<<7<<<;<<<<<<<<8;;<7;4<;<;;;;;94<;	69	CTCAAGGTTGTTGCAAGGGGGTCTATGTGAACAAA	0	192	1
    EAS56_57:6:190:289:82	0	99	<<<<<<;<<<<<<<<<<;<<;<<<<;8<6;9;;2;	137	AGGGGTGCAGAGCCGAGTCACGGGGTTGCCAGCAC	73	64	1
    EAS51_64:3:190:727:308	0	102	<<<<<<<<<<<<<<<<<<<<<<<<<<<::<<<844	99	GGTGCAGAGCCGAGTCACGGGGTTGCCAGCACAGG	99	18	1
    ...

You can also write to a :class:`~pysam.Samfile`::

   import pysam
   samfile = pysam.Samfile("ex1.bam", "rb")
   pairedreads = pysam.Samfile("allpaired.bam", "wb", template=samfile)
   for read in samfile.fetch():
	if read.is_paired:
		pairedreads.write(read)

   pairedreads.close()
   samfile.close()

An alternative way of accessing the data in a SAM file is by iterating 
over each base of a specified region using the :meth:`~pysam.Samfile.pileup` 
method. Each iteration returns a :class:`~pysam.PileupColumn` which 
represents all the reads in the SAM file that map to a single base in the 
reference sequence. The list of reads are represented as :class:`~pysam.PileupRead` 
objects in the :attr:`PileupColumn.pileups <pysam.PileupColumn.pileups>` property::

    import pysam
    samfile = pysam.Samfile("ex1.bam", "rb" )
    for pileupcolumn in samfile.pileup( 'chr1', 100, 120):
	print
	print 'coverage at base %s = %s' % (pileupcolumn.pos , pileupcolumn.n)
	for pileupread in pileupcolumn.pileups:
	    print '\tbase in read %s = %s' % (pileupread.alignment.qname, pileupread.alignment.seq[pileupread.qpos])

    samfile.close()

The above code outputs::

    coverage at base 99 = 1
        base in read EAS56_57:6:190:289:82 = A

    coverage at base 100 = 1
        base in read EAS56_57:6:190:289:82 = G

    coverage at base 101 = 1
        base in read EAS56_57:6:190:289:82 = G

    coverage at base 102 = 2
        base in read EAS56_57:6:190:289:82 = G
        base in read EAS51_64:3:190:727:308 = G
    ...

Commands available in :term:`csamtools` are available as simple function calls. For example::

   pysam.sort( "ex1.bam", "output" )

corresponds to the command line::

   samtools sort ex1.bam output

Analogous to :class:`~pysam.Samfile`, a :class:`~pysam.Tabixfile` allows fast random access to compressed
and tabix indexed tab-separated file formats with genomic data::

   import pysam
   tabixfile = pysam.Tabixfile( "example.gtf.gz" )
   
   for gtf in tabixfile.fetch('chr1', 1000, 2000):
       print gtf.contig, gtf.start, gtf.end, gtf.gene_id

:class:`~pysam.Tabixfile` implements lazy parsing in order to iterate over large tables efficiently.

More detailed usage instructions is at :ref:`usage`.

.. note::
    Coordinates in pysam are always 0-based (following the python convention). SAM text files use 1-based coordinates.

.. note::
    The above examples can be run in the :file:`tests` directory of the installation directory. Type 'make' before 
    running them.

.. seealso::

    http://code.google.com/p/pysam/
	The pysam Google code page, containing source code and download instructions

    http://wwwfgu.anat.ox.ac.uk/~andreas/documentation/samtools/contents.html
	The pysam website containing documentation

.. _samtools: http://samtools.sourceforge.net/ 


API
===

.. automodule:: pysam
   :members:
   :undoc-members:


