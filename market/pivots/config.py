from dataclasses import dataclass

from forex_bot.core.validators import (
    non_negative_float,
    positive_int,
)


@dataclass(
    frozen=True,
    slots=True,
)
class PivotDetectorConfig:
    """
    Configuration du détecteur de pivots.

    Les paramètres sont séparés du détecteur afin
    que nous puissions tester plusieurs réglages
    sans modifier l'algorithme.
    """

    # Nombre de bougies à gauche du pivot.
    left_bars: int = 3

    # Nombre de bougies nécessaires à droite
    # pour confirmer définitivement le pivot.
    right_bars: int = 3

    # Période utilisée pour calculer l'ATR.
    atr_period: int = 14

    # Prominence minimale exprimée en ATR.
    #
    # Exemple :
    # 0.30 signifie que le mouvement autour du pivot
    # doit représenter au minimum 30 % de l'ATR.
    #
    # Ce paramètre sera calibré par backtesting.
    min_prominence_atr: float = 0.30

    # Deux pivots du même type trop proches
    # sont considérés comme appartenant au même swing.
    min_separation_bars: int = 3

    # Tolérance permettant de reconnaître un plateau :
    #
    #      _____
    #     /     \
    #
    # au lieu de créer plusieurs Pivot High.
    #
    # La valeur est exprimée en POINTS du symbole MT5.
    plateau_tolerance_points: float = 1.0

    def __post_init__(self) -> None:

        positive_int(
            "left_bars",
            self.left_bars,
        )

        positive_int(
            "right_bars",
            self.right_bars,
        )

        positive_int(
            "atr_period",
            self.atr_period,
        )

        non_negative_float(
            "min_prominence_atr",
            self.min_prominence_atr,
        )

        positive_int(
            "min_separation_bars",
            self.min_separation_bars,
        )

        non_negative_float(
            "plateau_tolerance_points",
            self.plateau_tolerance_points,
        )

    @property
    def confirmation_strength(self) -> int:
        """
        Nombre total de bougies utilisées
        autour d'un pivot.

        Exemple :
        3 à gauche + 3 à droite = force 6.
        """

        return (
            self.left_bars
            + self.right_bars
        )