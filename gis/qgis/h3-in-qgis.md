# Qgis & H3
*Using Uber's H3 hex grid system in Qgis*

## Preparation

If using Qgis via standard installer open **OSGeo4W shell** and install H3 with pip:

```
pip install H3
```

**OR** if you use **conda** create and install Qgis with H3:

    conda create -n qgis
    conda activate qgis
    conda install qgis
    conda install h3-py
    
    qgis

## Usage

From Qgis:

1. Select a template layer in table of contents to get extent from
   1. Optionally select specific features
2. *Processing tool box >> Open existing script: [h3-grid-from-layer.py][0]* 
3. OR: *Plugins >> Python console >> Open editor >> load script: [h3-grid-from-layer.py][0]* 
4. Edit variables (particularly min/max resolution levels)
5. Run

More info: 
 - https://gis.stackexchange.com/questions/119495/does-qgis-work-with-anaconda
 - https://h3geo.org/

[0]: https://github.com/maphew/code/blob/master/gis/qgis/h3-grid-from-layer.py



## Troubleshooting

Unsolved: how to get Qgis to add user profile to python search path?

Work around: Run OSGeo4W Shell as administrator before running pip. (You might have to uninstall the user space package.)

```
$ pip install h3
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: h3 in c:\users\matt\appdata\roaming\python\python39\site-packages (3.7.3)
```

Related: https://gis.stackexchange.com/questions/395708/missing-optional-dependency-tables-in-qgis

---

The way INPUT is handled seems to have changed across Qgis versions.

```
Traceback (most recent call last):
  File "C:\PROGRA~1/QGIS32~1.1/apps/qgis/./python/plugins\processing\script\ScriptEditorDialog.py", line 228, in runAlgorithm
​    exec(self.editor.text(), _locals)
  File "<string>", line 139, in <module>
  File "C:\PROGRA~1/QGIS32~1.1/apps/qgis/./python/plugins\processing\tools\general.py", line 108, in run
​    return Processing.runAlgorithm(algOrName, parameters, onFinish, feedback, context)
  File "C:\PROGRA~1/QGIS32~1.1/apps/qgis/./python/plugins\processing\core\Processing.py", line 168, in runAlgorithm
​    raise QgsProcessingException(msg)
_core.QgsProcessingException: Unable to execute algorithm
Incorrect parameter value for INPUT
```

