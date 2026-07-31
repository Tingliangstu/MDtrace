initial_guess_hwhm
~~~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   initial_guess_hwhm = 0.001

**Meaning**
   Minimum initial equivalent half-width at half maximum (HWHM) used when
   mdtrace starts a Lorentz or DHO fit. The measured half-height width is used
   when it is larger. If fits fail or converge to unreasonable widths, this
   value can help guide the optimizer.

**Default**
   ``0.001``.

**Notes**
   This value has units of THz. It also contributes to the adaptive maximum
   width used to prevent a fitted component from turning into a flat
   background.

   In the SED theory used by mdtrace, the fitted peak is written as a Lorentzian

   .. math::

      \Phi(\mathbf{q},\omega)
      =
      \frac{I}
      {1+\left[(\omega-\omega_c)/\gamma\right]^2},

   where :math:`\gamma` is the HWHM. The PYSED paper defines the lifetime from
   this linewidth as :math:`\tau = 1/(2\gamma)`. In mdtrace output, frequencies
   are handled in THz and lifetimes are written in ps using the code convention
   described in the theory page.

   A reasonable initial HWHM helps the nonlinear fit converge to the physical
   linewidth. If ``initial_guess_hwhm`` is much too small, the fit may lock onto
   a very narrow spike or fail for broadened peaks. If it is much too large, the
   fit can over-broaden nearby peaks or converge slowly. For sharp crystalline
   peaks, values such as ``0.0005`` to ``0.005`` THz are often a useful starting
   range, but the best value depends on the material, temperature, trajectory
   length, and frequency resolution.

   Tune this parameter only after ``peak_height`` and ``peak_prominence`` detect
   the correct peaks. Then check the fitted curve visually before using
   ``lorentz_fit_all_qpoint = 1``.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`peak_height <peak_height>`
- :doc:`peak_prominence <peak_prominence>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
- :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
- :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
- :doc:`modulate_factor <modulate_factor>`
