===========
SVGCompress
===========
---------------
Highlights
---------------
SVGcompress is a pure python module for simplifying/compressing svg (Scalable Vector Graphics) files. Have you ever tried to output a plot in vector format (pdf, svg, eps, etc.) and been surprised that your file weighs 10 or 20MB? Needed to submit a vector figure for publication but ran up against the file size limit? Before you try to get away with the old standby of embedding a raster image in your vector and hoping the journal doesn’t notice, try SVGCompress! SVGCompress can help pare down your file size by:

     * Removing tiny polygons - Reduce the number of polygons in your image by removing those below a small threshold size. The size threshold can be based on polygon area or circumference.

     * Simplifying shapes - Reduce the complexity of your polygons using the Ramer–Douglas–Peucker algorithm.

     * Merging adjacent or overlapping shapes - Merging can be accomplished by taking the union of overlapping polygons or through the construction of a minimum convex hull.

     * Optimizing with *Scour* - SVG compress provides a scripting interface for the package *Scour*, which can optimize/sanitize an svg by removing redundant nodes, deleting comments, simplifying node ids and more. See http://pypi.python.org/pypi/scour for details.

----------------
Installation
----------------
*SVGCompress* has only been tested in Python 2.7

*Step 1*: Install *Numpy* and *Shapely*

     * Depending on your environment, pip may have issues installing *Numpy* and *Shapely* (See *Important* below). As a result, I’ve placed these two libraries outside of the *install_requires* list. Please make sure you have these installed through whatever means works for you (*Numpy* can be installed through pip or through their website, *Shapely* can be installed through pip if you run a Windows OS or through an application such as Canopy).

*Step 2*: Install *SVGCompress* through pip::

        $ pip install SVGCompress

Requires the following non-standard libraries:

     * *Numpy*
     * *svg.path*
     * *Shapely*
     * *rdp*
     * *Scour*
     * *lxml*

