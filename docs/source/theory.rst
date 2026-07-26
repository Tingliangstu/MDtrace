SED theory and implementation
=============================

MDtrace implements the eigenvector-free spectral energy density (SED)
expression used by Thomas *et al.* [Thomas2010]_ and the PYSED article
[Liang2025]_.

Eigenvector-free SED
--------------------

For basis atom :math:`b`, repeated unit cell :math:`l`, Cartesian direction
:math:`\alpha`, and equilibrium unit-cell reference position
:math:`\mathbf r_0(l)`,

.. math::

   \Phi'(\mathbf q,\omega)
   =
   \frac{1}{4\pi\tau_0N_T}
   \sum_{\alpha=1}^{3}\sum_{b=1}^{n}m_b
   \left|
   \int_0^{\tau_0}
   \sum_{l=1}^{N_T}
   \dot u_\alpha(l,b,t)
   \exp\left[
   i\mathbf q\cdot\mathbf r_0(l)-i\omega t
   \right]dt
   \right|^2.

:math:`n` is the number of basis atoms, :math:`N_T` is the number of
repeated unit cells, :math:`m_b` is the basis-atom mass, and :math:`\tau_0`
is the duration of one trajectory block.

Discrete Fourier transform and time step
----------------------------------------

NumPy and CuPy FFTs evaluate a discrete sum. The continuous integral is
approximated by

.. math::

   \int_0^{\tau_0}v(t)e^{-i\omega t}dt
   \approx
   \Delta t
   \sum_{j=0}^{N-1}v_j e^{-i\omega t_j}.

Because SED contains the squared magnitude of this integral, the numerical
normalization contains :math:`\Delta t^2`:

.. math::

   \Phi'_\mathrm{discrete}
   =
   \frac{\Delta t^2}{4\pi\tau_0N_T}
   \sum_{\alpha,b}m_b
   \left|
   \operatorname{FFT}\left[
   \sum_l
   \dot u_\alpha(l,b,t)
   e^{i\mathbf q\cdot\mathbf r_0(l)}
   \right]\right|^2.

The PYSED article writes the continuous integral explicitly. The dynasor
implementation [Dynasor2025]_ likewise multiplies the squared FFT by
``delta_t**2``.

Units
-----

MDtrace converts velocity to :math:`\mathrm{m\,s^{-1}}`, time to seconds,
and mass to kilograms. Therefore,

.. math::

   \Delta t\sum v
   :
   \quad
   \mathrm{s}\,
   \frac{\mathrm m}{\mathrm s}
   =
   \mathrm m,

and

.. math::

   \frac{
   m_b\left|\Delta t\sum v\right|^2
   }{\tau_0}
   =
   \frac{\mathrm{kg\,m^2}}{\mathrm s}
   =
   \mathrm{J\,s}.

The symbol :math:`m_b` denotes atomic mass. The :math:`\mathrm{m^2}` in the
unit is metre squared and comes from the squared time-integrated velocity.

Energy-preserving one-sided spectrum
------------------------------------

MDtrace folds positive and negative frequencies:

.. math::

   \Phi_+(\omega_k)
   =
   \begin{cases}
   \Phi(0), & k=0,\\
   \Phi(+\omega_k)+\Phi(-\omega_k), & k>0.
   \end{cases}

This preserves two-sided spectral power while writing only non-negative
frequencies. For a classical equilibrium crystal and a commensurate Q point,

.. math::

   \int_0^\infty
   \Phi_+(\mathbf q,\omega)d\omega
   \approx
   \frac{1}{2}N_\mathrm{bands}k_BT,
   \qquad
   N_\mathrm{bands}=3n.

MDtrace writes ordinary frequency in THz and SED in :math:`\mathrm{J\,s}`.
Since

.. math::

   d\omega
   =
   2\pi\,10^{12}\,df_\mathrm{THz},

an effective SED temperature can be checked with

.. code-block:: python

   import numpy as np

   k_B = 1.380649e-23
   prefix = "CNT"
   q_index = 1
   n_basis = 2

   frequency_thz = np.loadtxt(prefix + ".THz")
   sed = np.loadtxt(prefix + ".SED")[:, q_index]
   energy_joule = (
       2 * np.pi * 1.0e12
       * np.trapz(sed, frequency_thz)
   )
   temperature_sed = energy_joule / (
       0.5 * (3 * n_basis) * k_B
   )
   print(f"SED temperature: {temperature_sed:.2f} K")

