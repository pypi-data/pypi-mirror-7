Stormtracks
===========

**Warning, this project is in Alpha, it will be hard to get working and you can't trust the documentation!**

The main aim of this project is to develop an algorithm to detect and track tropical cyclones in the `C20 Reanalysis Project <http://www.esrl.noaa.gov/psd/data/gridded/data.20thC_ReanV2.html>`_. The algorithm will then be run against these data looking for trends in the time range of the data, from 1871 to 2013. Currently the algorithm uses vorticity maxima to locate potential candiates for cyclones, and tracks these maxima using a neareat neighbour approach from time frame to time frame. These tracks are then matched to best tracks from the `IBTrACS catalogue <https://climatedataguide.ucar.edu/climate-data/ibtracs-tropical-cyclone-best-track-data>`_, which it is hoped will allow for automated categorisation of these tracks (and the corresponding cyclones) through a machine learning technique: Support Vector Machines (SVMs). 

Installing and Running
----------------------

The project is `hosted on PyPI <https://pypi.python.org/pypi?name=stormtracks&:action=display>`_, and can be installed using:

::

    pypi install stormtracks

The code is `hosted on github <https://github.com/markmuetz/stormtracks>`_.

To run the analysis, you will first need to download some C20 Reanalysis data and the ibtracs data (`download_2005.py <https://raw.githubusercontent.com/markmuetz/stormtracks/master/stormtracks/demo/download_2005.py>`_):

.. code:: python

    import stormtracks.download as dl

    # Data will be saved to ~/stormtracks/data/
    dl.download_ibtracs()
    # N.B. one year is 4.2 GB of data! This will take a while.
    # It will download 3 files, two with the wind velocities at ~sea level (u9950/v9950)
    # and Pressure at Sea Level (prmsl).
    dl.download_full_c20(2005)

To run some analysis (`run_analysis_2005.py <https://raw.githubusercontent.com/markmuetz/stormtracks/master/stormtracks/demo/run_analysis_2005.py>`_):

.. code:: python

    import datetime as dt

    import pylab as plt

    from stormtracks.c20data import C20Data
    from stormtracks.ibtracsdata import IbtracsData
    from stormtracks.detect import GlobalCyclones
    from stormtracks.match import match2

    import stormtracks.plotting as pl

    # Create a wrapper for the C20 Reanalysis data.
    c20data = C20Data(2005)
    c20data.first_date()
    # Plot PSL for 1st of Jan 2005.
    pl.plot_on_earth(c20data.lon, c20data.lat, c20data.psl)
    plt.show()

    # Plot vorticity for 1st of Jan 2005.
    pl.plot_on_earth(c20data.lon, c20data.lat, c20data.vort)
    plt.show()

    # Load IBTrACS data for 2005.
    ibtracs = IbtracsData()
    best_tracks = ibtracs.load_ibtracks_year(2005)

    # Run the analysis for 2005.
    gdata = GlobalCyclones(c20data, ensemble_member=0)
    gdata.track_vort_maxima(dt.datetime(2005, 6, 1), dt.datetime(2005, 7, 1))

    # Match the generated tracks agains the best tracks.
    matches = match2(gdata.vort_tracks_by_date, best_tracks)
    good_matches = [ma for ma in matches.values() if ma.av_dist() < 5 and ma.overlap > 6]

    for gm in good_matches:
        pl.plot_match(gm, None)
        plt.show()
