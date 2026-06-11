# Phase 0: Research & Mathematical Formulation

## Dixon-Coles Likelihood Function
- **Decision**: Use the standard Dixon-Coles Poisson formulation with the $\tau$ (tau) adjustment factor for low scores.
- **Rationale**: The spec strictly requires "low-score dependencies (0-0, 1-0, etc.)". The original Poisson model assumes independence, heavily underestimating draws. The tau function $\tau(x, y)$ explicitly corrects probabilities for $x, y \in \{0, 1\}$.
- **Formulation**:
  - $E_H = \alpha_H \times \beta_A \times \gamma$ (Home expected goals, $\gamma$ is home advantage)
  - $E_A = \alpha_A \times \beta_H$ (Away expected goals)
  - $P(x, y) = \tau(x, y, \rho) \times \frac{E_H^x e^{-E_H}}{x!} \times \frac{E_A^y e^{-E_A}}{y!}$
  - where $\tau(x,y,\rho) = 1 - x y \rho + \dots$ for low scores, and 1 otherwise.

## MLE Optimization & Fallback
- **Decision**: Use `scipy.optimize.minimize` with L-BFGS-B or SLSQP solver.
- **Rationale**: We need bounded optimization since parameters $\alpha, \beta$ must be > 0.
- **Fallback Strategy**: Catch `scipy.optimize` convergence warnings/errors. If failed, automatically increase `ftol` or `maxiter` and retry before failing gracefully.

## Time-Weighting
- **Decision**: Apply an exponential decay weight $w = e^{-\xi \times t}$ where $t$ is days since match.
- **Rationale**: The specification mandates the decay should be $e^{-0.0065 \times \text{days}}$ (half-life of approx. 106 days, standard literature value for Dixon-Coles).
