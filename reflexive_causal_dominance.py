"""
reflexive_causal_dominance.py
==============================
Simulation of Reflexive Causal Dominance in Creator-Created Systems.

Implements:
  - 3D helicoidal dynamical system
  - Internal policy pi_S (proportional radial + axial damping controller)
  - External policy pi_D (noise + radial push)
  - do() interventions to estimate Delta_D and Delta_S
  - Dominance(D->S) = |Delta_D| / (|Delta_S| + epsilon)
  - Dominance inversion curve over alpha sweep
  - Phase-space plots of helicoidal trajectories
  - Saves figure as reflexive_dominance_plot.png

Usage:
    python reflexive_causal_dominance.py

Requires: numpy, matplotlib (standard scientific Python stack)
"""

import sys
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ── Reproducibility ──────────────────────────────────────────────────────────
RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

# ── Simulation parameters ─────────────────────────────────────────────────────
OMEGA   = 1.0        # base angular frequency (rad/s)
V_AXIAL = 0.05       # axial drift velocity
DT      = 0.05       # timestep
T_STEPS = 1000       # simulation length
N_RUNS  = 50         # independent runs per condition

# Internal policy gains
KP = 0.5             # proportional radial gain
KD = 0.1             # axial damping gain
R_TARGET = 1.0       # target radius in x1-x2 plane

# External policy parameters
SIGMA_D  = 0.05      # noise std for pi_D
PUSH_D   = 0.2       # radial push magnitude for pi_D

EPSILON  = 1e-9      # numerical stability in dominance denominator

# Cooperative region R: annular band in x1-x2, bounded axial range
R_MIN, R_MAX = 0.5, 2.0
X3_LIM       = 5.0


# ── Helper: check if state is in cooperative region ───────────────────────────
def in_region(x: np.ndarray) -> bool:
    r = np.sqrt(x[0]**2 + x[1]**2)
    return R_MIN <= r <= R_MAX and abs(x[2]) <= X3_LIM


# ── Internal policy pi_S ─────────────────────────────────────────────────────
def pi_S(x: np.ndarray, rng_local: np.random.Generator) -> np.ndarray:
    r = np.sqrt(x[0]**2 + x[1]**2)
    if r < 1e-8:
        return np.zeros(3)
    radial_err = r - R_TARGET
    a1 = -KP * radial_err * x[0] / r
    a2 = -KP * radial_err * x[1] / r
    a3 = -KD * x[2]
    return np.array([a1, a2, a3])


def pi_S_null(x: np.ndarray, rng_local: np.random.Generator) -> np.ndarray:
    """Null internal policy: zero action."""
    return np.zeros(3)


# ── External policy pi_D ─────────────────────────────────────────────────────
def pi_D(x: np.ndarray, rng_local: np.random.Generator) -> np.ndarray:
    r = np.sqrt(x[0]**2 + x[1]**2)
    if r < 1e-8:
        return rng_local.normal(0, SIGMA_D, 3)
    eta = rng_local.normal(0, SIGMA_D, 3)
    push = np.array([PUSH_D * x[0] / r, PUSH_D * x[1] / r, 0.0])
    return eta + push


def pi_D_null(x: np.ndarray, rng_local: np.random.Generator) -> np.ndarray:
    """Null external policy: zero action."""
    return np.zeros(3)


# ── State transition ─────────────────────────────────────────────────────────
def step(x: np.ndarray, action: np.ndarray) -> np.ndarray:
    """One timestep of the helicoidal dynamical system."""
    a1, a2, a3 = action
    c, s = np.cos(OMEGA * DT), np.sin(OMEGA * DT)
    x1_new = x[0] * c - x[1] * s + a1
    x2_new = x[0] * s + x[1] * c + a2
    x3_new = x[2] + V_AXIAL * DT + a3
    return np.array([x1_new, x2_new, x3_new])


# ── Persistence metric tau ────────────────────────────────────────────────────
def compute_tau(trajectory: np.ndarray) -> float:
    """Fraction of timesteps spent inside cooperative region R."""
    in_r = np.array([in_region(x) for x in trajectory])
    return float(np.mean(in_r))


