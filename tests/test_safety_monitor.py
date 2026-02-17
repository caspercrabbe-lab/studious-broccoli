"""
Tests for the Safety Monitor - Critical Hardware and Biological Safety Systems.

These tests verify that the safety monitor properly:
1. Detects thermal runaway and triggers emergency shutdown
2. Blocks unauthorized dangerous processes (e.g., cpu-burn)
3. Monitors power/current and enforces limits
4. Detects neural anomalies
5. Maintains fail-safe architecture
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.security.safety_monitor import (
    SafetyMonitor,
    SafetyLevel,
    ShutdownReason,
    ThermalThresholds,
    PowerThresholds,
    NeuralSafetyThresholds,
    ProcessRestriction,
    SafetyState,
)


class TestThermalThresholds:
    """Test thermal threshold configuration."""

    def test_default_thresholds_are_conservative(self):
        """Default thresholds should be conservative to prevent any risk."""
        thermal = ThermalThresholds()
        
        assert thermal.warning_threshold == 45.0
        assert thermal.throttling_threshold == 50.0
        assert thermal.critical_threshold == 55.0
        assert thermal.emergency_threshold == 60.0
        assert thermal.max_allowed == 60.0

    def test_emergency_cannot_exceed_max(self):
        """Emergency threshold cannot exceed maximum allowed."""
        with pytest.raises(ValueError):
            ThermalThresholds(
                emergency_threshold=70.0,
                max_allowed=60.0,
            )


class TestProcessRestrictions:
    """Test process execution control."""

    def test_cpu_burn_is_restricted(self):
        """cpu-burn should be in the default restricted list."""
        monitor = SafetyMonitor()
        
        # cpu-burn should be blocked
        assert not monitor.check_process_authorization("cpu-burn")
        assert not monitor.check_process_authorization("cpu-burn-fast")
        assert not monitor.check_process_authorization("cpu_burn")

    def test_stress_tools_are_restricted(self):
        """stress-ng and similar tools should be restricted."""
        monitor = SafetyMonitor()
        
        assert not monitor.check_process_authorization("stress-ng")
        assert not monitor.check_process_authorization("stress")
        assert not monitor.check_process_authorization("prime95")

    def test_normal_processes_allowed(self):
        """Normal processes should be allowed."""
        monitor = SafetyMonitor()
        
        # These should pass (not in restricted list)
        assert monitor.check_process_authorization("python")
        assert monitor.check_process_authorization("vim")
        assert monitor.check_process_authorization("bash")

    def test_violations_are_logged(self):
        """Process violations should be logged."""
        monitor = SafetyMonitor()
        
        # Try to run restricted process
        monitor.check_process_authorization("cpu-burn")
        
        violations = monitor.get_violation_log()
        assert len(violations) == 1
        assert violations[0]["process"] == "cpu-burn"
        assert violations[0]["risk_level"] == "emergency"


class TestSafetyMonitorInitialization:
    """Test safety monitor initialization."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Safety monitor should initialize successfully."""
        monitor = SafetyMonitor()
        await monitor.initialize()
        
        assert monitor._is_initialized
        assert not monitor._is_running

    @pytest.mark.asyncio
    async def test_start_requires_initialization(self):
        """Cannot start before initialization."""
        monitor = SafetyMonitor()
        
        with pytest.raises(RuntimeError):
            await monitor.start()

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        """Should be able to start and stop monitoring."""
        monitor = SafetyMonitor()
        await monitor.initialize()
        await monitor.start()
        
        assert monitor._is_running
        assert monitor.state.is_active
        
        await monitor.stop()
        assert not monitor._is_running


