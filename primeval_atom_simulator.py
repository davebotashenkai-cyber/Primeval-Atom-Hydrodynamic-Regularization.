"""
primeval_atom_simulator.py
==========================
Simulates the cosmic fluid expansion of the Primeval Atom model.

Plots:
  - Enstrophy Omega(r) vs radius r in [0.1, R_critical]
  - UV cutoff at R_critical = sqrt(pi) (vertical dashed line)
  - Madelung relativistic quantum potential Q_rel(r) vs r
  - Libration point where Du/Dt = 0

Saves: primeval_atom_plot.png
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
HBAR = 1.0          # natural units
M    = 1.0
C    = 1.0
NU   = 0.1          # kinematic viscosity coefficient
COEFF_C = 0.5       # dimensionless constant in enstrophy inequality

R_CRITICAL = np.sqrt(np.pi)   # ~1.7725

# ---------------------------------------------------------------------------
# Model functions
# ---------------------------------------------------------------------------

def phi(r):
    """Madelung amplitude: Gaussian wavepacket centered at origin."""
    sigma = R_CRITICAL / 2.0
    return np.exp(-r**2 / (2.0 * sigma**2))


def d2phi_dr2(r):
    """Analytical second derivative of phi w.r.t. r (radial Laplacian, spherical)."""
    sigma = R_CRITICAL / 2.0
    # Laplacian in 3D spherical for radial function: d²phi/dr² + (2/r) dphi/dr
    dphi = -(r / sigma**2) * phi(r)
    d2phi = (r**2 / sigma**4 - 1.0 / sigma**2) * phi(r)
    laplacian = d2phi + (2.0 / r) * dphi
    return laplacian


def Q_rel(r):
    """
    Relativistic Madelung quantum potential.
      Q_rel = (hbar^2 / m) * (box phi) / phi
    where box = d_mu d^mu (covariant Laplacian, Minkowski signature +---)
    In static, radial case reduces to -nabla^2 phi / phi (spatial part).
    """
    lap = d2phi_dr2(r)
    q = -(HBAR**2 / M) * lap / phi(r)
    return q


def enstrophy(r):
    """
    Enstrophy proxy: Omega(r) ~ integral of |omega|^2 up to radius r.
    We model the local enstrophy density as proportional to (1/r^2) * exp(-r^2/sigma^2)
    which diverges toward r->0 (UV cascade) and is cut off at R_critical.

    Omega(r) = integral_0^r  (C_ens / s^2) * exp(-s^2 / sigma^2) 4*pi*s^2 ds
             = 4*pi*C_ens * integral_0^r  exp(-s^2 / sigma^2) ds   (s^2 cancels)
    """
    sigma = R_CRITICAL / 2.0
    C_ens = 1.0
    # Numerical cumulative integral
    s = np.linspace(1e-6, r, 400)
    ds = s[1] - s[0]
    integrand = np.exp(-s**2 / sigma**2)
    return 4.0 * np.pi * C_ens * np.trapz(integrand, s) if hasattr(np, 'trapz') else 4.0 * np.pi * C_ens * np.trapezoid(integrand, s)


def Du_Dt(r):
    """
    Material derivative of fluid velocity (covariant acceleration).
    Du/Dt = -(1/rho) grad P + grad Q_rel / m
    In the Madelung picture, at the libration point these balance exactly.
    We model: Du/Dt ~ dQ_rel/dr  (drives acceleration toward equilibrium)
    """
    dr = 1e-5
    dq = (Q_rel(r + dr) - Q_rel(r - dr)) / (2.0 * dr)
    return dq


# ---------------------------------------------------------------------------
# Build arrays
# ---------------------------------------------------------------------------
r_vals = np.linspace(0.1, R_CRITICAL * 1.05, 500)

# Clip r to avoid log(0) at r=0
r_safe = np.clip(r_vals, 1e-6, None)

enstrophy_vals = np.array([enstrophy(r) for r in r_vals])
Q_vals         = np.array([Q_rel(r)    for r in r_vals])
DuDt_vals      = np.array([Du_Dt(r)    for r in r_vals])

# Normalize for overlay clarity
enstrophy_norm = enstrophy_vals / enstrophy_vals.max()
Q_norm         = (Q_vals - Q_vals.min()) / (Q_vals.max() - Q_vals.min() + 1e-12)
DuDt_norm      = (DuDt_vals - DuDt_vals.min()) / (DuDt_vals.max() - DuDt_vals.min() + 1e-12)

# Find libration point (Du/Dt closest to zero)
idx_lib = np.argmin(np.abs(DuDt_vals))
r_lib   = r_vals[idx_lib]

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(9, 10), sharex=True)
fig.suptitle(
    r"Primeval Atom: Cosmic Fluid Expansion — $R_{\rm critical} = \sqrt{\pi}$",
    fontsize=14, fontweight="bold"
)

# --- Top panel: Enstrophy ---
ax1 = axes[0]
ax1.plot(r_vals, enstrophy_norm, color="steelblue", lw=2, label=r"$\Omega(r)$ (normalized)")
ax1.axvline(R_CRITICAL, color="crimson", lw=2, ls="--",
            label=r"UV cutoff $R_c = \sqrt{\pi} \approx 1.7725$")
ax1.fill_betweenx([0, 1.05], R_CRITICAL, r_vals.max(),
                  alpha=0.08, color="crimson", label="Trans-Planck (regularized)")
ax1.set_ylabel(r"Normalized Enstrophy $\Omega(r)$", fontsize=11)
ax1.set_ylim(0, 1.05)
ax1.legend(fontsize=9)
ax1.set_title("Enstrophy accumulation with geometric UV cutoff", fontsize=11)
ax1.grid(True, alpha=0.3)

# Annotate
ax1.annotate(
    r"$\frac{d\Omega}{dt} \leq \frac{C}{\nu^3}\,\Omega^3$ diverges without cutoff",
    xy=(0.5, 0.5), xycoords="axes fraction",
    fontsize=9, color="gray", ha="center"
)

# --- Bottom panel: Q_rel and Du/Dt ---
ax2 = axes[1]
ax2.plot(r_vals, Q_norm, color="darkorange", lw=2,
         label=r"$Q_{\rm rel}(r)$ (normalized)")
ax2.plot(r_vals, DuDt_norm, color="mediumseagreen", lw=2, ls="-.",
         label=r"$Du/Dt$ (normalized)")
ax2.axvline(R_CRITICAL, color="crimson", lw=2, ls="--",
            label=r"$R_c = \sqrt{\pi}$")
ax2.axvline(r_lib, color="purple", lw=1.5, ls=":",
            label=rf"Libration point $r \approx {r_lib:.4f}$, $Du/Dt \to 0$")
ax2.set_xlabel(r"Radius $r$ [natural units]", fontsize=11)
ax2.set_ylabel("Normalized amplitude", fontsize=11)
ax2.legend(fontsize=9)
ax2.set_title(r"Madelung quantum potential $Q_{\rm rel}$ and libration point $Du/Dt=0$",
              fontsize=11)
ax2.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_dir  = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "primeval_atom_plot.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()

print(f"Figure saved: {out_path}")
print(f"R_critical = sqrt(pi) = {R_CRITICAL:.6f}")
print(f"Libration point r = {r_lib:.6f}  (Du/Dt ~ {DuDt_vals[idx_lib]:.2e})")
print(f"Enstrophy at R_critical (normalized) = {enstrophy_norm[np.argmin(np.abs(r_vals - R_CRITICAL))]:.4f}")
