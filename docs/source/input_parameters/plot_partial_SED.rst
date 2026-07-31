plot_partial_SED
~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   plot_partial_SED = O
   plot_partial_SED = O x

**Meaning**
   Plot the partial SED for an element symbol. With only the element, mdtrace
   sums x, y, and z directions. With a direction, mdtrace plots only that
   component.

**Default**
   ``0``.

**Allowed directions**
   ``x``, ``y``, or ``z``.

**Notes**
   Requires partial files generated earlier with ``output_partial = 1``. For
   example, ``plot_partial_SED = O y`` reads
   ``<out_files_name>.SED_O_y``.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`output_partial <output_partial>`
- :doc:`plot_cutoff_freq <plot_cutoff_freq>`
- :doc:`plot_interval <plot_interval>`
- :doc:`plot_color <plot_color>`
- :doc:`colorbar_min <colorbar_min>`
