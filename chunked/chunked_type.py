from enum import Enum


class ChunkedType(Enum):
    Start = "START",
    End = "END",
    Both = "BOTH",
    Nan = "NAN"