Finite sampling, constraints, removed center-of-mass motion, and Γ-point
translational modes cause deviations. At Γ, the three translational modes may
be absent, giving approximately :math:`(3n-3)k_BT/2`.

Commensurate Q points
---------------------

Write the supercell and primitive-cell matrices as

.. math::

   \mathbf S=\mathbf P\mathbf p.

A reduced wave vector is commensurate when

.. math::

   \mathbf q_\mathrm{red}\mathbf P^T\in\mathbb Z^3.

For a path

.. math::

   \mathbf q(f)
   =
   \mathbf q_\mathrm{start}
   +f\left(
   \mathbf q_\mathrm{end}-\mathbf q_\mathrm{start}
   \right),
   \qquad 0\leq f\leq1,

MDtrace retains the fractional values satisfying that integer condition.
Larger supercells provide denser exact Q sampling. Arbitrary incommensurate
points can introduce aliasing and should not be used for quantitative SED.

Calculation logic
-----------------

``Phonon.py`` follows this sequence:

1. Read the basis mapping and prepare basis IDs, masses, type mappings, and Q
   points once.
2. Select serial NumPy, persistent multiprocessing, or single-GPU CuPy.
3. Read one requested NetCDF trajectory block.
4. Average the reference-atom positions to obtain one equilibrium unit-cell
   reference vector for each repeated cell in the block.
5. Construct :math:`\exp(i\mathbf q\cdot\mathbf R_l)`.
6. Use ``tensordot`` to contract the unit-cell axis while keeping time, Q
   point, and Cartesian direction.
7. Apply the FFT along time and multiply :math:`|\mathrm{FFT}|^2` by mass.
8. Retain type/x/y/z components or sum the total SED.
9. Apply :math:`\Delta t^2/(4\pi\tau_0N_T)` and accumulate the block online.
10. Average blocks, fold positive and negative frequencies, and write the
    positive-frequency output.

The CPU path creates one process pool for the complete SED calculation. Each
trajectory block is copied once into shared memory, and workers receive only
small Q-point ranges. The CuPy path uploads one block, checks estimated device
memory before the first block, and frees its memory pools after completion.

Partial SED
-----------

With :math:`\mathcal B_s` denoting basis atoms of species :math:`s`,

.. math::

   \Phi'_{s,\alpha}(\mathbf q,\omega)
   =
   \frac{1}{4\pi\tau_0N_T}
   \sum_{b\in\mathcal B_s}m_b
   \left|
   \int_0^{\tau_0}
   \sum_l
   \dot u_\alpha(l,b,t)
   e^{i\mathbf q\cdot\mathbf r_0(l)-i\omega t}dt
   \right|^2.

The total is recovered by summing over species and Cartesian directions.

Linewidth convention
--------------------

The current fit model is

.. math::

   L(f)
   =
   \frac{I}{
   1+\left[(f-f_c)/h\right]^2
   },

where :math:`h` is HWHM in THz and FWHM is :math:`2h`. The current lifetime
file retains MDtrace's existing HWHM conversion convention. Users needing a
quantitative energy-relaxation lifetime should verify whether their reference
uses angular-frequency HWHM, angular-frequency FWHM, ordinary-frequency HWHM,
or ordinary-frequency FWHM. Pure dephasing can also broaden a line without the
same energy-relaxation rate.

References
----------

.. [Liang2025] T. Liang, W. Jiang, K. Xu, H. Bu, Z. Fan, W. Ouyang, and
   J. Xu, "PYSED: A tool for extracting kinetic-energy-weighted phonon
   dispersion and lifetime from molecular dynamics simulations," *Journal of
   Applied Physics* **138**, 075101 (2025).
   https://doi.org/10.1063/5.0278798

.. [Thomas2010] J. A. Thomas, J. E. Turney, R. M. Iutzi, C. H. Amon, and
   A. J. H. McGaughey, "Predicting phonon dispersion relations and lifetimes
   from the spectral energy density," *Physical Review B* **81**, 081411
   (2010). https://doi.org/10.1103/PhysRevB.81.081411

.. [Dynasor2025] E. Berger *et al.*, "Dynasor 2: From simulation to
   experiment through correlation functions," *Computer Physics
   Communications* **316**, 109759 (2025).
   https://doi.org/10.1016/j.cpc.2025.109759
