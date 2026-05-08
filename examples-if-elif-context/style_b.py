def decide_route(channel: str, priority: int) -> str:
    """Decide routing target by channel and priority."""
    if channel == 'test':
        return 'debug_only'
    elif channel == 'prod':
        return 'monitoring'
    elif priority == 1:
        return 'urgent'
    elif priority == 2:
        return 'fast'
    else:
        return 'standard'
