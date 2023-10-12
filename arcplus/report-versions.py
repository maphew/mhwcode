r'''
Report ArcGIS Pro's primary library versions
From
<https://support.esri.com/en-us/knowledge-base/faq-what-version-of-python-is-used-in-arcgis-000013224>

Locate ArcGIS Pro's python folder with Everything Search CLI:

    es pro-py
--> C:\ArcGIS\bin\Python\envs\arcgispro-py3

Run:
    C:\ArcGIS\bin\Python\envs\arcgispro-py3\python.exe path\to\arcplus\report-versions.py

--> python:         3.9.16 [MSC v.1931 64 bit (AMD64)]
    matplotlib      3.6.0 
    numpy:          1.20.1
    scipy:          1.6.2 
'''
import sys
import matplotlib
import numpy
import scipy
print(f'python:\t\t{sys.version}')
print(f'matplotlib:\t{matplotlib.__version__}')
print(f'numpy:\t\t{numpy.__version__}')
print(f'scipy:\t\t{scipy.__version__}')
