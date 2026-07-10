#!/usr/bin/env python
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
    r"| |\/| | | | | |   | |   | |_) |   / _ \   | |     |  _|",
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
    print(f"{_BANNER_INDENT}{'=' * _BANNER_WIDTH}")


def _show_help():
    _print_banner()
    print(r"""
USAGE:
    mdtrace [input.in]
    mdtrace -h

DESCRIPTION:
    mdtrace extracts multiple physical observables from a single MD trajectory:

      method = sed   →  Phonon spectral energy density + Lorentzian fitting
      method = dsf   →  Dynamic structure factor S(Q,ω) (neutron / X-ray)
      method = eels  →  Electron energy-loss spectra  [coming soon]

    Supported MD formats: GPUMD, LAMMPS.

    If no input file is given, defaults to 'input.in'.

── Control ───────────────────────────────────────────────────────

    action = thinking      # auto-detect progress (recommended!)
    action = compute       # force re-compute
    action = plot          # force re-plot
    action = fit           # force re-fit (SED only)

    method = sed           # phonon SED
    method = dsf           # dynamic structure factor

    backend = numpy        # CPU (default)
    backend = cupy         # GPU  [coming soon]

── thinking mode ──────────────────────────────────────────────────

    thinking mode automatically detects what has been done and
    runs the next missing step:

      No HDF5?         → compress + compute + plot + fit
      No .SED / .dsf?  → compute + plot + fit
      No fit data?     → plot + fit
      All done?        → reports complete, suggests re-run actions

    Write your input.in once, then just run:

        mdtrace input.in

    It will progress step by step each time you run it.

── Quick start ───────────────────────────────────────────────────

    # SED computation
    mdtrace input.in       # method=sed, action=thinking

    # DSF computation
    mdtrace input.in       # method=dsf, action=thinking

    # Force re-compute
    mdtrace input.in       # action=compute

REFERENCES:
    [1] Liang et al., J. Appl. Phys. 138, 075101 (2025).  [original pySED / SED]
    [2] Thomas et al., Phys. Rev. B 81, 081411 (2010).    [SED method]
    [3] Van Hove, Phys. Rev. 95, 249 (1954).              [DSF theory]
    [4] Squires, Intro to Thermal Neutron Scattering (2012).
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
    print(f"  Input: {input_file}\n")

    # ── parse ──
    params = read_input(input_file)

    # ── go ──
    run_pipeline(params)


if __name__ == "__main__":
    main()
