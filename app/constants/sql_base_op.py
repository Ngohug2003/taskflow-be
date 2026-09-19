from enum import Enum

class SqlBasicOp(Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GE = "ge"
    LE = "le"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"
