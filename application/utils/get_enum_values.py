def get_enum_values(enum_class) -> list[str]:
    """Extract string values from Pydantic Enum"""
    return [e.value for e in enum_class]