*Important*
===========
*SVGCompress* depends upon *Shapely*, which requires the GEOS framework (http://trac.osgeo.org/geos). If you operate on Windows, pip will install the required files along with *Shapely*, **but this will NOT happen with other operating systems** (you will see the error *OSError: Could not find library geos_c or load any of its variants* when you try to run). For non-Windows users, the most convenient way of installing the GEOS framework is through a program such as Canopy (free with academic license) or similar IDLE with an included package manager.

----------------
Usage Notes
----------------
Usage of *SVGCompress* is through the class *Compress*, or through the convenience function *compress_by_method*. In addition, a scripting interface to Scour is accessible through the function *optimize_svg*. The function *svg_compress.test* contains usage examples demonstrating all of the compression methods with *compress_by_method*.

compress_by_method API:
=============================
Convenience function for 1-step compression of svg files.

Inputs:

          *filename* (str) - Path to svg file to compress, e.g. 'test_vector.svg'

          *compression_type* (str) - how to carry out the compression. Options are 'delete' (remove polygons by size), 'simplify' (simplify polygons), and 'merge' (merge neighboring or overlapping polygons).

          *curve_fidelity* (int) - All polygons affected by compression (e.g. those that are simplified) need to first be linearized so as to convert smooth curves into a set of discrete coordinates. *curve_fidelity* sets the number of coordinates to use to interpolate a curve. The larger the number, the more computation the code will need to perform. Optional, defaults to 10.

          *outputfile* (str) - Path to output svg. Optional, defaults to 'originalname_compressed.svg'

          *pre_select* (bool) - If True, will perform the compression only on a subset of the polygons in the svg that are below a certain size threshold. Optional, defaults to False.

          *selection_tuple* (tuple) - If pre_select == True, the selection tuple ('criteria', threshold) determines the criteria for selection ('bboxarea' for the area of the bounding box of a polygon, or 'circumference' for its circumference) and the threshold size (e.g. 100). Optional, defaults to ('', '')

          *optimize* (bool) - If True, use package *Scour* to optimize/sanitize compressed svg (e.g. remove redundant nodes, delete id attributes). Optional, defaults to True

          *optimize_options* (dict) - if *optimize* == True, use *optimize_options* to pass args to *vector_utils.optimize_svg*. See *optimize_tothe_max* in *vector_utils.optimize_svg* for default name, value pairs.

          *kwargs* - Depending on the compression type and the pre-selection criteria, additional key word arguments may be required. See *compress_by_merging*, *compress_by_deletion*, and *compress_by_simplification* in class *Compress* for the valid keyword arguments when *compression_type* = 'merge', 'delete', and 'simplify' respectively.

Outputs:

          Compressed svg in the directory given by *outputfile* or in the code directory with the name  'originalname_compressed.svg'.

	  If *optimized* == True, an optimized svg in the directory 'outputfilename_opt.svg'

          A report string outputted to the console will also state some general indicators about the success of the compression, the path of the outputted svg, and the initial and compressed file sizes.

Producing/converting svg graphics
=================================
Producing your figures in svg format can be done through *Matplotlib*. This is especially convenient if you have a graphics editor such as Inkscape (free) or Adobe Illustrator which will allow you to do things such as modify the font and color of text or lines directly in the svg, without having to re-run your code. You can also use Inkscape to convert one of your svg files into an alternate vector format such as pdf or eps.
To allow Inkscape and other svg editing programs to recognize the text in your *Matplotlib* figures as text, you will need to place the following snippet in your code before you save the svg::

	matplotlib.rcParams['svg.fonttype'] = 'none'

This will also prevent SVGCompress from trying to simplify the text in your figure.

--------------
Examples
--------------
The directory SVGCompress/test contains examples of each compression algorithm on three different files: One is a demonstration graphic (test_vector.svg) and the second and third are actual vector plots (map_test.svg, matplotlib_test.svg)

For example, running the following call to *SVGCompress.compress_by_method*::

	compress_by_method(filename = 'test_vector.svg', compression_type = 'merge', 
                                          curve_fidelity = 10, pre_select = True, selection_tuple = ('bboxarea', 300),
                                          epsilon = 5, bufferDistance = 5, operation_key = 'hull')

compresses the test_vector.svg demonstration file from 87 to 14 KB by constructing convex hulls (operation_key = 'hull') around small neighboring polygons (bounding box area < 1000 pixels) to lessen the total number of polygons, using the Ramer–Douglas–Peucker algorithm to simplify them, and then optimizing the resulting svg by using the package *Scour*.

.. image:: https://dl.dropboxusercontent.com/u/35392962/demo_diagram.jpg
   :width: 741
   :height: 435

The 'test_vector series' in the folder 'test' contains examples of other compression routines. Note that these examples were designed to make the changes that occur during compression obvious. For a more subtle example of compression, see the map_test series.

--------------
Version
--------------
0.6 - Not extensively tested. Please email me to let me know of any issues.

Changelog
============
**0.6 (JULY/21/2014)**

	* Added *optimize_svg()* to default import from __init__.py and added the ability to  pass arguments to it to control how to run the optimization.

	* Fixed issue where *optimize_svg()* could not read unicode characters, added support for specifying the source encoding

	* Fixed create_testplot.py to output text in test svgs as text rather than paths

**0.51 (JULY/24/2014)**

	* Moved _get_kb() out of class Compress

	* Moved optimize() out of class Compress to allow it to be called independently

	* Removed numpy and shapely from install_requires and added new installation instructions

**0.50 (JULY/24/2014)**

	* Added optimize functionality using package Scour

	* Switched from built-in package xml to external library lxml for xml parsing

**0.20 (JULY/23/2014)**

	* Substantially expanded docstrings

**0.19 (JULY/22/2014)**

        * Changed compress_by_merging default behavior to group_by_color = True

        * Appended README with critical information on Shapely installation

**0.18 (JULY/22/2014)**

	* Fixed issue with clipping paths - Code previously threw an exception when trying to extract coordinate data from clipping paths

	* Updated README with a usage example

	* Fixed bug in install_requires that crashed installation with pip