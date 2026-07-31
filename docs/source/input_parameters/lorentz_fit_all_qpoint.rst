lorentz_fit_all_qpoint
~~~~~~~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   lorentz_fit_all_qpoint = 1

**Meaning**
   Runs Lorentzian fitting for every generated q-point and collects the fitted
   frequencies and lifetimes into the total lifetime output file.

**Default**
   ``0``.

**Notes**
   With ``action = fit``, fitting always runs. With ``action = thinking``,
   fitting runs after the numerical SED data and requested plots exist, but only
   when the requested fit output is still missing.

   Tune the fitting parameters on selected q-points first, then set this
   parameter to ``1`` to fit every q-point.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`peak_height <peak_height>`
- :doc:`peak_prominence <peak_prominence>`
- :doc:`re_output_total_freq_lifetime <re_output_total_freq_lifetime>`
- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
