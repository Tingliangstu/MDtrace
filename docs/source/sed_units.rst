SED units and plot conventions
==============================

Public SED quantity
-------------------

MDtrace writes the one-sided spectral energy density per ordinary frequency,

.. math::

   \Phi_f(\mathbf q,f),

in :math:`\mathrm{eV\,THz^{-1}}` (equivalently ``eV/THz``). Every value in a
``<name>.SED`` file and in an element- or direction-resolved partial SED file
uses this unit. The corresponding frequency values in ``<name>.THz`` are in
THz.

The area under a spectrum therefore has units of energy:

.. math::

   E[\mathrm{eV}]
   =
   \int
   \Phi_f(f)[\mathrm{eV\,THz^{-1}}]\,
   df[\mathrm{THz}].

Lorentzian peak amplitudes, ``peak_height``, and ``peak_prominence`` use the
same :math:`\mathrm{eV\,THz^{-1}}` unit. ``peak_min_significance`` is instead
a dimensionless ratio of log-SED prominence to a local robust noise estimate.

Conversion from the internal quantity
-------------------------------------

The time-domain calculation first produces a density per angular frequency,
:math:`\Phi_\omega`, in :math:`\mathrm{J\,s}`. MDtrace converts it once before
writing output:

.. math::

   \Phi_f[\mathrm{eV\,THz^{-1}}]
   =
   \Phi_\omega[\mathrm{J\,s}]
   \frac{2\pi\,10^{12}}
        {1.602176634\times10^{-19}}.

The factor :math:`2\pi` converts angular frequency to ordinary frequency,
:math:`10^{12}` converts the per-hertz density to a per-terahertz density,
and :math:`1.602176634\times10^{-19}` is the exact number of joules in one
electronvolt. The numerical conversion factor is approximately
:math:`3.921769\times10^{31}`.

Dispersion heatmap
------------------

The dispersion heatmap explicitly displays the natural logarithm

.. math::

   \ln\left(
   \frac{\Phi(\mathbf q,\omega)}
        {1\,\mathrm{eV\,THz^{-1}}}
   \right).

The numerator and denominator have the same unit, so their ratio and its
natural logarithm are dimensionless. The ``colorbar_min`` and
``colorbar_max`` parameters are therefore dimensionless natural-log values.
When either limit is ``None``, MDtrace determines it from the minimum or
maximum finite positive SED value after applying the natural logarithm.
Non-positive values cannot be logged and are masked in the heatmap.

The figure retains the conventional spectral notation
:math:`\Phi(\mathbf q,\omega)`, while its numerical frequency axis is ordinary
frequency in THz and its values are the public
:math:`\Phi_f[\mathrm{eV\,THz^{-1}}]` quantity defined above.

The terminal uses the compact equivalent notation
``ln[SED / (eV/THz)] (dimensionless)``. The figure uses the compact label
:math:`\ln\!\left[\mathrm{SED}(\mathbf q,\omega)/
(\mathrm{eV/THz})\right]`; the unit in the denominator implicitly
denotes the
reference value :math:`1\,\mathrm{eV\,THz^{-1}}`.

Single-q spectrum
-----------------

A single-q plot displays the physical quantity, labelled conventionally as
:math:`\Phi(\mathbf q,\omega)`, directly on a logarithmic y-axis. Its tick
values, Lorentzian curves, and fitted amplitudes remain in
:math:`\mathrm{eV\,THz^{-1}}`; the plotted quantity is not replaced by its
natural logarithm. This is why the single-q y-axis carries the physical unit,
whereas the dispersion colorbar is dimensionless.

Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 42 34 24

   * - Quantity or output
     - Displayed value
     - Unit
   * - ``<name>.SED`` and partial SED files
     - :math:`\Phi_f(\mathbf q,f)`
     - :math:`\mathrm{eV\,THz^{-1}}`
   * - Dispersion heatmap color
     - :math:`\ln\left(\Phi_f/(1\,\mathrm{eV\,THz^{-1}})\right)`
     - dimensionless
   * - Single-q spectrum and Lorentzian curves
     - :math:`\Phi_f(\mathbf q,f)` on a logarithmic y-axis
     - :math:`\mathrm{eV\,THz^{-1}}`
   * - ``peak_height`` and ``peak_prominence``
     - SED intensity thresholds
     - :math:`\mathrm{eV\,THz^{-1}}`
   * - ``peak_min_significance``
     - Local log-SED prominence divided by local robust noise
     - dimensionless
   * - ``<name>.THz`` and fitted frequencies
     - ordinary frequency
     - THz
