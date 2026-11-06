# Primeval Atom: Covariant Quantum Hydrodynamic Regularization in R³

**Author:** David Botargues Martin  
**Affiliation:** Independent Systems & Physics Researcher  
**DOI:** [10.5281/zenodo.24001826](https://doi.org/10.5281/zenodo.24001826)  
**Zenodo Record:** https://zenodo.org/records/24001826  
**License:** Creative Commons Attribution 4.0 (CC BY 4.0)

---

## Overview

This repository hosts the numerical simulation code and analytical manuscripts for:

> **Covariant Quantum Hydrodynamic Regularization, Flavor Phase-Space Positioning, and Gauge Extensions at the Zepto-Scale in R³**

The model formulates a covariant Madelung-Klein-Gordon hydrodynamic framework in phase space. Introducing a critical geometric radius **$R_c = \sqrt{\pi}$** acts as a spectral Littlewood-Paley projector in momentum space, regularizing high-frequency enstrophy divergence within Sobolev spaces $H^s(\mathbb{R}^3)$ for $s \ge 1$. 

Enforcing the boundary normalization condition derives a global stationary libration point where the relativistic material derivative collapses to zero (**$Du/Dt = 0$**), dynamically shielding the continuum against entropic collapse.

### Key Theoretical & Phenomenological Results:
- **Sobolev Enstrophy Regularization:** Classical finite-time vorticity blow-up ($T^*$) is averted by a spectral projection cutoff at the characteristic Zepto scale ($\ell_Z \sim 1.41 \times 10^{-20}\text{ m}$).
- **Heavy Vector Boson ($Z'_{Zepto}$):** $M_{Z'} = 14.0000\text{ TeV}$, $\Gamma = 2.7705\text{ GeV}$ ($\Gamma/M = 1.98 \times 10^{-4}$, narrow width). Observable via off-shell Drell-Yan dilepton contact interactions at the High-Luminosity LHC (HL-LHC) and on-shell resonance discovery at the Future Circular Collider (FCC-hh) and future Muon Colliders.
- **QCD Axion Dark Matter:** Basal pseudo-scalar vacuum field fixed at $m_a = 6.54183024\,\mu\text{eV}$ (within the target sensitivity window of ADMX Run 2A and CULTASK cavity haloscopes).
- **Cosmological Concordance:** Reproduces flat Euclidean vacuum fractions $\Omega_c = 0.264$ (cold dark matter) and $\Omega_\Lambda = 0.687$ (dark energy), consistent with Planck 2018 parameters.

---

## Repository Files

| File | Type | Description |
|---|---|---|
| `simulation.py` | Python Script | Main simulation v2.1: UV spectral projector, Sobolev enstrophy bounding, Madelung potential, and libration point |
| `zepto_matrix.py` | Python Script | Exact SI conversions, Breit-Wigner resonance cross-section, and collider reach analysis (HL-LHC vs. FCC-hh vs. Muon Collider) |
| `primeval_atom_simulator.py` | Python Script | Cosmic fluid expansion dynamics and radial quantum potential gradients |
| `fourier_breakdown_solver.py` | Python Script | Geometric phase-space boundary matching: $4\pi R_c^2 = 4\pi^2$ at $R_c = \sqrt{\pi}$ |
| `reflexive_causal_dominance.py` | Python Script | Reflexive Causal Dominance simulation using Judea Pearl's do-calculus in creator-created helicoidal systems |
| `param_card.dat` | Data Card | SLHA-format MadGraph5 parameter card specifying $M_{Z'}$, $M_{\text{Axion}}$, and electroweak running couplings |
| `run_card.dat` | Data Card | MadGraph5 run configuration for $pp \to Z'_{Zepto} \to \ell^+\ell^-$ simulations |
| `Technical_Manuscript_Zepto_Scale.pdf` | Document | Technical memorandum on zepto-scale gauge extensions and flavor positioning |
| `The_Primeval_Atom_Covariant_Hydrodynamic_Regularization.pdf` | Document | Foundational paper on covariant Madelung hydrodynamics and Sobolev bounding |

---

## Installation & Execution

### Prerequisites
Requires Python 3.8+ with standard scientific libraries:
```bash
pip install numpy matplotlib
```

### Running Simulations

1. **Main Regularization Pipeline:**
   ```bash
   python simulation.py
   ```
   *Generates:* `simulation_plot.png` (4-panel publication visual) and `simulation_report.md` (quantitative validation summary).

2. **$Z'_{Zepto}$ Phenomenology & Breit-Wigner Curve:**
   ```bash
   python zepto_matrix.py
   ```
   *Generates:* `zepto_resonance_curve.png`.

3. **Cosmic Fluid & Fourier Projector Analysis:**
   ```bash
   python primeval_atom_simulator.py
   python fourier_breakdown_solver.py
   ```
   *Generates:* `primeval_atom_plot.png` and `fourier_breakdown_plot.png`.

4. **Reflexive Causal Dominance Simulation:**
   ```bash
   python reflexive_causal_dominance.py
   ```
   *Generates:* `reflexive_dominance_plot.png`.

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
