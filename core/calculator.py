"""飞机总体参数核心计算"""
import numpy as np
from core.formulas import (
    G, WEIGHT_PER_PASSENGER, CARGO_RATIO,
    EMPTY_WEIGHT_COEF, L_D_CRUISE, SFC_CRUISE,
    WING_LOADING_RANGE, TW_TAKEOFF, ASPECT_RATIO_TYPICAL,
    FUSELAGE_LENGTH_COEF, mach_to_speed,
)


def calculate_aircraft(
    n_passengers: int,
    range_km: float,
    cruise_mach: float,
    cruise_altitude_m: float,
    engine_type: str = "turbofan",
    aspect_ratio: float = None,
):
    n_passengers = max(20, min(500, int(n_passengers)))
    range_km = max(500, min(15000, range_km))
    cruise_mach = max(0.4, min(0.9, cruise_mach))
    cruise_altitude_m = max(3000, min(13000, cruise_altitude_m))

    if engine_type not in EMPTY_WEIGHT_COEF:
        engine_type = "turbofan"
    if aspect_ratio is None:
        aspect_ratio = ASPECT_RATIO_TYPICAL[engine_type]

    # 载荷
    W_passengers = n_passengers * WEIGHT_PER_PASSENGER * G
    W_cargo = W_passengers * CARGO_RATIO
    W_payload = W_passengers + W_cargo

    # 巡航参数
    V_cruise = mach_to_speed(cruise_mach, cruise_altitude_m)
    L_D = L_D_CRUISE[engine_type]
    SFC = SFC_CRUISE[engine_type]
    R_meters = range_km * 1000.0

    # 迭代
    W_TO = 50000 * G
    empty_coef = EMPTY_WEIGHT_COEF[engine_type]
    for iteration in range(50):
        W_empty = empty_coef["A"] * (W_TO / 1000.0) ** empty_coef["C"] * W_TO
        exponent = R_meters * G * SFC / (V_cruise * L_D)
        W_start_over_end = np.exp(exponent)
        W_fuel = W_TO * (1 - 1.0 / W_start_over_end)
        W_TO_new = W_empty + W_fuel + W_payload
        if abs(W_TO_new - W_TO) / W_TO < 1e-4:
            W_TO = W_TO_new
            break
        W_TO = W_TO_new

    # 最终值
    W_empty = empty_coef["A"] * (W_TO / 1000.0) ** empty_coef["C"] * W_TO
    W_fuel = W_TO - W_empty - W_payload

    # 机翼
    W_S_range = WING_LOADING_RANGE[engine_type]
    W_S_design = np.mean(W_S_range)
    S_wing = W_TO / W_S_design
    b_wingspan = np.sqrt(aspect_ratio * S_wing)
    chord_mean = S_wing / b_wingspan

    # 推力
    TW = TW_TAKEOFF[engine_type]
    T_required = TW * W_TO

    # 机身
    W_TO_ton = W_TO / (1000 * G)
    L_fuselage = FUSELAGE_LENGTH_COEF * (W_TO_ton ** 0.43) * 10

    # 阻力
    D_cruise = W_TO / L_D

    return {
        "n_passengers": n_passengers,
        "range_km": range_km,
        "cruise_mach": cruise_mach,
        "cruise_altitude_m": cruise_altitude_m,
        "engine_type": engine_type,
        "aspect_ratio": aspect_ratio,
        "W_TO_ton": W_TO / (1000 * G),
        "W_empty_ton": W_empty / (1000 * G),
        "W_fuel_ton": W_fuel / (1000 * G),
        "W_payload_ton": W_payload / (1000 * G),
        "empty_ratio": W_empty / W_TO,
        "fuel_ratio": W_fuel / W_TO,
        "payload_ratio": W_payload / W_TO,
        "S_wing_m2": S_wing,
        "wingspan_m": b_wingspan,
        "mean_chord_m": chord_mean,
        "T_required_kN": T_required / 1000,
        "T_W_ratio": TW,
        "W_S_Nm2": W_S_design,
        "L_D": L_D,
        "V_cruise_ms": V_cruise,
        "D_cruise_kN": D_cruise / 1000,
        "L_fuselage_m": L_fuselage,
        "iterations": iteration + 1,
    }