# MDtrace TODO

## Phonon lifetime convention

- [ ] Review and finalize the lifetime definition derived from the fitted
  Lorentzian linewidth.
  - The fitted parameter is the ordinary-frequency HWHM \(h\), with
    \(\mathrm{FWHM}=2h\).
  - The current output uses \(1/(2\pi h)\), matching dynasor's
    amplitude/correlation lifetime convention.
  - The energy-relaxation lifetime commonly used in phonon transport is
    \(1/(4\pi h)\) when pure dephasing is negligible.
  - Before changing the output, decide whether to report the linewidth and
    explicitly labelled \(T_1\) and \(T_2\) values.
