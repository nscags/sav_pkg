from bgpy.enums import YamlAbleEnum

class Outcomes(YamlAbleEnum):
    """Outcomes for traceback"""
    
    ORIGIN: int = 1
    DISCONNECTED: int = 2     # Not on path
    FALSE_NEGATIVE: int = 3   # Incorrectly allows spoofed packet
    TRUE_NEGATIVE: int = 4    # Correctly allows legitimate packet
    FALSE_POSITIVE: int = 5   # Incorrectly block legitimate packet
    TRUE_POSITIVE: int = 6    # Correctly blocks spoofed packet
    FORWARD: int = 7
    FILTERED_ON_PATH: int = 8 # Filtered on path from attacker/victim -> reflector


class Prefixes(YamlAbleEnum):
    """Prefixes to use for attacks

    prefix always belongs to the victim
    """
    VICTIM: str = "7.7.7.0/24"
    ATTACKER: str = "6.6.6.0/24"
    REFLECTOR: str = "1.2.0.0/24"


class ASNs(YamlAbleEnum):
    """Default ASNs for various ASNs"""

    ATTACKER: int = 666
    VICTIM: int = 777
    REFLECTOR: int = 555

class ASGroups(YamlAbleEnum):
    """AS types"""

    IXPS: str = "ixp"
    # NOTE: only the IXP group has IXPs
    STUBS: str = "stub"
    MULTIHOMED: str = "multihomed"
    STUBS_OR_MH: str = "stub_or_multihomed"
    INPUT_CLIQUE: str = "input_clique"
    # Not stubs, multihomed, or input clique
    ETC: str = "etc"
    # not stubs or multihomed
    TRANSIT: str = "transit"
    ALL_WOUT_IXPS: str = "all_wout_ixps"

    REFLECTORS: str = "reflectors"