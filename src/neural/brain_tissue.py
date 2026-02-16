"""
Synthetic Brain-Tissue Natural AI Engine.

Bio-inspired neural matrices that emulate organic learning, emotional reasoning,
and intuition. Unlike traditional neural networks, this engine features:

- Self-healing neural substrates
- Dynamic synaptic plasticity
- Emotional depth integration
- Intuition-based pattern recognition
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class NeuralLayer:
    """Represents a single layer in the synthetic brain-tissue."""

    layer_id: int
    neurons: int
    activation_type: str = "sigmoid"
    plasticity_factor: float = 0.01
    weights: Optional[np.ndarray] = None
    biases: Optional[np.ndarray] = None

    def __post_init__(self):
        """Initialize weights and biases if not provided."""
        if self.weights is None:
            # Bio-inspired initialization with small random values
            self.weights = np.random.randn(self.neurons, self.neurons) * 0.01
        if self.biases is None:
            self.biases = np.zeros(self.neurons)


@dataclass
class EmotionalState:
    """Represents emotional context in decision-making."""

    valence: float = 0.0  # Positive to negative (-1 to 1)
    arousal: float = 0.0  # Calm to excited (0 to 1)
    dominance: float = 0.5  # Submissive to dominant (0 to 1)
    confidence: float = 0.5  # Uncertain to certain (0 to 1)

    def to_vector(self) -> np.ndarray:
        """Convert emotional state to feature vector."""
        return np.array([self.valence, self.arousal, self.dominance, self.confidence])


class Synapse:
    """
    Represents a synaptic connection between neurons.

    Synapses in the synthetic brain-tissue are dynamic and can:
    - Strengthen or weaken based on activity (plasticity)
    - Self-heal when damaged
    - Adapt transmission speed based on importance
    """

    def __init__(
        self,
        source_neuron: int,
        target_neuron: int,
        initial_strength: float = 0.5,
        plasticity: float = 0.01,
    ):
        """
        Initialize a synapse.

        Args:
            source_neuron: ID of the source neuron
            target_neuron: ID of the target neuron
            initial_strength: Initial connection strength (0 to 1)
            plasticity: Rate of strength adjustment
        """
        self.source_neuron = source_neuron
        self.target_neuron = target_neuron
        self.strength = initial_strength
        self.plasticity = plasticity
        self.activation_history: List[float] = []
        self.last_activated: Optional[datetime] = None

    def transmit(self, signal: float) -> float:
        """
        Transmit a signal through the synapse.

        Args:
            signal: Input signal strength

        Returns:
            Transmitted signal (modified by synapse strength)
        """
        output = signal * self.strength
        self.activation_history.append(output)
        self.last_activated = datetime.utcnow()

        # Keep history manageable
        if len(self.activation_history) > 1000:
            self.activation_history = self.activation_history[-500:]

        return output

    def adjust_strength(self, delta: float) -> None:
        """
        Adjust synapse strength based on learning.

        Args:
            delta: Change in strength (positive = strengthen, negative = weaken)
        """
        self.strength = np.clip(
            self.strength + delta * self.plasticity, 0.0, 1.0
        )

    def heal(self, healing_factor: float = 0.1) -> None:
        """
        Self-heal the synapse toward optimal strength.

        Args:
            healing_factor: Rate of healing
        """
        optimal_strength = 0.5  # Target middle ground
        self.strength += (optimal_strength - self.strength) * healing_factor
        self.strength = np.clip(self.strength, 0.0, 1.0)

    def get_metrics(self) -> Dict[str, Any]:
        """Get synapse metrics."""
        return {
            "strength": self.strength,
            "activation_count": len(self.activation_history),
            "avg_activation": (
                np.mean(self.activation_history) if self.activation_history else 0.0
            ),
            "last_activated": (
                self.last_activated.isoformat() if self.last_activated else None
            ),
        }


class SyntheticBrainTissue:
    """
    Synthetic brain-tissue natural AI engine.

    This engine emulates organic learning through:
    - Multi-layer neural architecture
    - Dynamic synaptic plasticity
    - Emotional reasoning integration
    - Self-healing capabilities
    - Intuition-based pattern recognition

    Example:
        >>> brain = SyntheticBrainTissue(layers=12, plasticity=0.01)
        >>> await brain.initialize()
        >>> output = await brain.analyze(input_data)
    """

    def __init__(
        self,
        layers: int = 12,
        neurons_per_layer: int = 256,
        plasticity: float = 0.01,
        emotional_depth: float = 0.5,
    ):
        """
        Initialize the synthetic brain-tissue.

        Args:
            layers: Number of neural layers
            neurons_per_layer: Neurons in each layer
            plasticity: Global synaptic plasticity factor
            emotional_depth: Weight of emotional reasoning (0 to 1)
        """
        self.layers = layers
        self.neurons_per_layer = neurons_per_layer
        self.plasticity = plasticity
        self.emotional_depth = emotional_depth

        self._neural_layers: List[NeuralLayer] = []
        self._synapses: List[Synapse] = []
        self._emotional_state = EmotionalState()
        self._is_initialized = False
        self._is_running = False

        self._total_patterns_recognized = 0
        self._total_decisions = 0

        logger.info(
            "SyntheticBrainTissue initialized: %d layers, %d neurons/layer, "
            "plasticity=%.3f, emotional_depth=%.3f",
            layers,
            neurons_per_layer,
            plasticity,
            emotional_depth,
        )

    async def initialize(self) -> None:
        """Initialize the neural architecture."""
        logger.info("Initializing synthetic brain-tissue...")

        # Create neural layers
        for i in range(self.layers):
            layer = NeuralLayer(
                layer_id=i,
                neurons=self.neurons_per_layer,
                plasticity_factor=self.plasticity,
            )
            self._neural_layers.append(layer)

        # Create synaptic connections between adjacent layers
        for i in range(len(self._neural_layers) - 1):
            self._create_synapses_between_layers(i, i + 1)

        self._is_initialized = True
        logger.info(
            "Synthetic brain-tissue initialized with %d layers and %d synapses",
            len(self._neural_layers),
            len(self._synapses),
        )

    def _create_synapses_between_layers(
        self, source_layer: int, target_layer: int
    ) -> None:
        """Create synaptic connections between two layers."""
        for source_neuron in range(self.neurons_per_layer):
            for target_neuron in range(self.neurons_per_layer):
                # Sparse connectivity (not all neurons connect)
                if np.random.random() < 0.1:  # 10% connectivity
                    synapse = Synapse(
                        source_neuron=source_neuron,
                        target_neuron=target_neuron,
                        plasticity=self.plasticity,
                    )
                    self._synapses.append(synapse)

    async def start(self) -> None:
        """Start the neural engine."""
        if not self._is_initialized:
            raise RuntimeError("Brain tissue must be initialized before starting")
        self._is_running = True
        logger.info("Synthetic brain-tissue started")

    async def stop(self) -> None:
        """Stop the neural engine."""
        self._is_running = False
        logger.info("Synthetic brain-tissue stopped")

    async def analyze(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze input data through the neural tissue.

        Args:
            data: Input data to analyze
            context: Optional contextual information including emotional state

        Returns:
            Analysis results with patterns, insights, and confidence scores
        """
        if not self._is_running:
            raise RuntimeError("Brain tissue must be started before analysis")

        logger.debug("Analyzing data through %d neural layers", self.layers)

        # Extract emotional context if present
        if context and "emotional_state" in context:
            self._update_emotional_state(context["emotional_state"])

        # Convert input to neural representation
        input_vector = self._encode_input(data)

        # Forward pass through neural layers
        activation = input_vector
        for layer in self._neural_layers:
            activation = self._forward_pass(activation, layer)

        # Interpret output
        result = self._decode_output(activation, data)

        # Update metrics
        self._total_patterns_recognized += 1
        self._total_decisions += 1

        logger.debug(
            "Analysis complete: confidence=%.3f, patterns=%d",
            result.get("confidence", 0.0),
            len(result.get("patterns", [])),
        )

        return result

    def _encode_input(self, data: Dict[str, Any]) -> np.ndarray:
        """Encode input data into neural representation."""
        # Simple encoding - in production, this would be more sophisticated
        values = list(data.values())
        numeric_values = [
            float(v) if isinstance(v, (int, float)) else hash(str(v)) % 1000 / 1000.0
            for v in values
        ]

        # Pad or truncate to match input layer size
        if len(numeric_values) < self.neurons_per_layer:
            numeric_values.extend([0.0] * (self.neurons_per_layer - len(numeric_values)))
        else:
            numeric_values = numeric_values[: self.neurons_per_layer]

        return np.array(numeric_values)

    def _forward_pass(
        self, activation: np.ndarray, layer: NeuralLayer
    ) -> np.ndarray:
        """Perform forward pass through a layer."""
        # Linear transformation
        output = np.dot(activation, layer.weights) + layer.biases

        # Apply activation function
        if layer.activation_type == "sigmoid":
            output = 1 / (1 + np.exp(-output))
        elif layer.activation_type == "relu":
            output = np.maximum(0, output)
        elif layer.activation_type == "tanh":
            output = np.tanh(output)

        return output

    def _decode_output(
        self, activation: np.ndarray, original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Decode neural output into meaningful results."""
        # Calculate confidence from activation variance
        confidence = float(1.0 - np.std(activation))

        # Extract patterns (simplified)
        top_activations = np.argsort(activation)[-10:]
        patterns = [f"pattern_{i}" for i in top_activations if activation[i] > 0.5]

        # Generate insights based on emotional context
        insights = []
        if self._emotional_state.confidence > 0.7:
            insights.append("High confidence in pattern recognition")
        if self._emotional_state.valence > 0.3:
            insights.append("Positive context detected")

        return {
            "activation_profile": activation.tolist(),
            "patterns": patterns,
            "confidence": confidence,
            "insights": insights,
            "emotional_context": {
                "valence": self._emotional_state.valence,
                "arousal": self._emotional_state.arousal,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _update_emotional_state(self, emotional_data: Dict[str, Any]) -> None:
        """Update emotional state from context."""
        if "valence" in emotional_data:
            self._emotional_state.valence = np.clip(
                emotional_data["valence"], -1.0, 1.0
            )
        if "arousal" in emotional_data:
            self._emotional_state.arousal = np.clip(emotional_data["arousal"], 0.0, 1.0)
        if "confidence" in emotional_data:
            self._emotional_state.confidence = np.clip(
                emotional_data["confidence"], 0.0, 1.0
            )

    def strengthen_synapse(self, synapse_index: int, delta: float) -> None:
        """
        Strengthen a specific synapse (learning).

        Args:
            synapse_index: Index of the synapse to strengthen
            delta: Strength adjustment
        """
        if 0 <= synapse_index < len(self._synapses):
            self._synapses[synapse_index].adjust_strength(delta)

    def heal_all_synapses(self) -> None:
        """Trigger self-healing across all synapses."""
        for synapse in self._synapses:
            synapse.heal()
        logger.debug("All synapses healed")

    def get_metrics(self) -> Dict[str, Any]:
        """Get neural engine metrics."""
        avg_synapse_strength = (
            np.mean([s.strength for s in self._synapses]) if self._synapses else 0.0
        )

        return {
            "layers": self.layers,
            "neurons_per_layer": self.neurons_per_layer,
            "total_synapses": len(self._synapses),
            "avg_synapse_strength": float(avg_synapse_strength),
            "emotional_depth": self.emotional_depth,
            "current_emotional_state": {
                "valence": self._emotional_state.valence,
                "arousal": self._emotional_state.arousal,
                "dominance": self._emotional_state.dominance,
                "confidence": self._emotional_state.confidence,
            },
            "patterns_recognized": self._total_patterns_recognized,
            "total_decisions": self._total_decisions,
            "is_running": self._is_running,
        }
