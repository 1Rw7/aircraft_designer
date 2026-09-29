"""飞机总体设计公式库 + 常数"""

G = 9.80665
RHO_SL = 1.225
SOUND_SPEED_SL = 340.29

WEIGHT_PER_PASSENGER = 95.0
CARGO_RATIO = 0.15

EMPTY_WEIGHT_COEF = {
    "turbofan": {"A": 0.88, "C": -0.06},
    "turboprop": {"A": 0.95, "C": -0.07},
}

L_D_CRUISE = {
    "turbofan": 17.0,
    "turboprop": 14.0,
}

SFC_CRUISE = {
    "turbofan": 1.6e-5,
    "turboprop": 1.0e-5,
}

WING_LOADING_RANGE = {
    "turbofan": (4500, 6500),
    "turboprop": (2500, 4000),
}

TW_TAKEOFF = {
    "turbofan": 0.30,
    "turboprop": 0.22,
}

ASPECT_RATIO_TYPICAL = {
    "turbofan": 9.5,
    "turboprop": 11.0,
}

SWEEP_ANGLE_TYPICAL = {
    "turbofan": 25.0,
    "turboprop": 0.0,
}

TAPER_RATIO = 0.30
FUSELAGE_LENGTH_COEF = 0.44


def air_density(altitude_m):
    if altitude_m < 0:
        return RHO_SL
    return RHO_SL * (1 - 0.0000226 * altitude_m) ** 4.256


def mach_to_speed(mach, altitude_m):
    T0 = 288.15
    if altitude_m < 11000:
        T = T0 - 0.0065 * altitude_m
    else:
        T = 216.65
    a = (1.4 * 287.05 * T) ** 0.5
    return mach * a