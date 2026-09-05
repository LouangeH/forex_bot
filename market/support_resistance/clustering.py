# forex_bot/market/support_resistance/clustering.py

from collections.abc import Sequence

from statistics import median

from forex_bot.core.models import (
    SymbolSpec,
)

from .config import (
    SupportResistanceConfig,
)

from .types import (
    ZoneTouch,
)


class ZoneClusterer:
    """
    Regroupe les contacts proches en clusters.

    Support et Résistance sont envoyés séparément :
    cette classe ne mélange jamais Pivot High
    et Pivot Low.
    """

    def __init__(
        self,
        config: SupportResistanceConfig,
    ) -> None:

        self._config = config

    def cluster(
        self,
        touches: Sequence[ZoneTouch],

        symbol_spec: SymbolSpec,
    ) -> tuple[
        tuple[ZoneTouch, ...],
        ...
    ]:

        if not touches:

            return ()

        ordered = sorted(
            touches,
            key=lambda touch:
            touch.price,
        )

        clusters: list[
            list[ZoneTouch]
        ] = [
            [ordered[0]]
        ]

        for touch in ordered[1:]:

            previous = (
                clusters[-1][-1]
            )

            threshold = (
                self._link_threshold(
                    first=previous,
                    second=touch,
                    symbol_spec=symbol_spec,
                )
            )

            if (
                abs(
                    touch.price
                    - previous.price
                )
                <= threshold
            ):

                clusters[-1].append(
                    touch
                )

            else:

                clusters.append(
                    [touch]
                )

        final_clusters: list[
            tuple[ZoneTouch, ...]
        ] = []

        for cluster in clusters:

            final_clusters.extend(
                self._split_if_too_wide(
                    cluster=cluster,

                    symbol_spec=symbol_spec,
                )
            )

        return tuple(
            final_clusters
        )

    def _link_threshold(
        self,
        *,
        first: ZoneTouch,

        second: ZoneTouch,

        symbol_spec: SymbolSpec,
    ) -> float:
        """
        Distance maximale autorisée entre
        deux contacts voisins.
        """

        atr_reference = (
            first.atr
            + second.atr
        ) / 2

        atr_distance = (
            atr_reference
            * self._config
            .cluster_distance_atr
        )

        point_distance = (
            self._config
            .min_cluster_distance_points
            * symbol_spec.point
        )

        return max(
            atr_distance,
            point_distance,
        )

    def _split_if_too_wide(
        self,
        *,
        cluster: Sequence[ZoneTouch],

        symbol_spec: SymbolSpec,
    ) -> list[
        tuple[ZoneTouch, ...]
    ]:
        """
        Évite l'effet de chaîne.

        Exemple problématique :

        1.1700 proche de 1.1710
        1.1710 proche de 1.1720
        1.1720 proche de 1.1730

        Un clustering naïf pourrait fusionner
        tout cela alors que 1.1700 et 1.1730
        sont très éloignés.
        """

        if len(cluster) <= 1:

            return [
                tuple(cluster)
            ]

        ordered = sorted(
            cluster,
            key=lambda touch:
            touch.price,
        )

        median_atr = median(
            touch.atr
            for touch
            in ordered
        )

        maximum_width = max(

            (
                2
                * self._config
                .min_zone_half_width_points
                * symbol_spec.point
            ),

            (
                median_atr
                * self._config
                .max_cluster_width_atr
            ),
        )

        actual_width = (
            ordered[-1].price
            - ordered[0].price
        )

        if (
            actual_width
            <= maximum_width
        ):

            return [
                tuple(ordered)
            ]

        # On cherche le plus grand espace
        # entre deux niveaux successifs.
        split_position = max(

            range(
                1,
                len(ordered),
            ),

            key=lambda index:
            self._normalized_gap(
                left=ordered[
                    index - 1
                ],

                right=ordered[
                    index
                ],

                symbol_spec=symbol_spec,
            ),
        )

        left_side = ordered[
            :split_position
        ]

        right_side = ordered[
            split_position:
        ]

        return (
            self._split_if_too_wide(
                cluster=left_side,
                symbol_spec=symbol_spec,
            )

            +

            self._split_if_too_wide(
                cluster=right_side,
                symbol_spec=symbol_spec,
            )
        )

    @staticmethod
    def _normalized_gap(
        *,
        left: ZoneTouch,

        right: ZoneTouch,

        symbol_spec: SymbolSpec,
    ) -> float:

        atr_reference = max(

            (
                left.atr
                + right.atr
            ) / 2,

            symbol_spec.point,
        )

        return (
            abs(
                right.price
                - left.price
            )
            / atr_reference
        )