===========
PyMethyl
===========

PyMethyl is a package that is a quick and dirty way to find methylation
patterns within the human genome. It is useful in determining the methylation
patterns for promoter regions and transcribable regions for different genes. 
The package has a foundation on the package cruzdb, pysam, and the local BLAST
alignment tool via NCBI. These packages are used to gather the information about
the genes you want to analyze. Then this package sorts out the bam files of the 
genome to look for methylation. All functions needed are accessible by typing
"from pymethyl.functions import *". Some functions are able to be customized 
for peak calling and mapping quality. An example may look like this.

An example may look like this::

    #!/usr/bin/env python

>>> from pymethyl.functions import *
>>> info = regionInfo()
What is the name of the gene you are interested in?: NUF2
What is the reference genome you are searching? Example: hg18 : hg18
Do you want to search the Promoter Region? (Y/N): Y
Here is the promoter region data
>>> file_handle = open("NUF2_Promoter.txt", "w")
>>> file_handle.write(info)
>>> file_handle.close()
>>> makeDatabase()
Choose the text file to make into a database
Name of your Database: NUF2
NCBI Database type, leave empty if unsure: nucl
Which database will you get the sequences from Example: hg18 : hg18
Your database is processing, not to worry, this can take some time.
Done
>>> findMethylation()
Chose the data file which holds results from bam file. This should be a text file.
Type the gene name you are looking at. Example: 'ACACA' : NUF2
What is the mapping quality needed for a read to be significant. Enter 0 for every read: 30
Type the amount of coverage you would like have a sequence considered methylated. Example: 5 (which means regions have 5 overlapping sequences are saved) : 5
Done
Your results are in your desktop folder named Methylated Results
>>> blastIt()
Enter the type of BLAST that you want to perform. Types of BLAST can be found on the NCBI website. Example: blastn : blastn
Name of the database you are searching. Would be the database you made with the MakeDatabase() function. Example: Sequences : NUF2
Went through 1 data files
Counted 1 events
>>> getResults()
Type the methylated gene you are looking at: NUF2
There are 1 events of methylation within this region.

functions
=========

	* Functions is the only module that needs to be imported. This is because Functions is the GUI for all of the other modules.
	  Realize that this process has to be done in order. This documentation will walk through what each function does and how
	  to maneuver through the interface in order to get your methylated results. We will start with getting the genetic information.

	  
regionInfo()
----------------------------------
"""This function is based off of the cruzdb package. This is a more friendly user interface to gather information that the cruzdb
package already gets. This function looks at the transcribable region or the promoter region of the named gene. The idea is to put 
in your gene name, the database you would want to search that gene in, and the region that you are interested in looking at.
For example we are going to pick the gene NUF2 and database hg18. You can find different databases on the UCSC genomic browser website. 
The databases are under assembly.
<https://genome.ucsc.edu/cgi-bin/hgTables?command=start>"""

>>> regionInfo()
What is the name of the gene you are interested in?: NUF2
What is the reference genome you are searching? Example: hg18 : hg18
Do you want to search the Promoter Region? (Y/N): Y
Here is the promoter region data
'NUF2\t1\t161556346\t161557346'

This is the output for the regionInfo function. It tells you the gene name, chromosome, starting position, and ending position.
of the transcribable region. This information is necessary to make a database as well as extract information from the bam file. Lets 
save this information to a text file called NUF2_Promoter.txt on our desktop. It is important that the files are text files because that's
what this program is compatible with.


makeDatabase()
----------------------------------
"""This function is based off the cruzdb package. This is a more user friendly interface to gather information that can be transformed
into a working database for the local BLAST tool. The result of this function is a blast-able database which will be stored in the blast
folder created on your desktop. What you name your database is important so make sure to remember it."""

>>> makeDatabase()
Choose the text file to make into a database 
##At this point in the function, python will open a root window for you to choose a file. This file is going to be our NUF2_Promoter.txt or 
##that we created via the regionInfo() function. When you find this file in the GUI window, double click it.
Name of your Database: NUF2
##Now choose the name for your database. I chose Promoters but you can pick anything.
NCBI Database type, leave empty if unsure: nucl
##Now choose the type of database you intend to create. I chose nucl because that signifies a nucleotide database. The options for this
##can be found on the NCBI website. If left empty, nucl is automatically chosen.
##<http://www.ncbi.nlm.nih.gov/books/NBK1763/>
Which database will you get the sequences from Example: hg18 : hg18
##Now choose the reference database from UCSC that you would like to search. Options for this can be found via the UCSC website.
##<https://genome.ucsc.edu/cgi-bin/hgTables?command=start>.
Your database is processing, not to worry, this can take some time.
Done
##Your database can be found in the blast folder you downloaded from NCBI and it is in the db subdirectory.


