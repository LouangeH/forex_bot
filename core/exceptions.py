class ForexBotError(Exception):
    """
    Exception de base du projet.
    """


class DomainValidationError(
    ForexBotError,
    ValueError,
):
    """
    Une donnée métier est incohérente.

    Exemple :
    HIGH inférieur au CLOSE d'une bougie.
    """


class ConfigurationError(ForexBotError):
    """
    Configuration incorrecte ou dangereuse.
    """


class SafetyViolation(ForexBotError):
    """
    Une protection de sécurité interdit
    volontairement une opération.
    """