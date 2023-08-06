Stormtracks
===========

**Warning, this project is in Alpha, it will be hard to get working and you can't trust the documentation!**

The main aim of this project is to develop an algorithm to detect and track tropical cyclones in the `C20 Reanalysis Project <http://www.esrl.noaa.gov/psd/data/gridded/data.20thC_ReanV2.html>`_. The algorithm will then be run against these data looking for trends in the time range of the data, from 1871 to 2013. Currently the algorithm uses vorticity maxima to locate potential candiated for cyclones, and tracks these maxima using a neareat neighbour approach from time frame to time frame. These tracks are then matched to best tracks from the `IBTrACS catalogue <https://climatedataguide.ucar.edu/climate-data/ibtracs-tropical-cyclone-best-track-data>`_, which it is hoped will allow for automated categorisation of these tracks (and the corresponding cyclones) through a machine learning technique: Support Vector Machines (SVMs). 
