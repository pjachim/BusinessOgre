# Installation
To install BusinessOgre, simply run:
```
pip install business_ogre
```

If you are working locally on this repo, use editable install from the repo root:
```text
pip install -e .
```

Quick sanity check after install:
```{python}
import business_ogre as ogr

print(ogr.WorkflowBlock)
```

If that prints the class, you are all good.

If import fails, the two common fixes are:
1. Make sure your virtual environment is activated.
2. Re-run install in the same environment where you run Python.