"""
Studious Broccoli - Post-quantum continuous-excellence delivery platform
powered by a synthetic brain-tissue natural AI engine.
"""

__version__ = "0.1.0"
__author__ = "Casper Crabbe Lab"

from .core.engine import ExcellenceEngine
from .neural.brain_tissue import SyntheticBrainTissue
from .security.post_quantum import PostQuantumSecurity
from .excellence.delivery import ContinuousExcellenceDelivery
from .fabric.cognitive import CognitiveFabric

__all__ = [
    "ExcellenceEngine",
    "SyntheticBrainTissue",
    "PostQuantumSecurity",
    "ContinuousExcellenceDelivery",
    "CognitiveFabric",
]
