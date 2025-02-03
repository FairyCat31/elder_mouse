from random import randint
from string import ascii_letters, digits


SYM_IDS = ascii_letters + digits
SYM_LEN = len(SYM_IDS) - 1


def generate_id(len_id: int = 8) -> str:
    result = "".join([SYM_IDS[randint(0, SYM_LEN)] for i in range(len_id)])
    return result
