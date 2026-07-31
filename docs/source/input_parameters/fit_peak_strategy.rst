fit_peak_strategy
~~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   fit_peak_strategy = auto

**Meaning**
   Controls how detected SED peaks share a fitting window.

   ``independent`` fits one peak in each valley-bounded local window.
   ``joint`` groups peaks whose expanded half-height supports overlap.
   ``auto`` uses a stricter overlap test and otherwise keeps peaks
   independent. Both joint modes avoid the unreliable global grouping that
   can arise from overlapping prominence-base intervals.

**Default**
   ``auto``.

**Diagnostics**
   The console and ``<out_files_name>_LORENTZ-<q-index>.baseline`` report the
   resolved strategy, interval, and number of fitted samples for every
   cluster.

**Related parameters**

- :doc:`fit_baseline_model <fit_baseline_model>`
- :doc:`fitting_function <fitting_function>`
- :doc:`peak_min_significance <peak_min_significance>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
