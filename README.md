# auxdata
Module for loading and processing of auxdata (peripheral signals, triggers, videos from triggered camera's),  using VI's from the Bonhoeffer-lab


__Modules for reading .lvd, .eye and .vid files__

---

#### Installation

* Option 1  
First clone repo, then install  
```
git clone https://github.com/pgoltstein/auxdata.git
cd auxdata
pip install .
```
* Option 2  
Install directly from github  
```
pip install git+https://github.com/pgoltstein/auxdata.git
```

#### Update

* Option 1  
Pull latest version of repo, then install  
```
cd auxdata
git pull
pip install .
```

* Option 2  
Uninstall and re-install directly from github  
```
pip uninstall auxdata
pip install git+https://github.com/pgoltstein/auxdata.git
```

---

_to do_  
* auxdata.py
* functionality for load and process aux data
* frame times, stimulus onsets, stim voltage, eye shutters, stimulus shutter, scan onset
* functionality for loading image frame synced .eye and .vid data

---

Version 0.0.1 - April 9, 2020 - Pieter Goltstein
