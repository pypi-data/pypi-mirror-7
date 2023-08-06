===============
pylibbvg
===============

This library implements a decoder for a Boldi-Vigna 
graph structure, a highly compressed means of storing
web-graphs.  The library is written in pure C.
It includes a Python interface, and a means to implement
multi-threaded graph algorithms.

Features
===============

* In-memory and on-disk graph storage
* Sequential iteration over graph edges
* Parallel iteration over graph edges
* random access to graph edges

Installation
===============
1. Compile the C library::

    make
    
2. Compile the Cython source code(``Cython`` is assumed to have installed)::

    python setup.py build_ext --inplace    

3. To clean the library::

    python setup.py clean
    make clean
       
Synopsis
===============
To use the library in Python code::

    import bvg
    G = bvg.BVGraph('wb-cs.stanford', 0) # sequential scan
    print 'nodes = ' + str(G.nverts)
    print 'edges = ' + str(G.nedges)
    edges_and_degrees = G.edges_and_degrees()
    for (src, dst, degree) in edges_and_degrees:
        print 'node ' + str(src) + ' has degree ' + str(degree)
        print 'edge: ' + str(src) + ' -> ' + str(dst)

License
===============

GPL version 2.

Copyright by David F. Gleich, 2007-2014
