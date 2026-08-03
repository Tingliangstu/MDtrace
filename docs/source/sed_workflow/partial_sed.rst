Partial SED
===========

Partial SED separates the total kinetic-energy-weighted spectrum by chemical
element and Cartesian direction. It remains eigenvector-free; it indicates
which species and directions contribute to a feature but does not assign a
normal mode.

Generate partial components
---------------------------

Partial data must be requested during numerical computation:

.. code-block:: text

   action          = compute
   method          = sed
   output_partial  = 1

MDtrace writes one ``x``, ``y``, and ``z`` SED matrix for every element under
``<out_files_name>_partial_SED/``. Their sum reproduces the total SED written
to ``<out_files_name>.SED``.

Select a component later
------------------------

During plotting or fitting, select an element alone to sum its three Cartesian
components, or add one direction:

.. code-block:: text

   action = plot
   plot_partial_SED = O

   # or select only oxygen y motion
   plot_partial_SED = O y

The element symbol must match the mass-to-element mapping inferred during
computation. See :doc:`../input_parameters/output_partial` and
:doc:`../input_parameters/plot_partial_SED`.

Fitting partial spectra
-----------------------

A selected partial SED can be fitted with the same local peak-detection and
line-shape workflow as the total SED. The partial lifetime summary figure is
placed beside the selected partial dispersion. Numbered fit figures and
lifetime tables still use the shared ``Fitting-Qpoint/`` and ``Lifetime/``
directories. Preserve an existing total-SED fit before replacing it with
partial-SED results.

See :doc:`output_files` for the exact directory layout.
