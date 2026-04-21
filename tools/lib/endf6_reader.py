"""
Pure-Python ENDF-6 reader for MF3 (cross-section) data.

No external dependencies beyond numpy (for interpolation).  Used as a
fallback when the `endf` package (endf-python) is not installed, and also
as the back-end for validating that both parsers agree.

ENDF-6 file format reference:
  ENDF-102, Rev. 2018 (BNL-203218-2018-BOOK)
  https://www.nndc.bnl.gov/endfdocs/ENDF-102-2018.pdf

Quick format summary
--------------------
Every record is exactly 80 characters:
  Chars  1–11  Field 1  (REAL or INT depending on record type)
  Chars 12–22  Field 2
  Chars 23–33  Field 3
  Chars 34–44  Field 4
  Chars 45–55  Field 5
  Chars 56–66  Field 6
  Chars 67–70  MAT  (material number, integer)
  Chars 71–72  MF   (file number)
  Chars 73–75  MT   (section number)
  Chars 76–80  NS   (line sequence — ignored)

Interpolation laws (INT codes in TAB1):
  1 = Histogram (constant)
  2 = Linear-linear  (E, σ)
  3 = Linear-log     (ln E, σ)
  4 = Log-linear     (E, ln σ)
  5 = Log-log        (ln E, ln σ)
"""

import re
import math
from typing import List, Tuple, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Field parsing
# ---------------------------------------------------------------------------

def _parse_float(s: str) -> float:
    """
    Parse an ENDF-6 real field (11 chars).

    ENDF uses a compact notation without the letter 'E':
      "1.5437-10"  →  1.5437e-10
      " 2.3456+3"  →  2345.6
      "0.0"        →  0.0
      "           " →  0.0
    """
    s = s.strip()
    if not s:
        return 0.0
    # Insert 'E' before the exponent sign if it was elided
    # Pattern: optional sign, digits, optional decimal, more digits, then +/- and digits
    m = re.match(r'^([+-]?\d*\.?\d+)([+-]\d+)$', s)
    if m:
        return float(m.group(1) + 'e' + m.group(2))
    return float(s)


def _parse_int(s: str) -> int:
    s = s.strip()
    if not s:
        return 0
    return int(s)


def _parse_line(line: str) -> Tuple[List[str], int, int, int]:
    """
    Split one 80-char ENDF record into raw field strings and (MAT, MF, MT).
    Pads short lines (e.g. SEND/FEND/MEND/TPID with fewer chars).
    """
    line = line.rstrip('\n').ljust(80)
    fields = [line[i*11:(i+1)*11] for i in range(6)]
    mat_s = line[66:70].strip()
    mf_s  = line[70:72].strip()
    mt_s  = line[72:75].strip()
    mat = int(mat_s) if mat_s else 0
    mf  = int(mf_s)  if mf_s  else 0
    mt  = int(mt_s)  if mt_s  else 0
    return fields, mat, mf, mt


# ---------------------------------------------------------------------------
# TAB1 record parser
# ---------------------------------------------------------------------------

def _read_tab1(lines: List[str], start: int) -> Tuple[int, np.ndarray, np.ndarray]:
    """
    Read a TAB1 record from an ENDF-6 section starting at `start`.

    TAB1 structure:
      CONT record : C1 C2 L1 L2 NR NP
      LIST of NR  : (NBT_i, INT_i) interp region pairs (3 per line as integer fields)
      LIST of NP  : (E_j, XS_j) data pairs (3 pairs per line, 6 real fields)

    Returns:
      next_line_index : int
      energies        : np.ndarray (eV)
      xs_values       : np.ndarray (barns)
    """
    # --- CONT record ---
    fields, _, _, _ = _parse_line(lines[start])
    NR = _parse_int(fields[4])  # number of interpolation regions
    NP = _parse_int(fields[5])  # number of data points
    idx = start + 1

    # --- Interpolation region pairs ---
    # Stored as integers, 6 per line, giving (NBT, INT) × NR
    nbt_int_vals: List[int] = []
    while len(nbt_int_vals) < NR * 2:
        fields, _, _, _ = _parse_line(lines[idx])
        for f in fields:
            nbt_int_vals.append(_parse_int(f))
        idx += 1
    NBT = np.array(nbt_int_vals[0::2][:NR], dtype=int)   # 1-indexed breakpoints
    INT = np.array(nbt_int_vals[1::2][:NR], dtype=int)   # interpolation codes

    # --- Energy / cross-section pairs ---
    # Stored as reals, 6 per line interleaved E1 XS1 E2 XS2 E3 XS3
    ev_xs_vals: List[float] = []
    while len(ev_xs_vals) < NP * 2:
        fields, _, _, _ = _parse_line(lines[idx])
        for f in fields:
            ev_xs_vals.append(_parse_float(f))
        idx += 1
    energies = np.array(ev_xs_vals[0::2][:NP])   # eV
    xs       = np.array(ev_xs_vals[1::2][:NP])   # barns

    return idx, energies, xs, NBT, INT


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

