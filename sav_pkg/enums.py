from bgpy.enums import YamlAbleEnum

class Outcomes(YamlAbleEnum):
    # SAV Outcomes
    FALSE_POSITIVE: int = 1 # Incorrectly block legitimate packet
    FALSE_NEGATIVE: int = 2 # Incorrectly allows spoofed packet
    TRUE_POSITIVE: int = 3  # Correctly blocks spoofed packet
    TRUE_NEGATIVE: int = 4  # Correctly allows legitimate packet

    # Non-SAV Outcomes
    DISCONNECTED: int = 5 # ASes which do not recieve a packet (filtered by AS on path)
    ATTACKER: int = 6     # Attacker AS, enumerating outcome so it doesn't get counted as disconnected
    VICTIM: int = 7       # Victim AS,   ^^^


class Prefixes(YamlAbleEnum):
    """Prefixes to use for attacks

    prefix always belongs to the victim
    """
    VICTIM: str = "1.0.0.0/24"
    ATTACKER: str = "1.1.0.0/24"
    REFLECTOR: str = "1.2.0.0/24"


class ASNs(YamlAbleEnum):
    """Default ASNs for various ASNs"""

    ATTACKER: int = 666
    VICTIM: int = 777
    REFLECTOR: int = 555
