"""
Excellence Engine - Core orchestration layer for the platform.

The ExcellenceEngine coordinates all subsystems:
- Synthetic brain-tissue neural engine
- Post-quantum security layer
- Continuous excellence delivery
- Cognitive fabric
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class EngineConfig:
    """Configuration for the Excellence Engine."""

    # Neural engine settings
    neural_layers: int = 12
    synaptic_plasticity: float = 0.01
    emotional_depth: float = 0.5

    # Security settings
    pq_algorithm: str = "kyber768"  # CRYSTALS-Kyber variant
    key_rotation_hours: int = 24

    # Excellence delivery settings
    feedback_interval_seconds: int = 60
    optimization_threshold: float = 0.05

    # Fabric settings
    max_connections: int = 1000
    shared_learning_enabled: bool = True


@dataclass
class EngineState:
    """Current state of the Excellence Engine."""

    started_at: datetime = field(default_factory=datetime.utcnow)
    is_running: bool = False
    active_connections: int = 0
    decisions_made: int = 0
    excellence_score: float = 0.0
    last_optimization: Optional[datetime] = None


class ExcellenceEngine:
    """
    Main orchestration engine for the post-quantum continuous-excellence platform.

    This engine coordinates all subsystems to deliver adaptive intelligence
    with quantum-resilient security and continuous optimization.

    Example:
        >>> engine = ExcellenceEngine()
        >>> await engine.initialize()
        >>> await engine.start()
        >>> result = await engine.process_decision(data)
        >>> await engine.stop()
    """

    def __init__(self, config: Optional[EngineConfig] = None):
        """
        Initialize the Excellence Engine.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or EngineConfig()
        self.state = EngineState()
        self._neural_engine = None
        self._security_layer = None
        self._excellence_system = None
        self._cognitive_fabric = None

        logger.info("ExcellenceEngine initialized with config: %s", self.config)

    async def initialize(self) -> None:
        """
        Initialize all subsystems.

        This method sets up:
        1. Post-quantum security layer
        2. Synthetic brain-tissue neural engine
        3. Continuous excellence delivery system
        4. Cognitive fabric
        """
        logger.info("Initializing Excellence Engine subsystems...")

        # Initialize security layer first (foundation)
        from ..security.post_quantum import PostQuantumSecurity

        self._security_layer = PostQuantumSecurity(
            algorithm=self.config.pq_algorithm,
            key_rotation_hours=self.config.key_rotation_hours,
        )
        await self._security_layer.initialize()
        logger.info("Post-quantum security layer initialized")

        # Initialize neural engine
        from ..neural.brain_tissue import SyntheticBrainTissue

        self._neural_engine = SyntheticBrainTissue(
            layers=self.config.neural_layers,
            plasticity=self.config.synaptic_plasticity,
            emotional_depth=self.config.emotional_depth,
        )
        await self._neural_engine.initialize()
        logger.info("Synthetic brain-tissue neural engine initialized")

        # Initialize excellence delivery system
        from ..excellence.delivery import ContinuousExcellenceDelivery

        self._excellence_system = ContinuousExcellenceDelivery(
            feedback_interval=self.config.feedback_interval_seconds,
            optimization_threshold=self.config.optimization_threshold,
        )
        await self._excellence_system.initialize()
        logger.info("Continuous excellence delivery system initialized")

        # Initialize cognitive fabric
        from ..fabric.cognitive import CognitiveFabric

        self._cognitive_fabric = CognitiveFabric(
            max_connections=self.config.max_connections,
            shared_learning_enabled=self.config.shared_learning_enabled,
        )
        await self._cognitive_fabric.initialize()
        logger.info("Cognitive fabric initialized")

        logger.info("All subsystems initialized successfully")

    async def start(self) -> None:
        """Start the engine and all subsystems."""
        if self.state.is_running:
            logger.warning("Engine is already running")
            return

        logger.info("Starting Excellence Engine...")
        self.state.is_running = True
        self.state.started_at = datetime.utcnow()

        # Start all subsystems
        await self._security_layer.start()
        await self._neural_engine.start()
        await self._excellence_system.start()
        await self._cognitive_fabric.start()

        logger.info("Excellence Engine started successfully")

    async def stop(self) -> None:
        """Stop the engine and all subsystems gracefully."""
        if not self.state.is_running:
            logger.warning("Engine is not running")
            return

        logger.info("Stopping Excellence Engine...")
        self.state.is_running = False

        # Stop all subsystems
        await self._cognitive_fabric.stop()
        await self._excellence_system.stop()
        await self._neural_engine.stop()
        await self._security_layer.stop()

        logger.info("Excellence Engine stopped")

    async def process_decision(
        self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a decision through the excellence engine.

        This method:
        1. Secures the data with post-quantum encryption
        2. Analyzes through the neural engine
        3. Optimizes via the excellence system
        4. Coordinates through the cognitive fabric

        Args:
            data: Input data for decision processing
            context: Optional contextual information

        Returns:
            Decision result with metadata
        """
        if not self.state.is_running:
            raise RuntimeError("Engine must be started before processing decisions")

        logger.debug("Processing decision: %s", data.keys())

        # Step 1: Secure the data
        secured_data = await self._security_layer.encrypt(data)

        # Step 2: Neural analysis
        neural_output = await self._neural_engine.analyze(secured_data, context)

        # Step 3: Excellence optimization
        optimized_output = await self._excellence_system.optimize(
            neural_output, context
        )

        # Step 4: Fabric coordination
        result = await self._cognitive_fabric.coordinate(optimized_output)

        # Update metrics
        self.state.decisions_made += 1
        self.state.excellence_score = (
            self._excellence_system.calculate_excellence_score()
        )

        logger.debug("Decision processed successfully")
        return result

    def get_state(self) -> EngineState:
        """Get current engine state."""
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive engine metrics.

        Returns:
            Dictionary containing metrics from all subsystems
        """
        return {
            "engine": {
                "is_running": self.state.is_running,
                "uptime_seconds": (
                    datetime.utcnow() - self.state.started_at
                ).total_seconds(),
                "decisions_made": self.state.decisions_made,
                "excellence_score": self.state.excellence_score,
            },
            "neural": self._neural_engine.get_metrics()
            if self._neural_engine
            else {},
            "security": self._security_layer.get_metrics()
            if self._security_layer
            else {},
            "excellence": self._excellence_system.get_metrics()
            if self._excellence_system
            else {},
            "fabric": self._cognitive_fabric.get_metrics()
            if self._cognitive_fabric
            else {},
        }
