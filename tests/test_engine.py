"""
Tests for the Excellence Engine.

Run with: pytest tests/test_engine.py -v
"""

import pytest
import asyncio
from src.core.engine import ExcellenceEngine, EngineConfig


class TestExcellenceEngine:
    """Tests for ExcellenceEngine class."""

    @pytest.fixture
    def engine_config(self):
        """Create a test configuration."""
        return EngineConfig(
            neural_layers=4,
            neurons_per_layer=64,
            synaptic_plasticity=0.01,
            emotional_depth=0.5,
            pq_algorithm="kyber768",
            key_rotation_hours=24,
            feedback_interval_seconds=60,
            optimization_threshold=0.05,
            max_connections=100,
            shared_learning_enabled=True,
        )

    @pytest.fixture
    async def initialized_engine(self, engine_config):
        """Create and initialize an engine for testing."""
        engine = ExcellenceEngine(config=engine_config)
        await engine.initialize()
        yield engine
        await engine.stop()

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine_config):
        """Test that engine initializes correctly."""
        engine = ExcellenceEngine(config=engine_config)
        await engine.initialize()

        assert engine._security_layer is not None
        assert engine._neural_engine is not None
        assert engine._excellence_system is not None
        assert engine._cognitive_fabric is not None

        await engine.stop()

    @pytest.mark.asyncio
    async def test_engine_start_stop(self, initialized_engine):
        """Test starting and stopping the engine."""
        engine = initialized_engine

        await engine.start()
        assert engine.state.is_running is True

        await engine.stop()
        assert engine.state.is_running is False

    @pytest.mark.asyncio
    async def test_process_decision(self, initialized_engine):
        """Test processing a decision through the engine."""
        engine = initialized_engine
        await engine.start()

        test_data = {
            "input_value": 42,
            "context": "test",
        }

        result = await engine.process_decision(test_data)

        assert "result" in result
        assert "processing_path" in result
        assert engine.state.decisions_made == 1

        await engine.stop()

    @pytest.mark.asyncio
    async def test_process_decision_without_start(self, initialized_engine):
        """Test that processing fails if engine not started."""
        engine = initialized_engine

        with pytest.raises(RuntimeError, match="Engine must be started"):
            await engine.process_decision({"test": "data"})

    @pytest.mark.asyncio
    async def test_get_state(self, initialized_engine):
        """Test getting engine state."""
        engine = initialized_engine
        state = engine.get_state()

        assert state.is_running is False
        assert state.decisions_made == 0
        assert state.excellence_score == 0.0

    @pytest.mark.asyncio
    async def test_get_metrics(self, initialized_engine):
        """Test getting comprehensive metrics."""
        engine = initialized_engine
        metrics = engine.get_metrics()

        assert "engine" in metrics
        assert "neural" in metrics
        assert "security" in metrics
        assert "excellence" in metrics
        assert "fabric" in metrics

        assert metrics["engine"]["is_running"] is False
        assert metrics["neural"]["layers"] == 4
        assert metrics["security"]["algorithm"] == "kyber768"


class TestEngineConfig:
    """Tests for EngineConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EngineConfig()

        assert config.neural_layers == 12
        assert config.synaptic_plasticity == 0.01
        assert config.emotional_depth == 0.5
        assert config.pq_algorithm == "kyber768"
        assert config.key_rotation_hours == 24

    def test_custom_config(self):
        """Test custom configuration."""
        config = EngineConfig(
            neural_layers=8,
            pq_algorithm="kyber1024",
            key_rotation_hours=12,
        )

        assert config.neural_layers == 8
        assert config.pq_algorithm == "kyber1024"
        assert config.key_rotation_hours == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
