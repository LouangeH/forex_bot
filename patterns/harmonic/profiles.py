# forex_bot/patterns/harmonic/profiles.py

from forex_bot.core.enums import (
    PatternType,
)

from .types import (
    ABCDProfile,
    CypherProfile,
    RatioBand,
    SharkProfile,
    ThreeDrivesProfile,
    XABCDProfile,
)


# =========================================================
# GARTLEY
# =========================================================

GARTLEY = XABCDProfile(

    bullish_type=(
        PatternType.GARTLEY_BULLISH
    ),

    bearish_type=(
        PatternType.GARTLEY_BEARISH
    ),

    b_xa=RatioBand(
        0.55,
        0.70,
        0.618,
    ),

    bc_ab=RatioBand(
        0.382,
        0.886,
        0.618,
    ),

    cd_bc=RatioBand(
        1.13,
        1.70,
        1.414,
    ),

    ad_xa=RatioBand(
        0.74,
        0.83,
        0.786,
    ),
)


# =========================================================
# BAT
# =========================================================

BAT = XABCDProfile(

    bullish_type=(
        PatternType.BAT_BULLISH
    ),

    bearish_type=(
        PatternType.BAT_BEARISH
    ),

    b_xa=RatioBand(
        0.382,
        0.50,
        0.50,
    ),

    bc_ab=RatioBand(
        0.382,
        0.886,
        0.618,
    ),

    cd_bc=RatioBand(
        1.618,
        2.618,
        2.0,
    ),

    ad_xa=RatioBand(
        0.84,
        0.93,
        0.886,
    ),
)


# =========================================================
# BUTTERFLY
# =========================================================

BUTTERFLY = XABCDProfile(

    bullish_type=(
        PatternType.BUTTERFLY_BULLISH
    ),

    bearish_type=(
        PatternType.BUTTERFLY_BEARISH
    ),

    b_xa=RatioBand(
        0.74,
        0.83,
        0.786,
    ),

    bc_ab=RatioBand(
        0.382,
        0.886,
        0.618,
    ),

    cd_bc=RatioBand(
        1.618,
        2.618,
        2.0,
    ),

    ad_xa=RatioBand(
        1.20,
        1.70,
        1.272,
    ),
)


# =========================================================
# CRAB
# =========================================================

CRAB = XABCDProfile(

    bullish_type=(
        PatternType.CRAB_BULLISH
    ),

    bearish_type=(
        PatternType.CRAB_BEARISH
    ),

    b_xa=RatioBand(
        0.382,
        0.618,
        0.50,
    ),

    bc_ab=RatioBand(
        0.382,
        0.886,
        0.618,
    ),

    cd_bc=RatioBand(
        2.24,
        3.618,
        3.0,
    ),

    ad_xa=RatioBand(
        1.55,
        1.68,
        1.618,
    ),
)


# =========================================================
# DEEP CRAB
# =========================================================

DEEP_CRAB = XABCDProfile(

    bullish_type=(
        PatternType.DEEP_CRAB_BULLISH
    ),

    bearish_type=(
        PatternType.DEEP_CRAB_BEARISH
    ),

    b_xa=RatioBand(
        0.84,
        0.93,
        0.886,
    ),

    bc_ab=RatioBand(
        0.382,
        0.886,
        0.618,
    ),

    cd_bc=RatioBand(
        2.0,
        3.618,
        2.618,
    ),

    ad_xa=RatioBand(
        1.55,
        1.68,
        1.618,
    ),
)


DEFAULT_XABCD_PROFILES = (

    GARTLEY,
    BAT,
    BUTTERFLY,
    CRAB,
    DEEP_CRAB,
)


# =========================================================
# AB = CD
# =========================================================

ABCD = ABCDProfile(

    bullish_type=(
        PatternType.AB_CD_BULLISH
    ),

    bearish_type=(
        PatternType.AB_CD_BEARISH
    ),

    bc_ab=RatioBand(
        0.382,
        0.886,
        0.618,
    ),

    cd_ab=RatioBand(
        0.85,
        1.15,
        1.0,
    ),

    cd_bc=RatioBand(
        1.13,
        2.618,
        1.618,
    ),
)


# =========================================================
# CYPHER
# =========================================================

CYPHER = CypherProfile(

    bullish_type=(
        PatternType.CYPHER_BULLISH
    ),

    bearish_type=(
        PatternType.CYPHER_BEARISH
    ),

    b_xa=RatioBand(
        0.382,
        0.618,
        0.50,
    ),

    c_xa=RatioBand(
        1.272,
        1.414,
        1.35,
    ),

    d_xc=RatioBand(
        0.74,
        0.83,
        0.786,
    ),
)


# =========================================================
# SHARK
#
# Le Shark est particulièrement sujet à des
# variations de définition selon les écoles.
#
# C'est précisément pour cette raison que
# ses rapports restent complètement configurables.
# =========================================================

SHARK = SharkProfile(

    bullish_type=(
        PatternType.SHARK_BULLISH
    ),

    bearish_type=(
        PatternType.SHARK_BEARISH
    ),

    ab_ox=RatioBand(
        1.13,
        1.618,
        1.272,
    ),

    bc_xa=RatioBand(
        1.618,
        2.24,
        2.0,
    ),

    c_ox=RatioBand(
        0.886,
        1.13,
        1.0,
    ),
)


# =========================================================
# THREE DRIVES
# =========================================================

THREE_DRIVES = ThreeDrivesProfile(

    bullish_type=(
        PatternType.THREE_DRIVES_BULLISH
    ),

    bearish_type=(
        PatternType.THREE_DRIVES_BEARISH
    ),

    drive_ratio=RatioBand(
        0.80,
        1.30,
        1.0,
    ),

    correction_ratio=RatioBand(
        0.55,
        0.82,
        0.707,
    ),
)