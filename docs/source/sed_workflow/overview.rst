Overview
========

MDtrace calculates an eigenvector-free, kinetic-energy-weighted spectral
energy density from atomic velocities. The supported 1.1.0 workflow is

.. code-block:: text

   trajectory + basis mapping + Q path
                    |
                    v
            block-averaged SED
                    |
          +---------+----------+
          |                    |
          v                    v
   dispersion/slices     partial decomposition
          |
          v
   peak detection and independent line-shape fits
          |
          v
   frequency-lifetime data and summary figure

The workflow does not require harmonic eigenvectors. Consequently, fitted
features should be interpreted as spectral peaks rather than automatically
assigned phonon branches. Dispersion continuity and a future mode-projected
workflow can provide additional branch information.

Actions
-------

The :doc:`../input_parameters/action` parameter controls the stage:

``thinking``
   Reuse outputs that already exist and run the next missing stage. It does
   not compare the parameters that created an old file with the current
   ``input.in``.

``compute``
   Read the requested trajectory frames, calculate SED, and overwrite the
   main numerical SED outputs.

``plot``
   Read existing numerical SED output and regenerate the requested figures.

``fit``
   Read existing SED output, detect peaks, fit line shapes, and write
   frequency-lifetime results.

Recommended use
---------------

1. Prepare and validate the trajectory and ``basis.in`` mapping.
2. Compute SED along a commensurate Q path.
3. Inspect the dispersion, partial components if requested, and several
   single-Q spectra.
4. Tune peak detection and line-shape settings on selected Q points.
5. Fit all Q points only after the local fits are satisfactory.

Continue with :doc:`preparing_trajectory_basis` or return to the
:doc:`../starting` example.
