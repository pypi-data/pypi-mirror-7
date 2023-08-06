sep-python
==========

[![Build Status](https://api.travis-ci.org/kbarbary/sep-python.svg?branch=master)](https://travis-ci.org/kbarbary/sep-python)

Soure Extraction and Photometry for Python

*"... [it's] an SEP: Somebody Else's Problem."  
"Oh, good. I can relax then."*

This is a Python wrapper of the [SEP](https://github.com/kbarbary/sep)
C library. SEP makes available some of the algorithms used in [Source
Extractor](http://www.astromatic.net/software/sextractor) as
stand-alone functions, suitable for wrapping in Python. It's derived directly
from the Source Extractor code base. For details on
what is available, see "Usage" below. A copy of the SEP source code is
bundled with this package; there's no need to separately install the C
library and this will also not conflict with an installed version of the
C library.

Requirements
------------

- Python 2.6+, 3.2+
- numpy

Install
-------

**From conda** (currently linux only)

[![Binstar Badge](https://binstar.org/kbarbary/sep/badges/installer/conda.svg)](https://conda.binstar.org/kbarbary) 
[![Binstar Badge](https://binstar.org/kbarbary/sep/badges/version.svg)](https://binstar.org/kbarbary/sep)

```
conda install -c https://conda.binstar.org/kbarbary sep
```

**From the development version**

Bulding the development verion requires `cython` and a C compiler.
Build and install in the usual place:

```
./setup.py install
```

**Running tests**

Run `./test.py`. Requires `pytest` package. Some tests require a FITS reader
(either `fitsio` or `astropy`).

Usage
-----

**Background estimation**

```python
import sep

# Measure a spatially variable background of some image data
# (a numpy array)
bkg = sep.Background(data)

# ... or with some optional parameters
bkg = sep.Background(data, mask=mask, bw=64, bh=64, fw=3, fh=3)

# The above creates a Background object which you can then use in 
# several ways:

# Evaluate the spatially variable background:
back = bkg.back()  # creates an array, same shape and type as data

# Evaluate the spatially variable RMS of the background:
rms = bkg.rms()  # creates an array, same shape and type as data

# Directly subtract the background from data without allocating any
# new memory:
bkg.subfrom(data)

bkg.globalback  # Global "average" background level
bkg.globalrms  # Global "average" RMS of background
```

**Object detection**

```python
# extract objects from data (second argument is threshold)
objects = sep.extract(data, 1.5 * bkg.globalrms)

# ... or with some optional parameters:
kernel = np.array([[1., 2., 1.],
                   [2., 4., 2.],
                   [1., 2., 1.]])
objects = sep.extract(data, 1.5 * bkg.globalrms, minarea=5, conv=kernel,
                      clean=True, clean_param=1.0, deblend_nthresh=32,
                      deblend_cont=0.005)

# objects is a numpy structured array:
len(objects)  # number of objects
objects['x'][i]  # flux-weighted x-center coordinate of i-th object
...              # ... and many other fields. See objects.dtype.names
```

**Aperture photometry**

The follow examples demonstrate options for circular aperture photometry.

```python
# sum flux in circles of radius=3.0
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0)

# x, y and r can be arrays and obey numpy broadcasting rules
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'],
                                   3.0 * np.ones(len(objects)))

# use a different subpixel sampling (default is 5)
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   subpix=10)

# Specify a per-pixel "background" error (default is zero):
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   err=bkg.globalrms, gain=1.0)

# Use "var" for variance rather than error:
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   var=bkg.globalrms**2, gain=1.0)

# err/var can also be an array:
bkgrms = bkg.rms()  # array, same shape as data
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   err=bkgrms, gain=1.0)

# If your uncertainty array includes Poisson noise from the object,
# leave gain as None (default):
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   err=error_array)

# If your data represent raw counts (not background-subtracted), set only
# gain to get the poisson error:
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   gain=1.0)

# Apply a mask (same shape as data). Pixels are igored where mask is True.
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   mask=mask)

# Perform local background subtraction in an annulus between 6 and 8 pixel
# radius. Pixels in the background annulus are not subsampled and any masked
# pixels in the annulus are completely igored rather than corrected.
# Inner and outer radii can also be arrays: 
flux, fluxerr, flag = sep.apercirc(data, objects['x'], objects['y'], 3.0,
                                   mask=mask, bkgann=(6., 8.))

# Convert flag array to boolean for specific flags:
sep.istruncated(flag)  # True where aperture was truncated by image edge.
sep.hasmasked(flag)    # True where aperture includes masked pixels.
```

**Mask image regions**

```python
# Create a boolean array with elliptical regions set to True:
mask = np.zeros(data.shape, dtype=np.bool)
sep.mask_ellipse(mask, objects['x'], objects['y'],
                 cxx=objects['cxx'], cyy=objects['cyy'], cxy=objects['cxy'],
                 scale=3.)
```

License
-------

The license for all parts of the code derived from SExtractor is
LGPLv3. The license for code not derived from SExtractor is MIT. The
license for the package as a whole is therefore LGPLv3. The license
for each file is explicitly stated at the top of each file and the
full text of the licenses can be found in `licenses`.


Development Note
----------------

The SEP library and this wrapper are being developed in parallel. Any
changes to SEP are made in the `sep` repository and then manually
copied to this repository.