def interpolate_xs(energies: np.ndarray, xs: np.ndarray,
                   NBT: np.ndarray, INT: np.ndarray,
                   query_eV: float) -> Optional[float]:
    """
    Evaluate a TAB1 cross-section at query_eV (eV) using the stored
    interpolation law.  Returns None if the query is outside the tabulated
    range (threshold reactions).
    """
    if query_eV < energies[0] or query_eV > energies[-1]:
        return None

    # Find bracketing indices
    j = np.searchsorted(energies, query_eV, side='right') - 1
    j = int(np.clip(j, 0, len(energies) - 2))

    E1, E2 = energies[j], energies[j + 1]
    S1, S2 = xs[j], xs[j + 1]

    if E1 == E2:
        return float(S1)

    # Determine interpolation law for this region
    # NBT[k] is the 1-indexed last point of region k; INT[k] applies to region k
    region_int = 2  # default: linear-linear
    for k in range(len(NBT)):
        if (j + 1) <= NBT[k]:   # j+1 is 1-indexed
            region_int = INT[k]
            break

    x = query_eV
    if region_int == 1:  # histogram
        return float(S1)
    elif region_int == 2:  # linear-linear
        return float(S1 + (S2 - S1) * (x - E1) / (E2 - E1))
    elif region_int == 3:  # linear-log: y linear, x log
        if E1 <= 0 or E2 <= 0 or x <= 0:
            return float(S1)
        return float(S1 + (S2 - S1) * math.log(x / E1) / math.log(E2 / E1))
    elif region_int == 4:  # log-linear: y log, x linear
        if S1 <= 0 or S2 <= 0:
            return float(S1)
        return float(math.exp(
            math.log(S1) + (math.log(S2) - math.log(S1)) * (x - E1) / (E2 - E1)
        ))
    elif region_int == 5:  # log-log
        if E1 <= 0 or E2 <= 0 or x <= 0 or S1 <= 0 or S2 <= 0:
            return float(S1)
        return float(math.exp(
            math.log(S1) + (math.log(S2) - math.log(S1)) *
            math.log(x / E1) / math.log(E2 / E1)
        ))
    else:
        # Unknown law — fall back to linear-linear
        return float(S1 + (S2 - S1) * (x - E1) / (E2 - E1))


# ---------------------------------------------------------------------------
# Main public interface
# ---------------------------------------------------------------------------

def read_mf3_section(filepath: str, target_mt: int) -> Optional[dict]:
    """
    Parse an ENDF-6 file and return the MF=3 cross-section data for target_mt.

    Returns a dict:
        {
            "MAT":      int,        # ENDF material number
            "MT":       int,        # reaction type (e.g. 102 for (n,γ))
            "energies": np.ndarray, # tabulated energies, eV
            "xs":       np.ndarray, # tabulated cross-sections, barns
            "NBT":      np.ndarray, # interpolation region breakpoints
            "INT":      np.ndarray, # interpolation codes
        }

    Returns None if target_mt is not found (e.g. threshold reaction not in library).
    """
    with open(filepath, 'r', errors='replace') as fh:
        lines = fh.readlines()

    in_mf3 = False
    in_target_mt = False
    section_start = None
    found_mat = None

    for i, line in enumerate(lines):
        _, mat, mf, mt = _parse_line(line)

        if mf == 3 and mt == target_mt:
            if not in_target_mt:
                in_target_mt = True
                section_start = i
                found_mat = mat
            # Section header is the first line; TAB1 starts at section_start + 1
            # (first line of MF3/MT is the CONT header line)
        elif in_target_mt and (mf != 3 or mt != target_mt):
            # End of section — parse what we collected
            break

    if section_start is None:
        return None

    # Skip the CONT record (which is the HEAD/first line for MF3 sections)
    # MF3 structure: HEAD (CONT), then TAB1 for the cross section
    # The HEAD gives ZA, AWR, 0, 0, 0, 0
    # The TAB1 (starting next line) gives QM, QI, 0, LR, NR, NP, then data
    tab1_start = section_start + 1

    _, energies, xs_vals, NBT, INT = _read_tab1(lines, tab1_start)

    return {
        "MAT":      found_mat,
        "MT":       target_mt,
        "energies": energies,
        "xs":       xs_vals,
        "NBT":      NBT,
        "INT":      INT,
    }


def query_xs(filepath: str, target_mt: int,
             energies_eV: List[float]) -> dict:
    """
    High-level function: read one reaction from an ENDF-6 file and evaluate
    the cross-section at each requested energy.

    Returns:
        {
            "found":    bool,
            "MAT":      int or None,
            "results":  {energy_eV: sigma_barns or None, ...},
        }
    """
    section = read_mf3_section(filepath, target_mt)
    if section is None:
        return {"found": False, "MAT": None, "results": {e: None for e in energies_eV}}

    results = {}
    for e in energies_eV:
        val = interpolate_xs(section["energies"], section["xs"],
                             section["NBT"], section["INT"], e)
        results[e] = val

    return {
        "found":   True,
        "MAT":     section["MAT"],
        "results": results,
    }
