from bgpy.enums import YamlAbleEnum


class Outcomes(YamlAbleEnum):
    """Outcomes for traceback"""

    ORIGIN: int = 1
    DISCONNECTED: int = 2      # Victim/Attacker cannot route to reflector
    FALSE_NEGATIVE: int = 3    # Incorrectly allows spoofed packet
    TRUE_NEGATIVE: int = 4     # Correctly allows legitimate packet
    FALSE_POSITIVE: int = 5    # Incorrectly block legitimate packet
    TRUE_POSITIVE: int = 6     # Correctly blocks spoofed packet
    FORWARD: int = 7           # Packet forwarded (no SAV policy applied)
    FILTERED_ON_PATH: int = 8  # Filtered on path from attacker/victim -> reflector

    # Used for metrics
    ATTACKER_SUCCESS: int = 9 # FN or Forward
    VICTIM_SUCCESS: int = 10  # TN or Forward


class Prefixes(YamlAbleEnum):
    """Default Prefixes"""

    VICTIM: str = "7.7.7.0/24"
    ATTACKER: str = "6.6.6.0/24"
    REFLECTOR: str = "1.2.0.0/24"


class ASNs(YamlAbleEnum):
    """Default ASNs for various ASNs"""

    ATTACKER: int = 666
    VICTIM: int = 777
    REFLECTOR: int = 555


class Interfaces(YamlAbleEnum):
    """Interfaces to apply SAV policy"""
    CUSTOMER: int = 0
    PROVIDER: int = 1
    PEER: int = 3