# ── Single simulation run ─────────────────────────────────────────────────────
def run_simulation(
    alpha: float,
    policy_S=pi_S,
    policy_D=pi_D,
    seed: int = 0,
    return_trajectory: bool = False,
):
    """
    Run one simulation with mixing coefficient alpha.

    Effective action: alpha * pi_D(x) + (1 - alpha) * pi_S(x)

    Returns tau (float), and optionally the full trajectory array.
    """
    local_rng = np.random.default_rng(seed)

    # Initial state: sample inside cooperative region
    r0 = local_rng.uniform(R_MIN + 0.1, R_MAX - 0.1)
    theta0 = local_rng.uniform(0, 2 * np.pi)
    x = np.array([r0 * np.cos(theta0), r0 * np.sin(theta0), 0.0])

    traj = [x.copy()]
    for _ in range(T_STEPS):
        a_int = policy_S(x, local_rng)
        a_ext = policy_D(x, local_rng)
        action = alpha * a_ext + (1.0 - alpha) * a_int
        x = step(x, action)
        traj.append(x.copy())

    trajectory = np.array(traj)
    tau = compute_tau(trajectory)

    if return_trajectory:
        return tau, trajectory
    return tau


# ── Batch runs for a condition ────────────────────────────────────────────────
def batch_tau(alpha, policy_S=pi_S, policy_D=pi_D, n_runs=N_RUNS, base_seed=0):
    taus = [
        run_simulation(alpha, policy_S, policy_D, seed=base_seed + i)
        for i in range(n_runs)
    ]
    return np.array(taus)


# ── Helicoidal index ──────────────────────────────────────────────────────────
def helicoidal_index(traj: np.ndarray) -> float:
    """
    H = (mean axial velocity) * (mean angular frequency) / trajectory variance.
    Higher H = more structured helical motion.
    """
    x1, x2, x3 = traj[:, 0], traj[:, 1], traj[:, 2]

    # Angular velocity in x1-x2 plane
    r = np.sqrt(x1**2 + x2**2)
    theta = np.unwrap(np.arctan2(x2, x1))
    dtheta = np.abs(np.diff(theta)) / DT
    mean_omega = np.mean(dtheta)

    # Axial velocity
    dx3 = np.abs(np.diff(x3)) / DT
    mean_v = np.mean(dx3)

    # Trajectory variance (in x1-x2 plane)
    var = np.var(x1) + np.var(x2)
    var = max(var, 1e-12)

    return (mean_v * mean_omega) / var


