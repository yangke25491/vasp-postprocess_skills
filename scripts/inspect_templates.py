#!/usr/bin/env python3
"""
VASP file inspection templates — call the relevant function for your file type.
Each inspects the file header and prints structure info without reading all data.
Usage: python inspect_templates.py /path/to/EIGENVAL
"""

import re, os, sys
import numpy as np


def inspect_eigenval(path):
    with open(path) as f:
        lines = f.readlines()
    total = len(lines)
    print("=== EIGENVAL ===")
    for i in range(min(7, total)):
        print(f"  [{i}] {lines[i].rstrip()}")
    # Try to find dims at any reasonable line
    for idx in range(3, min(8, total)):
        parts = lines[idx].strip().split()
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            nkpts, nbands = int(parts[1]), int(parts[2])
            print(f"  NKPTS={nkpts}, NBANDS={nbands}")
            break
    # Find first k-point
    for i in range(min(10, total)):
        parts = lines[i].strip().split()
        if len(parts) == 4 and i >= 5:
            print(f"  First k-point [{i}]: {lines[i].strip()}")
            if i + 1 < total:
                print(f"  First band [{i+1}]: {lines[i+1].strip()}")
            break


def inspect_chgcar_header(path):
    """Read CHGCAR header + grid size without loading entire file."""
    with open(path) as f:
        # Read POSCAR header (first ~50 lines)
        for i in range(15):
            line = f.readline()
            if not line:
                break
        # Read until we find 3 integers (grid) or augmentation
        while True:
            line = f.readline()
            if not line:
                break
            parts = line.strip().split()
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                ngx, ngy, ngz = map(int, parts)
                print(f"Grid: {ngx} x {ngy} x {ngz} = {ngx*ngy*ngz}")
                expected_data_lines = int(np.ceil(ngx * ngy * ngz / 5))
                # f.tell() to estimate remaining
                print(f"Expected data lines: ~{expected_data_lines}")
                break
            if 'augmentation' in line:
                print(f"augmentation found at byte {f.tell()}")

    # Now estimate from end of file
    total_size = os.path.getsize(path)
    print(f"File size: {total_size / 1024 / 1024:.1f} MB")


def inspect_procar(path):
    with open(path) as f:
        lines = f.readlines()
    total = len(lines)
    print("=== PROCAR ===")
    for i in range(4):
        print(f"  [{i}] {lines[i].rstrip()}")

    h = lines[1].strip()
    nk = int(re.search(r'# of k-points:\s+(\d+)', h).group(1))
    nb = int(re.search(r'# of bands:\s+(\d+)', h).group(1))
    ni = int(re.search(r'# of ions:\s+(\d+)', h).group(1))
    print(f"  nkpts={nk}, nbands={nb}, nions={ni}")

    for i in range(5, min(20, total)):
        line = lines[i].strip()
        if line.startswith('ion') and 's' in line and 'tot' in line:
            cols = line.split()
            print(f"  Columns ({len(cols)}): {cols}")
            print(f"  Orbitals: {cols[1:-1]}")
            break

    has_spin_down = any('spin down' in l.lower() for l in lines)
    print(f"  Spin down section: {has_spin_down}")


def inspect_wavecar(path):
    try:
        from vaspwfc import vaspwfc
        wfc = vaspwfc(path)
        print("=== WAVECAR ===")
        print(f"  nbands={wfc._nbands}, encut={wfc._encut:.1f}")
        print(f"  kvecs: {wfc._kvecs.shape}, range=[{wfc._kvecs.min():.4f}, {wfc._kvecs.max():.4f}]")
        for attr in ['_gamma', '_lsorbit', '_lnoncollinear', '_ispin', '_efermi']:
            if hasattr(wfc, attr):
                print(f"  {attr}={getattr(wfc, attr)}")
    except ImportError:
        size = os.path.getsize(path)
        print(f"  File: {size/1024/1024:.1f} MB (vaspwfc not available)")
        print("  Binary format, cannot inspect without vaspwfc")


def inspect_doscar(path):
    with open(path) as f:
        lines = f.readlines()
    total = len(lines)
    print("=== DOSCAR ===")

    for i in range(6):
        print(f"  [{i}] {lines[i].rstrip()}")

    info = lines[5].strip().split()
    nedos, efermi = int(info[2]), float(info[3])
    print(f"  NEDOS={nedos}, EFermi={efermi:.4f}")

    total_dos = np.loadtxt(lines[6:6+nedos])
    print(f"  Total DOS: shape={total_dos.shape}")
    print(f"    -> {total_dos.shape[1]-1} data columns")

    # Check atom DOS
    if total > 6 + nedos + 1:
        atom1 = np.loadtxt(lines[7+nedos:7+2*nedos])
        print(f"  Atom DOS: shape={atom1.shape}")
        print(f"    -> {atom1.shape[1]-1} data columns")

    # Estimate number of atoms
    n_atoms = (total - 6) // (1 + nedos) - 1  # -1 for total DOS block
    print(f"  Estimated NIONS: ~{n_atoms}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_templates.py <path_to_vasp_file>")
        print("\nOr import and call specific functions:")
        print("  from inspect_templates import inspect_eigenval")
        print("  inspect_eigenval('EIGENVAL')")
        sys.exit(1)

    path = sys.argv[1]
    fname = os.path.basename(path).upper()

    if fname == 'EIGENVAL':
        inspect_eigenval(path)
    elif fname == 'CHGCAR' or fname == 'CHG':
        inspect_chgcar_header(path)
    elif fname == 'PROCAR':
        inspect_procar(path)
    elif fname == 'WAVECAR':
        inspect_wavecar(path)
    elif fname == 'DOSCAR':
        inspect_doscar(path)
    else:
        print(f"Unknown file: {fname}")
        print("Supported: EIGENVAL, CHGCAR, PROCAR, WAVECAR, DOSCAR")