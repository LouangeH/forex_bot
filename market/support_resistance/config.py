# forex_bot/market/support_resistance/config.py

from dataclasses import dataclass

from forex_bot.core.exceptions import DomainValidationError

from forex_bot.core.validators import (
    non_negative_float,
    positive_float,
    positive_int,
    ratio_0_1,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ZoneScoreWeights:
    """
    Poids utilisés pour calculer la qualité finale
    d'une zone Support/Résistance.

    La somme doit toujours être égale à 1.0.
    """

    touches: float = 0.25
    prominence: float = 0.20
    reaction: float = 0.20
    recency: float = 0.15
    compactness: float = 0.20

    def __post_init__(self) -> None:

        for field_name in (
            "touches",
            "prominence",
            "reaction",
            "recency",
            "compactness",
        ):

            ratio_0_1(
                field_name,
                getattr(
                    self,
                    field_name,
                ),
            )

        total = (
            self.touches
            + self.prominence
            + self.reaction
            + self.recency
            + self.compactness
        )

        if abs(total - 1.0) > 1e-9:

            raise DomainValidationError(
                "La somme des poids du score "
                "doit être égale à 1.0."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class SupportResistanceConfig:
    """
    Paramètres du moteur Support/Résistance.

    Aucun seuil important n'est écrit directement
    dans l'algorithme.

    Cela permettra plus tard de tester différentes
    configurations sans réécrire le code.
    """

    # Une zone doit avoir au moins deux contacts.
    min_touches: int = 2

    # À partir de 4 contacts, le sous-score
    # du nombre de touches atteint 100 %.
    target_touches: int = 4

    # Ignore les pivots extrêmement faibles.
    min_pivot_prominence_atr: float = 0.30

    # Distance maximale entre deux niveaux voisins,
    # exprimée en proportion d'ATR.
    cluster_distance_atr: float = 0.35

    # Distance minimale en points MT5.
    min_cluster_distance_points: float = 5.0

    # Petite marge ajoutée autour des contacts.
    zone_padding_atr: float = 0.10

    # Largeur minimale d'un demi-côté de zone.
    min_zone_half_width_points: float = 3.0

    # Empêche plusieurs niveaux différents
    # d'être fusionnés dans une zone gigantesque.
    max_cluster_width_atr: float = 1.25

    # Nombre de bougies observées après un pivot
    # pour mesurer la réaction du prix.
    reaction_bars: int = 8

    # Valeurs utilisées pour normaliser les scores.
    target_prominence_atr: float = 1.0
    target_reaction_atr: float = 1.0

    # Demi-vie du score de récence.
    #
    # Sur M15 :
    # 96 bougies ≈ 24 heures.
    recency_half_life_bars: int = 96

    # Empêche un pivot énorme de dominer entièrement
    # le calcul du centre de la zone.
    prominence_weight_cap: float = 3.0

    # Influence supplémentaire de la réaction
    # sur le poids du contact.
    reaction_weight_factor: float = 0.50

    # Score minimal pour conserver une zone.
    min_quality: float = 0.45

    score_weights: ZoneScoreWeights = (
        ZoneScoreWeights()
    )

    def __post_init__(self) -> None:

        positive_int(
            "min_touches",
            self.min_touches,
        )

        positive_int(
            "target_touches",
            self.target_touches,
        )

        if self.min_touches < 2:

            raise DomainValidationError(
                "Une zone S/R doit avoir "
                "au moins deux contacts."
            )

        if (
            self.target_touches
            < self.min_touches
        ):

            raise DomainValidationError(
                "target_touches doit être "
                ">= min_touches."
            )

        non_negative_float(
            "min_pivot_prominence_atr",
            self.min_pivot_prominence_atr,
        )

        positive_float(
            "cluster_distance_atr",
            self.cluster_distance_atr,
        )

        non_negative_float(
            "min_cluster_distance_points",
            self.min_cluster_distance_points,
        )

        non_negative_float(
            "zone_padding_atr",
            self.zone_padding_atr,
        )

        non_negative_float(
            "min_zone_half_width_points",
            self.min_zone_half_width_points,
        )

        positive_float(
            "max_cluster_width_atr",
            self.max_cluster_width_atr,
        )

        positive_int(
            "reaction_bars",
            self.reaction_bars,
        )

        positive_float(
            "target_prominence_atr",
            self.target_prominence_atr,
        )

        positive_float(
            "target_reaction_atr",
            self.target_reaction_atr,
        )

        positive_int(
            "recency_half_life_bars",
            self.recency_half_life_bars,
        )

        positive_float(
            "prominence_weight_cap",
            self.prominence_weight_cap,
        )

        non_negative_float(
            "reaction_weight_factor",
            self.reaction_weight_factor,
        )

        ratio_0_1(
            "min_quality",
            self.min_quality,
        )

        if not isinstance(
            self.score_weights,
            ZoneScoreWeights,
        ):

            raise DomainValidationError(
                "score_weights doit être "
                "ZoneScoreWeights."
            )