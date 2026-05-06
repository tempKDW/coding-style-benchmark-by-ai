USER = "USER"
ADMIN = "ADMIN"
SUPER_ADMIN = "SUPER_ADMIN"

ALLOWED_ROLES = (USER, ADMIN, SUPER_ADMIN)


def validate_role(role):
    if role not in ALLOWED_ROLES:
        raise ValueError(f"invalid role: {role}")
    return role


def can_access(role, resource):
    validate_role(role)
    if role == USER:
        return resource in {"profile", "feed"}
    if role == ADMIN:
        return resource in {"profile", "feed", "users", "logs"}
    if role == SUPER_ADMIN:
        return True
    return False


def role_label(role):
    validate_role(role)
    if role == USER:
        return "사용자"
    if role == ADMIN:
        return "관리자"
    if role == SUPER_ADMIN:
        return "최고관리자"
    return ""
