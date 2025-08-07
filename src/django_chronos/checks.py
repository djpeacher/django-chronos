from django.conf import settings
from django.core.checks import Warning, register

@register()
def check_stats_settings(app_configs, **kwargs):
    warnings = []
    
    if hasattr(settings, "CHRONOS_SWAP_METHOD"):
        swap_method = settings.CHRONOS_SWAP_METHOD
        if swap_method not in ['replace', 'prepend', 'append']:
            warnings.append(Warning(f"The CHRONOS_SWAP_METHOD setting should be set to 'replace', 'prepend', or 'append'. Defaulting to 'replace'. Got: {swap_method}"))

    if hasattr(settings, "CHRONOS_SWAP_TARGET"):
        swap_target = settings.CHRONOS_SWAP_TARGET
        if not swap_target:
            warnings.append(Warning("The CHRONOS_SWAP_TARGET setting cannot be None or empty string as this will prevent stats from being displayed."))

    if hasattr(settings, "CHRONOS_SHOW_IN_PRODUCTION"):
        show_in_production = settings.CHRONOS_SHOW_IN_PRODUCTION
        if not isinstance(show_in_production, bool):
            warnings.append(Warning(f"The CHRONOS_SHOW_IN_PRODUCTION setting must be a boolean (True/False). Defaulting to False. Got: {show_in_production}"))

    return warnings
