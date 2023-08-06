########
  natu
########

**Natural units in Python**

.. warning:: This project is currently in a pre-release state.  It will be
   officially released once the unit tests are complete.

natu_ is a free, open-source package to represent physical quantities.  There
are many Python_ packages that deal with units and quantities (see `here
<http://kdavies4.github.io/natu/seealso.html>`_), but natu_ is uniquely
system-independent.  The units are derived from physical constants with
adjustable values and dimensions.  The value of a unit is factored into a
quantity so that the quantity is not "in" any particular unit.  This has the
following advantages:

- **Flexibility**: Different unit systems, including natural units (hence the
  name "natu"), can be represented by simply adjusting the physical constants.
- **Simplicity**: Unit conversion is inherent.  This results in quick
  computations and a small code base.  By default, dimensions and display units
  are tracked to catch errors and for string formatting, respectively.  However,
  this can be turned off to reduce the computational overhead to nearly zero
  while still providing the core features.
- **Scalability**: The values of the base physical constants can scaled to
  prevent exponent overflow, regardless of the units used.
- **Intuitive**: Each unit is a fixed quantity which can be treated as a
  mathematical entity.  A variable quantity is expressed as the product of a
  number and a unit, as stated by BIPM_.
- **Representative**: The structure of the package reflects the way modern units
  are defined: standards organizations such as NIST_ assign values to universal
  physical constants so that the values of units can be determined by physical
  experiments instead of prototypes.

For example, you can do this:

    >>> from natu.units import degC, K
    >>> print(0*degC + 100*K)
    100.0 degC

Please `see the tutorial
<http://nbviewer.ipython.org/github/kdavies4/natu/blob/master/examples/tutorial.ipynb>`_
for more examples.  natu_ incorporates some of the best features of the
existing packages and introduces some novel features.  For the full
documentation, please `visit the main website`_.

Installation
~~~~~~~~~~~~

The easiest way to install natu_ is to use pip_::

    > pip install natu

On Linux, it may be necessary to have root privileges::

    $ sudo pip install natu

License terms and development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

natu_ is published under a `BSD-compatible license
<https://github.com/kdavies4/natu/blob/master/LICENSE.txt>`_.  Please share any
improvements you make, preferably as a pull request to the ``master`` branch of
the `GitHub repository`_.  There are useful development scripts in the `hooks
folder <https://github.com/kdavies4/natu/blob/master/hooks/>`_.  If you find a
bug, have a suggestion, or just want to leave a comment, please `open an issue
<https://github.com/kdavies4/natu/issues/new>`_.


.. _Python: http://www.python.org/
.. _Python Standard Library: https://docs.python.org/3/library/
.. _GitHub repository: https://github.com/kdavies4/natu
.. _NIST: http://www.nist.gov/
.. _BIPM: http://www.bipm.org/
.. _pip: https://pypi.python.org/pypi/pip
.. _degree Celsius (degC): http://en.wikipedia.org/wiki/Celsius
.. _decibel (dB): http://en.wikipedia.org/wiki/Decibel
.. _coherent relations: http://en.wikipedia.org/wiki/Coherence_(units_of_measurement)
.. _statcoulomb: http://en.wikipedia.org/wiki/Statcoulomb
.. _math: https://docs.python.org/3/library/math.html
.. _numpy: http://numpy.scipy.org/
.. _visit the main website: http://kdavies4.github.io/natu/