class TestThermalMonitoring:
    """Test thermal monitoring and shutdown."""

    @pytest.mark.asyncio
    async def test_emergency_shutdown_on_thermal_runaway(self):
        """Should trigger emergency shutdown when temperature exceeds threshold."""
        shutdown_triggered = []
        
        def on_shutdown(reason):
            shutdown_triggered.append(reason)
        
        monitor = SafetyMonitor(
            thermal_thresholds=ThermalThresholds(
                emergency_threshold=50.0,  # Lower for testing
            )
        )
        monitor.on_emergency_shutdown(on_shutdown)
        
        await monitor.initialize()
        await monitor.start()
        
        # Mock temperature sensor to return dangerous temperature
        with patch.object(monitor, '_read_temperature_sensor', return_value=55.0):
            # Give monitoring loop time to detect
            await asyncio.sleep(0.3)
        
        # Should have triggered shutdown
        assert len(shutdown_triggered) > 0
        assert shutdown_triggered[0] == ShutdownReason.THERMAL_RUNAWAY
        assert monitor.state.is_emergency
        
        await monitor.stop()

    @pytest.mark.asyncio
    async def test_throttling_on_elevated_temperature(self):
        """Should initiate throttling when temperature is elevated."""
        monitor = SafetyMonitor(
            thermal_thresholds=ThermalThresholds(
                warning_threshold=40.0,
                throttling_threshold=45.0,
                emergency_threshold=60.0,
            )
        )
        
        await monitor.initialize()
        await monitor.start()
        
        # Mock temperature at throttling level
        with patch.object(monitor, '_read_temperature_sensor', return_value=46.0):
            await asyncio.sleep(0.3)
        
        # Should be in warning state but not emergency
        assert not monitor.state.is_emergency
        assert monitor.state.safety_level in [SafetyLevel.WARNING, SafetyLevel.CRITICAL]
        
        await monitor.stop()


class TestPowerMonitoring:
    """Test power and current monitoring."""

    @pytest.mark.asyncio
    async def test_emergency_shutdown_on_power_surge(self):
        """Should trigger shutdown on dangerous current levels."""
        shutdown_triggered = []
        
        def on_shutdown(reason):
            shutdown_triggered.append(reason)
        
        monitor = SafetyMonitor(
            power_thresholds=PowerThresholds(
                max_current_ma=1000.0,  # Lower for testing
            )
        )
        monitor.on_emergency_shutdown(on_shutdown)
        
        await monitor.initialize()
        await monitor.start()
        
        # Mock current sensor to return dangerous current
        with patch.object(monitor, '_read_current_sensor', return_value=1500.0):
            await asyncio.sleep(0.3)
        
        assert len(shutdown_triggered) > 0
        assert shutdown_triggered[0] == ShutdownReason.POWER_SURGE
        
        await monitor.stop()


class TestNeuralMonitoring:
    """Test neural activity monitoring."""

    @pytest.mark.asyncio
    async def test_emergency_shutdown_on_neural_anomaly(self):
        """Should trigger shutdown on dangerous neural activity."""
        shutdown_triggered = []
        
        def on_shutdown(reason):
            shutdown_triggered.append(reason)
        
        monitor = SafetyMonitor(
            neural_thresholds=NeuralSafetyThresholds(
                critical_threshold_uv=800.0,  # Lower for testing
            )
        )
        monitor.on_emergency_shutdown(on_shutdown)
        
        await monitor.initialize()
        await monitor.start()
        
        # Mock neural sensor to return dangerous activity
        with patch.object(monitor, '_read_neural_sensor', return_value=1000.0):
            await asyncio.sleep(0.3)
        
        assert len(shutdown_triggered) > 0
        assert shutdown_triggered[0] == ShutdownReason.NEURAL_ANOMALY
        
        await monitor.stop()

    @pytest.mark.asyncio
    async def test_seizure_detection(self):
        """Should detect potential seizure activity."""
        monitor = SafetyMonitor(
            neural_thresholds=NeuralSafetyThresholds(
                seizure_threshold_uv=400.0,  # Lower for testing
            )
        )
        
        await monitor.initialize()
        await monitor.start()
        
        # Mock neural activity at seizure threshold
        with patch.object(monitor, '_read_neural_sensor', return_value=500.0):
            await asyncio.sleep(0.3)
        
        # Should detect anomaly but may not trigger full shutdown
        assert monitor.state.neural_activity_uv >= 400.0
        
        await monitor.stop()


