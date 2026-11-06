# Primeval Atom: Covariant Quantum Hydrodynamic Regularization in R³

**Author:** David Botargues Martin  
**DOI:** [10.5281/zenodo.24001826](https://doi.org/10.5281/zenodo.24001826)  
**Zenodo record:** https://zenodo.org/records/24001826  
**License:** Creative Commons Attribution 4.0 (CC BY 4.0)

---

## Overview

This repository contains the simulation code for the paper:

> *Covariant Quantum Hydrodynamic Regularization, Flavor Phase-Space Positioning, and Gauge Extensions at the Zepto-Scale in R³*

The model demonstrates that a critical geometric radius **R = √π** in phase space acts as an orthogonal projector in Fourier space, interrupting the ultraviolet divergence of enstrophy within Sobolev spaces H^s(R³). This mechanism derives a stationary libration point where **Du/Dt = 0**, shielding the continuum against entropic degradation.

**Key predictions:**
- Z'_Zepto boson at √s = 14.0000 TeV, Γ = 2.7705 GeV (testable at HL-LHC)
- QCD axion at 6.54183024 μeV (within ADMX Run 2A projected range)
- Ω_c = 0.264, Ω_Λ = 0.687 (consistent with Planck 2018)

---

## Files

| File | Description |
|------|-------------|
| `simulation.py` | Main simulation: UV cutoff proof, enstrophy, Madelung potential, libration point |
| `zepto_matrix.py` | Energy conversions eV→J + Breit-Wigner Z' cross-section |
| `primeval_atom_simulator.py` | Cosmic fluid expansion simulator |
| `fourier_breakdown_solver.py` | Fourier neutralization identity: 4πR²=4π² at R=√π |
| `reflexive_causal_dominance.py` | Reflexive Causal Dominance simulation (do-calculus) |
| `run_card.dat` | MadGraph5 run card for pp → Z'_Zepto → l⁺l⁻ |

---

## Usage

```bash
pip install numpy matplotlib
python simulation.py
```

Output: `simulation_plot.png` + `simulation_report.md`

---

## Citation

```bibtex
@software{botargues_martin_2026_24001826,
  author    = {Botargues Martin, David},
  title     = {Covariant Quantum Hydrodynamic Regularization, Flavor
               Phase-Space Positioning, and Gauge Extensions at the
               Zepto-Scale in R³},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.24001826},
  url       = {https://doi.org/10.5281/zenodo.24001826}
}
```
