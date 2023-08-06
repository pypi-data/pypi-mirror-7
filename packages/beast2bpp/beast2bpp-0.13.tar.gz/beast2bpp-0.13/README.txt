The function beast2bpp.scan() converts a a starBeast input file in xml format to bpp format creating 3 files (a control file bpp.ctl, an individual map file bpp.Imap.txt, and a sequence data file bpp.txt). To execute the program use:

import beast2bpp
beast2bpp.scan('input.xml') 

where input.xml is the name of a starBeast xml file in the working directory (or the full path to the file).
Report and bugs to brannala@ucdavis.edu
