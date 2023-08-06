SVGCompress
===========

SVGcompress is a pure python module for simplifying/compressing svg (Scalable Vector Graphics) files. Have you ever tried to output a plot in vector format (pdf, svg, eps, etc.) and been surprised that your file weighs 10 or 20MB? Needed to submit a vector figure for publication but run up against the file size limit? Before you try to get away with the old standby of embedding a raster image in your vector and hoping the journal doesn’t notice, try SVGCompress! SVGCompress can help pare down your file size by:
     * Removing tiny polygons - Reduce the number of polygons in your image by removing those below a small threshold size. The size threshold can be based on polygon area or circumference.
     * Simplifying shapes - Reduce the complexity of your polygons using the Ramer–Douglas–Peucker algorithm.
     * Merging adjacent or overlapping shapes - Merging can be accomplished by taking the union of overlapping polygons or through the construction of a minimum convex hull.


Installation
============
SVGCompress has only been tested in Python 2.x
Installation should be through pip (pip install SVGCompress)
Requires the following non-standard libraries:
     * Numpy; svg.path; Shapely; rdp


Usage Notes
===========
Usage of SVGCompress is through the class Compress, or through the convenience function compress_by_method. The function svg_compress.test() contains usage examples demonstrating all of the compression methods with compress_by_method.
Producing your figures in svg format can be done through Matplotlib. This is especially convenient if you have a graphics editor such as Inkscape (free) which will allow you to do things such as modify the font and color of text or lines directly in the svg, without having to re-run your code. You can also use this to convert one of your svg files into an alternate vector format such as pdf or eps.


Examples
========
SVGCompress/test contains examples of each compression algorithm on three different files: One is a demonstration graphic (test_vector.svg) and the second and third are actual vector plots (map_test.svg, matplotlib_test.svg)
For example, here is an uncompressed version of test_vector.svg that weighs 87 KB

  .. image:: test/compression_series/uncompressed.jpg

And after convex_hull merging, the size goes down to 30 KB:

  .. image:: test/compression_series/merged_hull.jpg

This is the code for this demonstration::
	compress_by_method(filename, 'merge', curve_fidelity, outputfile, pre_select = True, 
			   selection_tuple = (criterias[0], thresholds[0]), epsilon = epsilon, 
			   bufferDistance = buffer_distance, operation_key = 'hull')


Version
=======
0.18 - Not extensively tested. Please email me to let me know of any issues.