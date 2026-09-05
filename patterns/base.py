# forex_bot/patterns/base.py

from __future__ import annotations

from abc import ABC, abstractmethod

from forex_bot.core.models import PatternMatch

from .context import PatternContext


class PatternDetector(ABC):
    """
    Interface commune de tous les détecteurs.

    Pour ajouter une nouvelle figure :

        class MyDetector(PatternDetector)

    Aucun changement du PatternEngine
    ne sera nécessaire.
    """

    name: str

    version: str

    @abstractmethod
    def detect(
        self,
        context: PatternContext,
    ) -> tuple[
        PatternMatch,
        ...
    ]:

        raise NotImplementedError