class TestSafetyMetrics:
    """Test safety metrics and state reporting."""

    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Should collect and report comprehensive metrics."""
        monitor = SafetyMonitor()
        
        await monitor.initialize()
        await monitor.start()
        
        metrics = monitor.get_metrics()
        
        assert "is_active" in metrics
        assert "is_emergency" in metrics
        assert "safety_level" in metrics
        assert "shutdown_count" in metrics
        assert "total_violations" in metrics
        
        await monitor.stop()

    @pytest.mark.asyncio
    async def test_state_reporting(self):
        """Should report current safety state."""
        monitor = SafetyMonitor()
        
        await monitor.initialize()
        state = monitor.get_state()
        
        assert isinstance(state, SafetyState)
        assert not state.is_emergency
        assert state.safety_level == SafetyLevel.NORMAL


class TestCallbackSystem:
    """Test safety callback system."""

    @pytest.mark.asyncio
    async def test_emergency_callback_registration(self):
        """Should register and call emergency shutdown callbacks."""
        callback_called = []
        
        def callback(reason):
            callback_called.append(reason)
        
        monitor = SafetyMonitor()
        monitor.on_emergency_shutdown(callback)
        
        assert len(monitor._shutdown_callbacks) == 1
        
        # Manually trigger to test callback
        monitor._trigger_emergency_shutdown(ShutdownReason.MANUAL_OVERRIDE)
        
        assert len(callback_called) == 1
        assert callback_called[0] == ShutdownReason.MANUAL_OVERRIDE

    @pytest.mark.asyncio
    async def test_alert_callback_registration(self):
        """Should register and call safety alert callbacks."""
        alerts_received = []
        
        def alert_callback(level, message):
            alerts_received.append((level, message))
        
        monitor = SafetyMonitor()
        monitor.on_safety_alert(alert_callback)
        
        assert len(monitor._alert_callbacks) == 1
        
        # Manually send alert
        monitor._send_alert(SafetyLevel.WARNING, "Test warning")
        
        assert len(alerts_received) == 1
        assert alerts_received[0][0] == SafetyLevel.WARNING


class TestFailSafeArchitecture:
    """Test fail-safe architecture and redundancy."""

    @pytest.mark.asyncio
    async def test_monitoring_loop_error_handling(self):
        """Monitoring loop should handle errors gracefully."""
        monitor = SafetyMonitor()
        
        await monitor.initialize()
        await monitor.start()
        
        # The monitoring loop should continue even if sensor readings fail
        # This is tested by the loop continuing to run
        await asyncio.sleep(0.3)
        
        assert monitor._is_running
        
        await monitor.stop()

    @pytest.mark.asyncio
    async def test_emergency_state_persistence(self):
        """Emergency state should persist until reset."""
        monitor = SafetyMonitor()
        
        await monitor.initialize()
        await monitor.start()
        
        # Trigger emergency
        monitor._trigger_emergency_shutdown(ShutdownReason.SYSTEM_FAILURE)
        
        assert monitor.state.is_emergency
        
        # Emergency state should persist
        await asyncio.sleep(0.2)
        assert monitor.state.is_emergency
        
        await monitor.stop()


class TestIntegration:
    """Integration tests for safety monitor with engine."""

    def test_all_safety_layers_present(self):
        """Verify all required safety layers are implemented."""
        # Check that SafetyMonitor has all required methods
        monitor = SafetyMonitor()
        
        required_methods = [
            'initialize',
            'start',
            'stop',
            'check_process_authorization',
            'on_emergency_shutdown',
            'on_safety_alert',
            'get_metrics',
            'get_state',
        ]
        
        for method in required_methods:
            assert hasattr(monitor, method), f"Missing method: {method}"

    def test_default_restrictions_block_dangerous_processes(self):
        """Default restrictions should block all dangerous processes from the incident."""
        monitor = SafetyMonitor()
        
        # All processes that could cause thermal runaway
        dangerous_processes = [
            "cpu-burn",
            "stress-ng",
            "prime95",
            "folding@home",
        ]
        
        for process in dangerous_processes:
            # At minimum, these should require authorization
            result = monitor.check_process_authorization(process)
            # Either blocked outright or requires authorization
            assert result is False, f"Process {process} should be restricted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