extractBamFile()
----------------------------------
"""This function takes the input of a file created by regionInfo. The format of the input file must be gene name \t chromosome \t start
position \t end position \n. This function also takes an input file of a sorted bam file with it's bai file in the same directory. The
function also takes the sample name which will be the name of the directory created and the read lengths. For methylation data this can
be reads of 50bp - 250bp. With that user input, the program will create a directory with a file named for the gene that it represents.
The files inside of the directory contain all of the reads and format them as start position \t end position \t mapping quality \t sequence.
This file is the input file for findMethylation function.

>>> extractBamFile()
Choose the data file which holds the information of the gene that you are looking for. Format gene name, chromosome, start position, end position.
##Here you would choose the input file that is formatted like described above.
Choose the BAM file that you are extracting reads from.
##Choose the BAM file but make sure that the bai file is in the same directory as the bam file
What is the name of the sample the reads are coming from: Sample1
##This can be named anthing. It is just what the directory will be called that shows up on your desktop
What is the length of each read's sequence: 50
##The reads that are contained within the bam file have a length and they are usually 50-250bp long. This number is necessary as the 
##BAM file does not contain information about the end position but it is found using the read length.



findMethylation()
----------------------------------
"""This function is original to this package and doesn't depend on any other packages. It is a quick and dirty algorithm that finds
the places of hypermethylation. It can be customized depending on what you decide is significant. It works by taking all of the sequences
in the information file that you give it and finds areas where there is X (a number you choose) number of overlapping sequences. It then
prepares these regions and sequences in a file that the blastIt function can blast for statistical significance."""

>>> findMethylation()
Chose the data file which holds results from bam file. This should be a text file.
##A GUI window should appear allowing you to choose a file. This file should be the text file that resulted in running the function that
##extracts information out of the bam file.
Type the gene name you are looking at. Example: 'ACACA' : NUF2
##Self Explanatory. Just enter in the gene you are looking at.
What is the mapping quality needed for a read to be significant. Enter 0 for every read: 30
##Each read in a bam file has a mapping quality. You can decide to make this higher or lower. The higher the mapping quality, the better
##quality of data you will have. However, the higher the mapping quality, the more sequences are rejected and the amount of data decreases.
Type the amount of coverage you would like have a sequence considered methylated. Example: 5 (which means regions have 5 overlapping 
sequences are saved) : 5
##This is where the user determines the amount of overlap or peak coverage that they would like in order to warrant a significant 
##methylation event. The program will then only find regions where that amount of coverage was found.
Done
Your results are in your desktop folder named Methylated Results
##If you see the message below, it is because your mapping quality stipulation was to high, your amount of coverage was too high
##or there are not enough sequences for a significant methylation event to of been counted. 
Not Enough Reads To Warrant Significant Methylation
##If there simply is no methylation within your samples then you will get the message
No Methylated Detected, File Removed
##If your input file contains nothing, you will get the message
File contained no sequences


blastIt()
----------------------------------
"""This function takes the output files from the findMethylation function and blast the sequence against the locally made database to
ensure that the formulated sequence actually belongs to a gene. We make up the database by the makeDatabase function. The output of this
function is a file for every single methylated sequence. The files contain an alignment of the sequence to the reference gene, as well
as the E-value signifying how likely that sequence belongs to that gene."""

>>>blastIt()
Enter the type of BLAST that you want to perform. Types of BLAST can be found on the NCBI website. Example: blastn : blastn
##This feature allows the user to do a blast for nucleotides, other options are blastp etc. Options can be found on the NCBI website.
Name of the database you are searching. Would be the database you made with the makeDatabase() function. Example: Sequences : NUF2
##Remember this was the name of the database that we created using makeDatabase function.
Went through 1 data files
##Tells you how many files were looked at
Counted 1 events
##Tells you how many events of methylation occurred in all those files.


*****Some users may find it necessary to completely change the command for blasting. To do this, you must go into the source code and change it.*****


getResults()
----------------------------------
"""This function counts the number of methylated events occurring in the region. It is nothing more than a counter function. It does not
actually do anything to the data."""
>>> getResults()
##It is important you spell the gene correct and exactly the way it appears.
Type the methylated gene you are looking at: NUF2
There are 1 events of methylation within this region.



Tests
=========
"""The tests are located in the tests folder. The require interaction from the user."""

THIS IS A RUN OF THE TEST

When the program asks you to choose a file. Pick the NUF.txt file that will appear on the screen.

>>> 
test_1 (__main__.TestSequenceFunctions) ... What is the name of the gene you are interested in?: NUF2
What is the reference genome you are searching? Example: hg18 : hg18
Do you want to search the Promoter Region? (Y/N): Y
Here is the promoter region data
ok
test_2 (__main__.TestSequenceFunctions) ... Choose the text file to make into a database
Name of your Database: NUF2
NCBI Database type, leave empty if unsure: nucl
Which database will you get the sequences from Example: hg18 : hg18
Your database is processing, not to worry, this can take some time.
Done
ok
test_3 (__main__.TestSequenceFunctions) ... Choose the data file which holds the information of the gene \
that you are looking for. Format gene name, chromosome, start position, end position.
Choose the BAM file that you are extracting reads from.
What is the name of the sample the reads are coming from: Sample1
What is the length of each read's sequence: 50
Done
test_4 (__main__.TestSequenceFunctions) ... Chose the data file which holds results from bam file. This should be a text file.
Type the gene name you are looking at. Example: 'ACACA' : NUF2
What is the mapping quality needed for a read to be significant. Enter 0 for every read: 0
Type the amount of coverage you would like have a sequence considered methylated. Example: 5 (which means regions have 5 overlapping sequences are saved) : 5
Done
Your results are in your desktop folder named Methylated Results
ok
test_5 (__main__.TestSequenceFunctions) ... Enter the type of BLAST that you want to perform. Types of BLAST can be found on the NCBI website. Example: blastn : blastn
Name of the database you are searching. Would be the database you made with the MakeDatabase() function. Example: Sequences : NUF2
Went through 1 data files
Counted 1 events
ok
test_6 (__main__.TestSequenceFunctions) ... Type the methylated gene you are looking at: NUF2
ok
test_7 (__main__.TestSequenceFunctions) ... ok

----------------------------------------------------------------------
Ran 7 tests in 52.829s

OK