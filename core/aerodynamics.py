"""气动性能计算：升力曲线、阻力极曲线、升阻比"""
import numpy as np
from core.formulas import air_density


def lift_curve_analysis(
    S_wing: float, AR: float, sweep_deg: float = 25.0,
    mach: float = 0.78, altitude_m: float = 11000,
    alpha_deg: np.ndarray = None,
):
    if alpha_deg is None:
        alpha_deg = np.linspace(-5, 20, 100)

    a0 = 2 * np.pi
    sweep_rad = np.deg2rad(sweep_deg)
    a0_swept = a0 * np.cos(sweep_rad)

    e_oswald = 0.80
    CL_alpha_per_rad = a0_swept / (1 + a0_swept / (np.pi * AR * e_oswald))
    CL_alpha_per_deg = CL_alpha_per_rad * np.pi / 180

    alpha_0 = -2.0
    CL = CL_alpha_per_deg * (alpha_deg - alpha_0)

    CL_max = 1.4 + 0.3 * np.log10(max(AR, 3)) * np.cos(sweep_rad)
    CL_max = min(CL_max, 1.8)
    alpha_stall = alpha_0 + CL_max / CL_alpha_per_deg

    CL = np.where(alpha_deg > alpha_stall,
                  CL_max * (1 - 0.05 * (alpha_deg - alpha_stall)),
                  CL)

    return {
        "alpha_deg": alpha_deg,
        "CL": CL,
        "CL_alpha_per_deg": CL_alpha_per_deg,
        "CL_max": CL_max,
        "alpha_stall": alpha_stall,
        "alpha_0": alpha_0,
    }


def drag_polar(CL: np.ndarray, AR: float,
               sweep_deg: float = 25.0, mach: float = 0.78):
    if mach < 0.7:
        CD0 = 0.018
    elif mach < 0.85:
        CD0 = 0.018 + 0.06 * (mach - 0.7) ** 2
    else:
        CD0 = 0.025 + 0.1 * (mach - 0.85)

    sweep_rad = np.deg2rad(sweep_deg)
    e_oswald = 0.80 * np.cos(sweep_rad)
    k = 1.0 / (np.pi * AR * e_oswald)

    CD = CD0 + k * CL ** 2
    return {"CL": CL, "CD": CD, "CD0": CD0, "k": k}


def lift_to_drag_vs_speed(
    W_TO_N: float, S_wing: float, AR: float,
    altitude_m: float, mach: np.ndarray = None, sweep_deg: float = 25.0,
):
    if mach is None:
        mach = np.linspace(0.4, 0.85, 50)

    if altitude_m < 11000:
        T = 288.15 - 0.0065 * altitude_m
    else:
        T = 216.65
    a = (1.4 * 287.05 * T) ** 0.5
    rho = air_density(altitude_m)

    V = mach * a
    W_S = W_TO_N / S_wing
    q = 0.5 * rho * V ** 2
    CL = W_S / q

    CD0 = np.where(
        mach < 0.7, 0.018,
        np.where(mach < 0.85,
                 0.018 + 0.06 * (mach - 0.7) ** 2,
                 0.025 + 0.1 * (mach - 0.85))
    )

    sweep_rad = np.deg2rad(sweep_deg)
    e_oswald = 0.80 * np.cos(sweep_rad)
    k = 1.0 / (np.pi * AR * e_oswald)

    CD = CD0 + k * CL ** 2
    LD = CL / CD

    return {
        "mach": mach, "V_ms": V, "CL": CL, "CD": CD, "LD": LD,
        "max_LD": float(np.max(LD)),
        "mach_at_max_LD": float(mach[np.argmax(LD)]),
    }


def stall_speed(W_TO_N: float, S_wing: float,
                CL_max: float, altitude_m: float = 0):
    rho = air_density(altitude_m)
    V_stall = np.sqrt(2 * W_TO_N / (rho * S_wing * CL_max))
    return float(V_stall)