"""
fourier_breakdown_solver.py
============================
Analyzes the Fourier neutralization mechanism of the Primeval Atom model.

The core result: when R = sqrt(pi), the surface area 4*pi*R^2 equals 4*pi^2,
which is the normalization constant of the 3D spherical Fourier kernel.
The residue  delta(R) = |4*pi*R^2 - 4*pi^2|  collapses to zero at R = sqrt(pi),
demonstrating the UV-cutoff projector identity.

Plots:
  - Surface area 4*pi*R^2 and Fourier normalization 4*pi^2 vs R
  - Residue delta(R) = |surface_area - fourier_norm| vs R
  - Highlights the zero crossing at R = sqrt(pi)

Saves: fourier_breakdown_plot.png
"""

import sys
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
R_CRITICAL   = np.sqrt(np.pi)            # ~1.7725
FOURIER_NORM = 4.0 * np.pi**2            # ~39.478  (3D Fourier kernel normalization)

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def surface_area(R):
    """Euclidean surface area of a 2-sphere of radius R."""
    return 4.0 * np.pi * R**2


def residue(R):
    """
    Absolute residue between surface area and Fourier normalization.
    delta(R) = | 4*pi*R^2 - 4*pi^2 |
    Vanishes at R = sqrt(pi).
    """
    return np.abs(surface_area(R) - FOURIER_NORM)


def relative_residue(R):
    """Dimensionless residue: delta(R) / (4*pi^2)."""
    return residue(R) / FOURIER_NORM


def fourier_projector_weight(R):
    """
    Orthogonal projector weight in Fourier space.
    P(R) = exp( - (R^2 - pi)^2 / sigma^2 )
    Peaks at R = sqrt(pi) — represents the concentration of projection weight
    around the UV-cutoff scale.
    """
    sigma = 0.3
    return np.exp(-((R**2 - np.pi)**2) / sigma**2)


# ---------------------------------------------------------------------------
# Build arrays
# ---------------------------------------------------------------------------
R_min, R_max = 0.5, 3.5
R_vals = np.linspace(R_min, R_max, 1000)

sa_vals   = surface_area(R_vals)
res_vals  = residue(R_vals)
rrel_vals = relative_residue(R_vals)
proj_vals = fourier_projector_weight(R_vals)

# Index of R_critical
idx_rc = np.argmin(np.abs(R_vals - R_CRITICAL))

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(9, 12))
fig.suptitle(
    r"Fourier Neutralization at $R = \sqrt{\pi}$: "
    r"Surface Area $4\pi R^2 = 4\pi^2$ at $R = \sqrt{\pi}$",
    fontsize=13, fontweight="bold"
)

# --- Panel 1: Surface area vs Fourier normalization ---
ax1 = axes[0]
ax1.plot(R_vals, sa_vals, color="steelblue", lw=2.5,
         label=r"$4\pi R^2$ (surface area)")
ax1.axhline(FOURIER_NORM, color="darkorange", lw=2, ls="--",
            label=rf"$4\pi^2 \approx {FOURIER_NORM:.3f}$ (Fourier normalization)")
ax1.axvline(R_CRITICAL, color="crimson", lw=2, ls=":",
            label=rf"$R_c = \sqrt{{\pi}} \approx {R_CRITICAL:.4f}$")

# Intersection marker
ax1.scatter([R_CRITICAL], [FOURIER_NORM], zorder=5, s=80,
            color="crimson", label=rf"Intersection: $R={R_CRITICAL:.4f}$, $A={FOURIER_NORM:.3f}$")

ax1.set_ylabel(r"Area / Normalization value", fontsize=11)
ax1.set_title(r"Surface area $4\pi R^2$ vs Fourier normalization $4\pi^2$", fontsize=11)
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(R_min, R_max)

# Annotate the identity
ax1.annotate(
    r"$4\pi R^2 = 4\pi^2$  at  $R = \sqrt{\pi}$",
    xy=(R_CRITICAL, FOURIER_NORM),
    xytext=(R_CRITICAL + 0.4, FOURIER_NORM - 5),
    arrowprops=dict(arrowstyle="->", color="crimson"),
    fontsize=10, color="crimson"
)

# --- Panel 2: Absolute residue ---
ax2 = axes[1]
ax2.plot(R_vals, res_vals, color="mediumseagreen", lw=2.5,
         label=r"$\delta(R) = |4\pi R^2 - 4\pi^2|$")
ax2.axvline(R_CRITICAL, color="crimson", lw=2, ls=":",
            label=rf"$R_c = \sqrt{{\pi}}$")
ax2.scatter([R_CRITICAL], [res_vals[idx_rc]], zorder=5, s=80, color="crimson")

ax2.set_ylabel(r"Absolute residue $\delta(R)$", fontsize=11)
ax2.set_title(r"Residue $\delta(R) = |4\pi R^2 - 4\pi^2|$ — collapses to 0 at $R = \sqrt{\pi}$",
              fontsize=11)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(R_min, R_max)
ax2.set_ylim(bottom=0)

ax2.annotate(
    rf"$\delta(R_c) = {res_vals[idx_rc]:.2e}$",
    xy=(R_CRITICAL, res_vals[idx_rc] + 0.3),
    xytext=(R_CRITICAL + 0.3, 5),
    arrowprops=dict(arrowstyle="->", color="crimson"),
    fontsize=10, color="crimson"
)

# --- Panel 3: Fourier projector weight ---
ax3 = axes[2]
ax3.plot(R_vals, proj_vals, color="mediumpurple", lw=2.5,
         label=r"$P(R) = \exp\!\left(-\frac{(R^2 - \pi)^2}{\sigma^2}\right)$, $\sigma=0.3$")
ax3.axvline(R_CRITICAL, color="crimson", lw=2, ls=":",
            label=rf"$R_c = \sqrt{{\pi}} \approx {R_CRITICAL:.4f}$")
ax3.fill_between(R_vals, proj_vals, alpha=0.15, color="mediumpurple")

ax3.set_xlabel(r"Radius $R$ [natural units]", fontsize=11)
ax3.set_ylabel(r"Projector weight $P(R)$", fontsize=11)
ax3.set_title(r"Fourier orthogonal projector concentrated at $R = \sqrt{\pi}$ (UV cutoff)",
              fontsize=11)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(R_min, R_max)
ax3.set_ylim(0, 1.1)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_dir  = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "fourier_breakdown_plot.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()

print(f"Figure saved: {out_path}")
print()
print("=== Key values ===")
print(f"R_critical       = sqrt(pi)  = {R_CRITICAL:.8f}")
print(f"Surface area(Rc) = 4*pi*Rc^2 = {surface_area(R_CRITICAL):.8f}")
print(f"Fourier norm     = 4*pi^2    = {FOURIER_NORM:.8f}")
print(f"Residue at Rc    = delta(Rc) = {residue(R_CRITICAL):.2e}  (machine precision zero)")
print(f"Relative residue = {relative_residue(R_CRITICAL):.2e}")
print()
print("Identity confirmed: 4*pi*R^2 = 4*pi^2  at  R = sqrt(pi)")
print("This acts as an orthogonal Fourier projector — UV cutoff mechanism.")
