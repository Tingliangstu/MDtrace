Tips
====

This page collects small workflow tips for running mdtrace more efficiently.

Use a Run Script
----------------

For repeated calculations, it is convenient to use a small shell script to
switch ``input_SED.in`` between compute mode and plot/fitting mode. This is
especially useful on clusters, where the same folder may be submitted several
times while tuning plotting and Lorentzian fitting parameters.

The older silicon example contains a simple script:
`run_SED.sh <https://github.com/Tingliangstu/mdtrace/blob/main/example/For_old_version_example/Silicon/SED/run_SED.sh>`_.
The idea is:

1. set ``action = compute`` and run mdtrace once to compute ``.SED``, ``.Qpts``,
   and ``.THz`` files;
2. set ``action = plot`` and run mdtrace again to plot the existing SED data;
3. repeat plot or fit mode while tuning ``peak_min_significance``,
   ``peak_height``, ``peak_prominence``, ``lorentz_fit_freq_min``,
   ``lorentz_fit_freq_max``, and related parameters.

A more robust Bash version is:

.. code-block:: bash

   #!/usr/bin/env bash
   set -euo pipefail

   input_file="input_SED.in"

   set_param() {
       local key="$1"
       local value="$2"
       sed -i -E "s|^(${key}[[:space:]]*=[[:space:]]*).*|\\1${value}|" "${input_file}"
   }

   # First run: compute SED from the trajectory.
   set_param action compute
   mdtrace "${input_file}"

   # Second run: read existing SED data and plot or fit.
   set_param action plot
   mdtrace "${input_file}"

This avoids changing a fixed line number. It is safer when comments or new
parameters are added to ``input_SED.in``.

On Windows PowerShell, the same idea can be written as:

.. code-block:: powershell

   $inputFile = "input_SED.in"

   function Set-SedParam($key, $value) {
       $content = Get-Content $inputFile
       $content = $content -replace "^($key\s*=\s*).*", "`${1}$value"
       Set-Content -Path $inputFile -Value $content
   }

   Set-SedParam "action" "compute"
   mdtrace $inputFile

   Set-SedParam "action" "plot"
   mdtrace $inputFile

Keep Compute and Plot Modes Separate
------------------------------------

Use ``action = compute`` when the trajectory, ``basis.in``, q-path, and cell
settings are ready. After SED files are written, use ``action = plot`` or
``action = fit``. This avoids recalculating SED when you only want to tune
figure or fitting parameters.

Publish Documentation with Read the Docs
----------------------------------------

The online manual is built from the files under ``docs/source``. The repository
contains ``.readthedocs.yaml``, so Read the Docs rebuilds and deploys the manual
after documentation changes are pushed to ``main``.

Recommended update workflow:

.. code-block:: bash

   python -m sphinx -b html docs/source docs/_build/html
   git add README.md docs/source .readthedocs.yaml
   git commit -m "Update mdtrace documentation"
   git push

Update ``docs/source/publications.rst`` when a new publication should appear in
the online manual.
