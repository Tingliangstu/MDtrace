#!/usr/bin/env python
# =============================================================================
#     Copyright 2025-2026 Ting Liang and MDTRACE development team
#     This file is part of MDTRACE.
#     MDTRACE is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     MDTRACE is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     You should have received a copy of the GNU General Public License
#     along with MDTRACE.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================


"""
mdtrace — Molecular Dynamics Trace.

Trace the physics inside your MD trajectory.
"""
import sys
import os

from mdtrace import __version__
from mdtrace.parser import read_input
from mdtrace.pipeline import run as run_pipeline


_LOGO_LINES = (
    r" __  __   ____    _____   ____       _       ____   _____",
    r"|  \/  | |  _ \  |_   _| |  _ \     / \     / ___| | ____|",
    r"| |\/| | | | | |   | |   | |_) |   / _ \   | |     | |",
    r"| |  | | | |_| |   | |   |  _ <   / ___ \  | |___  | |___",
    r"|_|  |_| |____/    |_|   |_| \_\ /_/   \_\  \____| |_____|",
)

_BANNER_INDENT = "  "
_BANNER_WIDTH = max(len(line) for line in _LOGO_LINES)


def _center_banner_line(text):
    """Center one line within the logo block without trailing whitespace."""
    return f"{_BANNER_INDENT}{text:^{_BANNER_WIDTH}}".rstrip()


LOGO = "\n".join(f"{_BANNER_INDENT}{line}" for line in _LOGO_LINES)
TAGLINE = "\n".join(
    _center_banner_line(line)
    for line in (
        f"Molecular Dynamics Trace   v{__version__}",
        "trace the physics inside your MD trajectory",
        "Author: liangting.zj@gmail.com",
    )
)


def _print_banner():
    print(f"\n{LOGO}\n\n{TAGLINE}\n")


def _print_run_summary(input_file, params):
    """Print one aligned panel describing the task about to run."""

    if params.backend == "cupy":
        backend = "CuPy (single GPU)"
    elif params.max_cores == 1:
        backend = "NumPy (1 CPU process)"
    else:
        backend = f"NumPy (up to {params.max_cores} CPU processes)"

    border = f"{_BANNER_INDENT}{'=' * _BANNER_WIDTH}"
    divider = f"{_BANNER_INDENT}{'-' * _BANNER_WIDTH}"
    print(border)
    print(f"{_BANNER_INDENT}🚀 Starting MDtrace task")
    print(divider)
    print(f"{_BANNER_INDENT}Input   : {input_file}")
    print(f"{_BANNER_INDENT}Method  : {params.method.upper()}")
    print(f"{_BANNER_INDENT}Action  : {params.action}")
    print(f"{_BANNER_INDENT}Backend : {backend}")
    print(f"{_BANNER_INDENT}Output  : {params.out_files_name}")
    print(f"{border}\n")


def _show_help():
    _print_banner()
    print(r"""
USAGE:
    mdtrace [input.in]
    mdtrace -h

DESCRIPTION:
    MDtrace 1.0 computes phonon spectral energy density (SED), plots
    reciprocal-space spectra, and fits spectral peaks:

      method = sed   →  SED compute, plot, and Lorentz/DHO fitting

    DSF and EELS are planned extensions and are not part of the
    supported 1.0 workflow.

    Supported MD formats: GPUMD, LAMMPS.

    If no input file is given, defaults to 'input.in'.

── Control ───────────────────────────────────────────────────────

    action = thinking      # auto-detect progress (recommended!)
    action = compute       # always recompute the main numerical output
    action = plot          # plot existing numerical output
    action = fit           # fit existing SED output

    method = sed           # supported 1.0 method

    backend = numpy        # CPU (default)
    backend = cupy         # GPU (optional CuPy installation)

── thinking mode ──────────────────────────────────────────────────

    thinking mode automatically detects what has been done and
    runs the next missing step:

      Text trajectory? → convert once to .mdtrace.nc
      No .SED data?    → compute + plot
      SED exists?      → plot if needed, then fit on the next run
      All done?        → reports complete, suggests re-run actions

    Write your input.in once, then just run:

        mdtrace input.in

    It will progress step by step each time you run it.

── Quick start ───────────────────────────────────────────────────

    # SED computation
    mdtrace input.in       # method=sed, action=thinking

    # Run the compute stage
    mdtrace input.in       # action=compute

    # Fit existing SED output
    mdtrace input.in       # action=fit

REFERENCES:
    [1] Liang et al., J. Appl. Phys. 138, 075101 (2025).  [original pySED / SED]
    [2] Thomas et al., Phys. Rev. B 81, 081411 (2010).    [SED method]
""")
    sys.exit(0)


def _detect_input_file():
    """Resolve input file from CLI args."""
    if len(sys.argv) == 1:
        # try new format first, then legacy
        if os.path.exists("input.in"):
            return "input.in"
        elif os.path.exists("input_SED.in"):
            return "input_SED.in"
        else:
            print("No input.in or input_SED.in found in current directory.")
            print("Run 'mdtrace -h' for help.")
            sys.exit(1)

    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        if arg in ("h", "help", "-h", "--help", "-help"):
            _show_help()
        return sys.argv[1]

    else:
        print("mdtrace takes 0 or 1 argument.")
        print("Run 'mdtrace -h' for help.")
        sys.exit(1)


def main():
    input_file = _detect_input_file()

    if not os.path.exists(input_file):
        print(f"\n  ERROR: file '{input_file}' not found.\n")
        sys.exit(1)

    _print_banner()

    # ── parse ──
    params = read_input(input_file)
    _print_run_summary(input_file, params)

    # ── go ──
    run_pipeline(params)


if __name__ == "__main__":
    main()
