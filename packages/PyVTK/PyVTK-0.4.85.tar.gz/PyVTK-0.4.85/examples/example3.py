#!/usr/bin/env python

import sys
sys.path = ['..']+sys.path
if sys.version[:3]=='1.5':
    from lib152 import *
else:
    from lib import *

#from pyvtk import *

points = [[0,0,0],[1,0,0],[2,0,0],[0,1,0],[1,1,0],[2,1,0],
          [0,0,1],[1,0,1],[2,0,1],[0,1,1],[1,1,1],[2,1,1],
          [0,1,2],[1,1,2],[2,1,2],[0,1,3],[1,1,3],[2,1,3],
          [0,1,4],[1,1,4],[2,1,4],[0,1,5],[1,1,5],[2,1,5],
          [0,1,6],[1,1,6],[2,1,6]
          ]
vectors = [[1,0,0],[1,1,0],[0,2,0],[1,0,0],[1,1,0],[0,2,0],
           [1,0,0],[1,1,0],[0,2,0],[1,0,0],[1,1,0],[0,2,0],
           [0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1],
           [0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1],
           [0,0,1],[0,0,1],[0,0,1]
           ]
vtk = VtkData(\
        UnstructuredGrid(points,
                         hexahedron=[[0,1,4,3,6,7,10,9],
                                     [1,2,5,4,7,8,11,10]],
                         tetra=[[6,10,9,12],
                                [5,11,10,14]],
                         polygon=[15,16,17,14,13,12],
                         triangle_strip=[18,15,19,16,20,17],
                         quad=[22,23,20,19],
                         triangle=[[21,22,18],
                                   [22,19,18]],
                         line=[26,25],
                         vertex=[24]
                         ),
        PointData(Vectors(vectors),Scalars(range(27))),
        'Unstructured Grid Example'
        )
vtk.tofile('example3')
vtk.tofile('example3b','binary')

VtkData('example3')