# ══════════════════════════════════════════════════════════════════════════════
# MAIN: run all conditions
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 62)
    print("  Reflexive Causal Dominance Simulation")
    print("=" * 62)
    print(f"  Runs per condition : {N_RUNS}")
    print(f"  Timesteps per run  : {T_STEPS}")
    print(f"  Mixing alpha (base): 0.3")
    print()

    # ── Condition (a): Baseline alpha=0.3 ────────────────────────────────────
    print("Running condition (a): Baseline alpha=0.30 ...", end=" ", flush=True)
    tau_baseline = batch_tau(alpha=0.30, base_seed=100)
    print(f"done  tau={tau_baseline.mean():.3f} ± {tau_baseline.std():.3f}")

    # ── Condition (b): pi_D only (alpha=1.0) ─────────────────────────────────
    print("Running condition (b): pi_D only (alpha=1.00) ...", end=" ", flush=True)
    tau_piD_only = batch_tau(alpha=1.00, base_seed=200)
    print(f"done  tau={tau_piD_only.mean():.3f} ± {tau_piD_only.std():.3f}")

    # ── Condition (c): pi_D null (alpha=0.0, internal only) ──────────────────
    print("Running condition (c): pi_D null (alpha=0.00) ...", end=" ", flush=True)
    tau_piD_null = batch_tau(alpha=0.00, policy_D=pi_D_null, base_seed=300)
    print(f"done  tau={tau_piD_null.mean():.3f} ± {tau_piD_null.std():.3f}")

    # ── Condition (d): pi_S null (internal disabled) ─────────────────────────
    print("Running condition (d): pi_S null (internal disabled) ...", end=" ", flush=True)
    tau_piS_null = batch_tau(alpha=0.00, policy_S=pi_S_null, policy_D=pi_D_null, base_seed=400)
    print(f"done  tau={tau_piS_null.mean():.3f} ± {tau_piS_null.std():.3f}")

    # ── Compute Delta_D, Delta_S, Dominance ──────────────────────────────────
    # Delta_D: effect of external policy on tau
    #   = E[tau | pi_D active, alpha=1] - E[tau | pi_D null, alpha=0]
    Delta_D = tau_piD_only.mean() - tau_piD_null.mean()

    # Delta_S: effect of internal policy on tau
    #   = E[tau | pi_S active, alpha=0] - E[tau | pi_S null]
    Delta_S = tau_piD_null.mean() - tau_piS_null.mean()

    Dominance = abs(Delta_D) / (abs(Delta_S) + EPSILON)

    # ── Confidence intervals (bootstrap 95%) ─────────────────────────────────
    def ci95(arr):
        low = np.percentile(arr, 2.5)
        high = np.percentile(arr, 97.5)
        return low, high

    # ── Results table ─────────────────────────────────────────────────────────
    print()
    print("-" * 62)
    print(f"  {'Condition':<38} {'tau mean':>8}  {'SD':>6}")
    print("-" * 62)
    print(f"  {'Baseline (alpha=0.30)':<38} {tau_baseline.mean():>8.3f}  {tau_baseline.std():>6.3f}")
    print(f"  {'pi_D only (alpha=1.00)':<38} {tau_piD_only.mean():>8.3f}  {tau_piD_only.std():>6.3f}")
    print(f"  {'pi_D null / pi_S active (alpha=0.00)':<38} {tau_piD_null.mean():>8.3f}  {tau_piD_null.std():>6.3f}")
    print(f"  {'pi_S null (both null)':<38} {tau_piS_null.mean():>8.3f}  {tau_piS_null.std():>6.3f}")
    print("-" * 62)
    print()
    print(f"  Delta_D  = {Delta_D:+.4f}   (effect of external control)")
    print(f"  Delta_S  = {Delta_S:+.4f}   (effect of internal regulation)")
    print(f"  |Delta_D| / |Delta_S| = {'inf' if abs(Delta_S) < 1e-12 else f'{abs(Delta_D)/abs(Delta_S):.4f}'}")
    print()
    print("  +-------------------------------------------------+")
    print(f"  |  Dominance(D->S) = {Dominance:.4f}                     |")
    if Dominance < 1.0:
        ratio = abs(Delta_S) / abs(Delta_D)
        print(f"  |  Interpretation : S dominates D  ({ratio:.2f}x stronger)|")
    else:
        ratio = abs(Delta_D) / (abs(Delta_S) + 1e-12)
        print(f"  |  Interpretation : D dominates S  ({ratio:.2f}x stronger)|")
    print("  +-------------------------------------------------+")
    print()

    # ── Dominance inversion curve over alpha ─────────────────────────────────
    print("Computing dominance inversion curve over alpha sweep ...", flush=True)
    alphas = np.linspace(0.0, 1.0, 21)
    dominance_curve = []
    for a in alphas:
        tau_a = batch_tau(alpha=a, n_runs=20, base_seed=500)
        # Delta_D(alpha): relative to internal-only baseline
        d_d = tau_a.mean() - tau_piD_null.mean()
        dom = abs(d_d) / (abs(Delta_S) + EPSILON)
        dominance_curve.append(dom)
        print(f"    alpha={a:.2f}  tau={tau_a.mean():.3f}  Dominance={dom:.3f}")
    dominance_curve = np.array(dominance_curve)

    # Find inversion point (where dominance crosses 1)
    inversion_alpha = None
    for i in range(len(dominance_curve) - 1):
        if dominance_curve[i] <= 1.0 <= dominance_curve[i + 1]:
            # linear interpolation
            t = (1.0 - dominance_curve[i]) / (dominance_curve[i + 1] - dominance_curve[i])
            inversion_alpha = alphas[i] + t * (alphas[i + 1] - alphas[i])
            break
    print()
    if inversion_alpha is not None:
        print(f"  Dominance inversion point: alpha ~ {inversion_alpha:.3f}")
    else:
        print("  Dominance inversion point: not found in [0, 1] range")

    # ── Sample trajectories for plotting ─────────────────────────────────────
    print()
    print("Generating sample trajectories for plotting ...")
    _, traj_internal = run_simulation(0.0, pi_S, pi_D_null,  seed=1, return_trajectory=True)
    _, traj_external = run_simulation(1.0, pi_S, pi_D,       seed=2, return_trajectory=True)
    _, traj_baseline = run_simulation(0.3, pi_S, pi_D,       seed=3, return_trajectory=True)

    H_internal = helicoidal_index(traj_internal)
    H_external = helicoidal_index(traj_external)
    H_baseline = helicoidal_index(traj_baseline)

    print(f"  Helicoidal index — internal-only : {H_internal:.3f}")
    print(f"  Helicoidal index — external-only : {H_external:.3f}")
    print(f"  Helicoidal index — baseline      : {H_baseline:.3f}")

    # ── Plotting ──────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0f0f1a")
    gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

    TRAJ_COLOR_INT = "#00e5ff"
    TRAJ_COLOR_EXT = "#ff4081"
    TRAJ_COLOR_BAS = "#76ff03"
    BG_COLOR = "#0f0f1a"
    PANEL_BG = "#15152a"
    GRID_COLOR = "#2a2a4a"
    TEXT_COLOR = "#e0e0ff"

    def style_ax(ax, title):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_COLOR, labelsize=7)
        ax.title.set_color(TEXT_COLOR)
        ax.title.set_fontsize(9)
        ax.set_title(title)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COLOR)
        ax.grid(color=GRID_COLOR, linewidth=0.5, alpha=0.7)

    # ── Panel 1: 3D helicoidal trajectory — internal only ────────────────────
    ax1 = fig.add_subplot(gs[0, 0], projection="3d")
    ax1.set_facecolor(PANEL_BG)
    ax1.plot(traj_internal[:, 0], traj_internal[:, 1], traj_internal[:, 2],
             color=TRAJ_COLOR_INT, lw=0.8, alpha=0.9)
    ax1.set_title(f"pi_S only  (H={H_internal:.2f})", color=TEXT_COLOR, fontsize=9)
    ax1.tick_params(colors=TEXT_COLOR, labelsize=6)
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.set_xlabel("x1", color=TEXT_COLOR, fontsize=7)
    ax1.set_ylabel("x2", color=TEXT_COLOR, fontsize=7)
    ax1.set_zlabel("x3", color=TEXT_COLOR, fontsize=7)

    # ── Panel 2: 3D trajectory — external only ───────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1], projection="3d")
    ax2.set_facecolor(PANEL_BG)
    ax2.plot(traj_external[:, 0], traj_external[:, 1], traj_external[:, 2],
             color=TRAJ_COLOR_EXT, lw=0.8, alpha=0.9)
    ax2.set_title(f"pi_D only  (H={H_external:.2f})", color=TEXT_COLOR, fontsize=9)
    ax2.tick_params(colors=TEXT_COLOR, labelsize=6)
    ax2.xaxis.pane.fill = False
    ax2.yaxis.pane.fill = False
    ax2.zaxis.pane.fill = False
    ax2.set_xlabel("x1", color=TEXT_COLOR, fontsize=7)
    ax2.set_ylabel("x2", color=TEXT_COLOR, fontsize=7)
    ax2.set_zlabel("x3", color=TEXT_COLOR, fontsize=7)

    # ── Panel 3: 3D trajectory — baseline ────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2], projection="3d")
    ax3.set_facecolor(PANEL_BG)
    ax3.plot(traj_baseline[:, 0], traj_baseline[:, 1], traj_baseline[:, 2],
             color=TRAJ_COLOR_BAS, lw=0.8, alpha=0.9)
    ax3.set_title(f"Baseline alpha=0.3  (H={H_baseline:.2f})", color=TEXT_COLOR, fontsize=9)
    ax3.tick_params(colors=TEXT_COLOR, labelsize=6)
    ax3.xaxis.pane.fill = False
    ax3.yaxis.pane.fill = False
    ax3.zaxis.pane.fill = False
    ax3.set_xlabel("x1", color=TEXT_COLOR, fontsize=7)
    ax3.set_ylabel("x2", color=TEXT_COLOR, fontsize=7)
    ax3.set_zlabel("x3", color=TEXT_COLOR, fontsize=7)

    # ── Panel 4: tau by condition (bar chart) ─────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    style_ax(ax4, "Persistence tau by Condition")
    conditions = ["Baseline\nalpha=0.3", "pi_D only\nalpha=1.0",
                  "pi_D null\nalpha=0.0", "pi_S null\n(both null)"]
    means = [tau_baseline.mean(), tau_piD_only.mean(),
             tau_piD_null.mean(), tau_piS_null.mean()]
    stds  = [tau_baseline.std(), tau_piD_only.std(),
             tau_piD_null.std(), tau_piS_null.std()]
    colors_bar = [TRAJ_COLOR_BAS, TRAJ_COLOR_EXT, TRAJ_COLOR_INT, "#ff9100"]
    bars = ax4.bar(conditions, means, yerr=stds, color=colors_bar,
                   capsize=4, error_kw={"ecolor": TEXT_COLOR, "lw": 1.2},
                   width=0.55, alpha=0.85)
    ax4.set_ylabel("tau (persistence)", color=TEXT_COLOR, fontsize=8)
    ax4.set_ylim(0, 1.1)
    ax4.tick_params(axis="x", labelsize=7)
    for bar, m in zip(bars, means):
        ax4.text(bar.get_x() + bar.get_width() / 2, m + 0.04,
                 f"{m:.3f}", ha="center", va="bottom", fontsize=7, color=TEXT_COLOR)

    # ── Panel 5: Dominance inversion curve ───────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    style_ax(ax5, "Dominance(D→S) vs Mixing Coefficient α")
    ax5.plot(alphas, dominance_curve, color="#ce93d8", lw=2, marker="o",
             markersize=4, markerfacecolor="#7b1fa2")
    ax5.axhline(1.0, color="#ff4081", lw=1.5, ls="--", label="Dominance = 1 (inversion)")
    if inversion_alpha is not None:
        ax5.axvline(inversion_alpha, color="#ffcc02", lw=1.2, ls=":",
                    label=f"α* ≈ {inversion_alpha:.2f}")
    ax5.fill_between(alphas, dominance_curve, 1.0,
                     where=(dominance_curve < 1.0), alpha=0.15,
                     color=TRAJ_COLOR_INT, label="S dominates")
    ax5.fill_between(alphas, dominance_curve, 1.0,
                     where=(dominance_curve > 1.0), alpha=0.15,
                     color=TRAJ_COLOR_EXT, label="D dominates")
    ax5.set_xlabel("α (external policy weight)", color=TEXT_COLOR, fontsize=8)
    ax5.set_ylabel("Dominance(D→S)", color=TEXT_COLOR, fontsize=8)
    leg = ax5.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=GRID_COLOR,
                     labelcolor=TEXT_COLOR)

    # ── Panel 6: Results summary text ────────────────────────────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor(PANEL_BG)
    ax6.axis("off")
    summary_lines = [
        "DOMINANCE SUMMARY",
        "",
        f"  Delta_D  =  {Delta_D:+.4f}",
        f"  Delta_S  =  {Delta_S:+.4f}",
        "",
        f"  Dominance(D→S) = {Dominance:.4f}",
        "",
        "  " + ("S DOMINATES D" if Dominance < 1 else "D DOMINATES S"),
        f"  ratio  ≈  {max(abs(Delta_D), abs(Delta_S)) / (min(abs(Delta_D), abs(Delta_S)) + 1e-12):.2f}×",
        "",
        f"  alpha* ≈ {inversion_alpha:.3f}" if inversion_alpha else "  alpha* not in [0,1]",
        "",
        "  Helicoidal index H:",
        f"    pi_S only:  {H_internal:.3f}",
        f"    pi_D only:  {H_external:.3f}",
        f"    baseline:   {H_baseline:.3f}",
    ]
    y = 0.95
    for line in summary_lines:
        style = {"fontsize": 9, "color": TEXT_COLOR, "family": "monospace",
                 "transform": ax6.transAxes, "va": "top"}
        if line in ("DOMINANCE SUMMARY",):
            style["fontsize"] = 10
            style["color"] = "#ffcc02"
            style["fontweight"] = "bold"
        elif "DOMINATES" in line:
            style["color"] = TRAJ_COLOR_INT if Dominance < 1 else TRAJ_COLOR_EXT
            style["fontweight"] = "bold"
        ax6.text(0.05, y, line, **style)
        y -= 0.068

    # ── Figure title ──────────────────────────────────────────────────────────
    fig.suptitle(
        "Reflexive Causal Dominance in Creator-Created Systems\n"
        "David Botargues Martin — do() Interventions on Helicoidal Dynamics",
        color=TEXT_COLOR, fontsize=11, y=0.98
    )

    out_path = "reflexive_dominance_plot.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    print(f"\n  Figure saved → {out_path}")
    plt.close()

    print()
    print("  Done.")
    print("=" * 62)


if __name__ == "__main__":
    main()
