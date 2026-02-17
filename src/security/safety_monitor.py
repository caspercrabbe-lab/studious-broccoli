"""
Safety Monitor - Critical Hardware and Biological Safety Systems.

This module implements multi-layer safety mechanisms to prevent catastrophic
failures like thermal runaway, unauthorized process execution, and biological
harm to research subjects.

Implements:
- Process Execution Control (capability-based security)
- Thermal Monitoring with auto-throttling
- Power Regulation and current limiting
- Neural Safety Circuit Breakers
- Biometric Monitoring (EEG/neural activity)
- Fail-Safe Architecture with redundant shutdown
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
import time

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety alert levels."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ShutdownReason(Enum):
    """Reasons for emergency shutdown."""
    THERMAL_RUNAWAY = "thermal_runaway"
    POWER_SURGE = "power_surge"
    NEURAL_ANOMALY = "neural_anomaly"
    UNAUTHORIZED_PROCESS = "unauthorized_process"
    MANUAL_OVERRIDE = "manual_override"
    SYSTEM_FAILURE = "system_failure"


@dataclass
class ThermalThresholds:
    """Temperature thresholds for safety monitoring."""
    # Conservative thresholds to prevent any risk
    warning_threshold: float = 45.0  # °C - start monitoring closely
    throttling_threshold: float = 50.0  # °C - begin auto-throttling
    critical_threshold: float = 55.0  # °C - prepare emergency shutdown
    emergency_threshold: float = 60.0  # °C - IMMEDIATE shutdown
    max_allowed: float = 60.0  # °C - absolute maximum (never exceed)


@dataclass
class PowerThresholds:
    """Power and current thresholds."""
    normal_current_ma: float = 100.0  # mA - normal operating range
    warning_current_ma: float = 500.0  # mA - elevated current
    critical_current_ma: float = 1000.0  # mA - dangerous level
    max_current_ma: float = 2000.0  # mA - absolute maximum (2A)
    current_limit_ma: float = 1500.0  # mA - hardware current limit


@dataclass
class NeuralSafetyThresholds:
    """Neural activity safety thresholds."""
    normal_eeg_uv: float = 100.0  # μV - normal EEG amplitude
    seizure_threshold_uv: float = 500.0  # μV - potential seizure activity
    critical_threshold_uv: float = 1000.0  # μV - dangerous neural activity
    sampling_rate_hz: int = 256  # Hz - EEG sampling rate


@dataclass
class SafetyState:
    """Current state of the safety monitoring system."""
    is_active: bool = False
    is_emergency: bool = False
    current_temperature: float = 0.0
    current_current_ma: float = 0.0
    neural_activity_uv: float = 0.0
    safety_level: SafetyLevel = SafetyLevel.NORMAL
    last_shutdown: Optional[datetime] = None
    shutdown_count: int = 0
    total_violations: int = 0


@dataclass
class ProcessRestriction:
    """Definition of a restricted process."""
    name: str
    pattern: str
    risk_level: SafetyLevel
    allowed_with_safeguards: bool = False
    requires_authorization: bool = True


class SafetyMonitor:
    """
    Multi-layer safety monitoring system for NeuroACon devices.

    This class implements comprehensive safety mechanisms:
    1. Process Execution Control - restricts dangerous processes
    2. Thermal Monitoring - real-time temperature with auto-throttling
    3. Power Regulation - current limiting and surge protection
    4. Neural Safety - EEG monitoring and anomaly detection
    5. Fail-Safe Architecture - redundant emergency shutdown

    Example:
        >>> monitor = SafetyMonitor()
        >>> await monitor.initialize()
        >>> await monitor.start()
        >>> # Monitor runs continuously, auto-shutdown on violations
    """

    # Default restricted processes (CPU-intensive, dangerous)
    DEFAULT_RESTRICTED_PROCESSES = [
        ProcessRestriction("cpu-burn", "cpu.*burn", SafetyLevel.EMERGENCY, False, True),
        ProcessRestriction("stress-ng", "stress.*", SafetyLevel.CRITICAL, False, True),
        ProcessRestriction("prime95", "prime.*", SafetyLevel.CRITICAL, False, True),
        ProcessRestriction("folding@home", "fah.*", SafetyLevel.WARNING, True, True),
    ]

    def __init__(
        self,
        thermal_thresholds: Optional[ThermalThresholds] = None,
        power_thresholds: Optional[PowerThresholds] = None,
        neural_thresholds: Optional[NeuralSafetyThresholds] = None,
        monitoring_interval_ms: int = 100,  # 100ms = 10Hz monitoring
    ):
        """
        Initialize the safety monitor.

        Args:
            thermal_thresholds: Custom temperature thresholds
            power_thresholds: Custom power thresholds
            neural_thresholds: Custom neural safety thresholds
            monitoring_interval_ms: How often to check sensors (default 100ms)
        """
        self.thermal = thermal_thresholds or ThermalThresholds()
        self.power = power_thresholds or PowerThresholds()
        self.neural = neural_thresholds or NeuralSafetyThresholds()
        self.monitoring_interval_ms = monitoring_interval_ms

        self.state = SafetyState()
        self._restricted_processes = self.DEFAULT_RESTRICTED_PROCESSES.copy()
        self._is_initialized = False
        self._is_running = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Callbacks for emergency actions
        self._shutdown_callbacks: List[Callable] = []
        self._alert_callbacks: List[Callable[[SafetyLevel, str], None]] = []

        # Metrics
        self._temperature_readings: List[float] = []
        self._current_readings: List[float] = []
        self._neural_readings: List[float] = []
        self._process_violations: List[Dict[str, Any]] = []

        logger.info("SafetyMonitor initialized")
        logger.info(
            "Thermal thresholds: warning=%.1f°C, throttle=%.1f°C, "
            "critical=%.1f°C, emergency=%.1f°C",
            self.thermal.warning_threshold,
            self.thermal.throttling_threshold,
            self.thermal.critical_threshold,
            self.thermal.emergency_threshold,
        )

    async def initialize(self) -> None:
        """Initialize the safety monitoring system."""
        logger.info("Initializing SafetyMonitor...")

        # Validate thresholds are sensible
        self._validate_thresholds()

        self._is_initialized = True
        logger.info("SafetyMonitor initialized successfully")

    def _validate_thresholds(self) -> None:
        """Validate that all thresholds are within safe ranges."""
        # Thermal validation
        if self.thermal.emergency_threshold > self.thermal.max_allowed:
            raise ValueError(
                f"Emergency threshold ({self.thermal.emergency_threshold}) "
                f"exceeds max allowed ({self.thermal.max_allowed})"
            )

        # Power validation
        if self.power.current_limit_ma > self.power.max_current_ma:
            raise ValueError(
                f"Current limit ({self.power.current_limit_ma}mA) "
                f"exceeds max ({self.power.max_current_ma}mA)"
            )

        logger.info("All safety thresholds validated")

    async def start(self) -> None:
        """Start continuous safety monitoring."""
        if not self._is_initialized:
            raise RuntimeError("SafetyMonitor must be initialized before starting")

        if self._is_running:
            logger.warning("SafetyMonitor is already running")
            return

        logger.info("Starting SafetyMonitor...")
        self._is_running = True
        self.state.is_active = True
        self._stop_event.clear()

        # Start monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="SafetyMonitor"
        )
        self._monitoring_thread.start()

        logger.info("SafetyMonitor started - monitoring active")

    async def stop(self) -> None:
        """Stop safety monitoring."""
        logger.info("Stopping SafetyMonitor...")
        self._is_running = False
        self.state.is_active = False
        self._stop_event.set()

        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2.0)
            self._monitoring_thread = None

        logger.info("SafetyMonitor stopped")

    def _monitoring_loop(self) -> None:
        """Continuous monitoring loop (runs in separate thread)."""
        logger.info("Safety monitoring loop started")

        while not self._stop_event.is_set():
            try:
                self._check_all_sensors()

                if self.state.is_emergency:
                    # Already in emergency state, maintain shutdown
                    time.sleep(0.1)
                    continue

            except Exception as e:
                logger.error("Error in monitoring loop: %s", e)
                self._trigger_emergency_shutdown(ShutdownReason.SYSTEM_FAILURE)

            # Sleep for monitoring interval
            time.sleep(self.monitoring_interval_ms / 1000.0)

    def _check_all_sensors(self) -> None:
        """Check all safety sensors and take action if needed."""
        # Check thermal sensors
        self._check_thermal_safety()

        # Check power sensors
        self._check_power_safety()

        # Check neural sensors
        self._check_neural_safety()

        # Update overall safety level
        self._update_safety_level()

    def _check_thermal_safety(self) -> None:
        """Check thermal sensors and enforce temperature limits."""
        # In production, this would read from actual hardware sensors
        # For now, we simulate sensor reading
        temp = self._read_temperature_sensor()
        self.state.current_temperature = temp
        self._temperature_readings.append(temp)

        # Keep history manageable (last 1000 readings = ~100 seconds)
        if len(self._temperature_readings) > 1000:
            self._temperature_readings = self._temperature_readings[-500:]

        # Check thresholds
        if temp >= self.thermal.emergency_threshold:
            logger.critical(
                "EMERGENCY: Temperature %.1f°C exceeds emergency threshold %.1f°C",
                temp, self.thermal.emergency_threshold
            )
            self._trigger_emergency_shutdown(ShutdownReason.THERMAL_RUNAWAY)

        elif temp >= self.thermal.critical_threshold:
            logger.error(
                "CRITICAL: Temperature %.1f°C exceeds critical threshold %.1f°C",
                temp, self.thermal.critical_threshold
            )
            self._send_alert(SafetyLevel.CRITICAL, f"Temperature critical: {temp}°C")
            self._initiate_throttling()

        elif temp >= self.thermal.throttling_threshold:
            logger.warning(
                "WARNING: Temperature %.1f°C exceeds throttling threshold %.1f°C",
                temp, self.thermal.throttling_threshold
            )
            self._send_alert(SafetyLevel.WARNING, f"Temperature elevated: {temp}°C")
            self._initiate_throttling()

        elif temp >= self.thermal.warning_threshold:
            logger.info("Temperature monitoring: %.1f°C", temp)
            self._send_alert(SafetyLevel.WARNING, f"Temperature rising: {temp}°C")

    def _check_power_safety(self) -> None:
        """Check power sensors and enforce current limits."""
        # In production, read from actual current sensors
        current = self._read_current_sensor()
        self.state.current_current_ma = current
        self._current_readings.append(current)

        if len(self._current_readings) > 1000:
            self._current_readings = self._current_readings[-500:]

        if current >= self.power.max_current_ma:
            logger.critical(
                "EMERGENCY: Current %.1fmA exceeds maximum %.1fmA",
                current, self.power.max_current_ma
            )
            self._trigger_emergency_shutdown(ShutdownReason.POWER_SURGE)

        elif current >= self.power.critical_current_ma:
            logger.error(
                "CRITICAL: Current %.1fmA exceeds critical threshold %.1fmA",
                current, self.power.critical_current_ma
            )
            self._send_alert(SafetyLevel.CRITICAL, f"Current critical: {current}mA")
            self._limit_current()

    def _check_neural_safety(self) -> None:
        """Check neural activity sensors for anomalies."""
        # In production, read from EEG/neural interface
        neural_activity = self._read_neural_sensor()
        self.state.neural_activity_uv = neural_activity
        self._neural_readings.append(neural_activity)

        if len(self._neural_readings) > 1000:
            self._neural_readings = self._neural_readings[-500:]

        if neural_activity >= self.neural.critical_threshold_uv:
            logger.critical(
                "EMERGENCY: Neural activity %.1fμV exceeds critical threshold %.1fμV",
                neural_activity, self.neural.critical_threshold_uv
            )
            self._trigger_emergency_shutdown(ShutdownReason.NEURAL_ANOMALY)

        elif neural_activity >= self.neural.seizure_threshold_uv:
            logger.error(
                "CRITICAL: Neural activity %.1fμV indicates possible seizure",
                neural_activity
            )
            self._send_alert(
                SafetyLevel.CRITICAL,
                f"Neural anomaly detected: {neural_activity}μV"
            )
            self._disconnect_neural_interface()

    def _update_safety_level(self) -> None:
        """Update overall safety level based on all sensors."""
        if self.state.is_emergency:
            self.state.safety_level = SafetyLevel.EMERGENCY
            return

        # Determine highest alert level
        levels = [SafetyLevel.NORMAL]

        if self.state.current_temperature >= self.thermal.warning_threshold:
            levels.append(SafetyLevel.WARNING)
        if self.state.current_temperature >= self.thermal.critical_threshold:
            levels.append(SafetyLevel.CRITICAL)

        if self.state.current_current_ma >= self.power.warning_current_ma:
            levels.append(SafetyLevel.WARNING)
        if self.state.current_current_ma >= self.power.critical_current_ma:
            levels.append(SafetyLevel.CRITICAL)

        if self.state.neural_activity_uv >= self.neural.seizure_threshold_uv:
            levels.append(SafetyLevel.CRITICAL)

        # Take highest level
        level_order = [SafetyLevel.NORMAL, SafetyLevel.WARNING,
                       SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]
        self.state.safety_level = max(levels, key=lambda x: level_order.index(x))

    def _trigger_emergency_shutdown(self, reason: ShutdownReason) -> None:
        """Trigger immediate emergency shutdown."""
        if self.state.is_emergency:
            return  # Already in emergency state

        logger.critical("EMERGENCY SHUTDOWN TRIGGERED: %s", reason.value)
        self.state.is_emergency = True
        self.state.last_shutdown = datetime.utcnow()
        self.state.shutdown_count += 1
        self.state.safety_level = SafetyLevel.EMERGENCY

        # Execute all shutdown callbacks
        for callback in self._shutdown_callbacks:
            try:
                callback(reason)
            except Exception as e:
                logger.error("Error in shutdown callback: %s", e)

        # Send emergency alert
        self._send_alert(
            SafetyLevel.EMERGENCY,
            f"EMERGENCY SHUTDOWN: {reason.value}"
        )

        # In production: cut power, disconnect neural interfaces, etc.
        logger.critical("Emergency shutdown complete")

    def _initiate_throttling(self) -> None:
        """Initiate CPU throttling to reduce heat."""
        logger.info("Initiating CPU throttling")
        # In production: reduce CPU frequency, limit processes

    def _limit_current(self) -> None:
        """Limit current flow to safe levels."""
        logger.info("Limiting current to safe levels")
        # In production: engage current-limiting circuits

    def _disconnect_neural_interface(self) -> None:
        """Disconnect neural interface for safety."""
        logger.info("Disconnecting neural interface")
        # In production: open circuit breakers, isolate implants

    # Sensor reading methods (override in production for real hardware)
    def _read_temperature_sensor(self) -> float:
        """Read current temperature from sensor."""
        # Placeholder - in production, read from actual hardware
        return 0.0

    def _read_current_sensor(self) -> float:
        """Read current from power sensor."""
        # Placeholder
        return 0.0

    def _read_neural_sensor(self) -> float:
        """Read neural activity from EEG sensor."""
        # Placeholder
        return 0.0

    # Process execution control
    def check_process_authorization(self, process_name: str) -> bool:
        """
        Check if a process is authorized to run.

        Args:
            process_name: Name of the process to check

        Returns:
            True if process is authorized, False if restricted
        """
        import re

        for restriction in self._restricted_processes:
            if re.match(restriction.pattern, process_name, re.IGNORECASE):
                self.state.total_violations += 1
                self._process_violations.append({
                    "process": process_name,
                    "restriction": restriction.name,
                    "risk_level": restriction.risk_level.value,
                    "timestamp": datetime.utcnow().isoformat(),
                })

                if not restriction.allowed_with_safeguards:
                    logger.error(
                        "UNAUTHORIZED PROCESS BLOCKED: %s (risk: %s)",
                        process_name, restriction.risk_level.value
                    )
                    return False

                if restriction.requires_authorization:
                    logger.warning(
                        "Process %s requires explicit authorization",
                        process_name
                    )
                    return False  # Require explicit approval

        return True

    def add_restricted_process(self, restriction: ProcessRestriction) -> None:
        """Add a new process restriction."""
        self._restricted_processes.append(restriction)
        logger.info("Added process restriction: %s", restriction.name)

    # Callback registration
    def on_emergency_shutdown(self, callback: Callable[[ShutdownReason], None]) -> None:
        """Register callback for emergency shutdown events."""
        self._shutdown_callbacks.append(callback)
        logger.info("Registered emergency shutdown callback")

    def on_safety_alert(
        self, callback: Callable[[SafetyLevel, str], None]
    ) -> None:
        """Register callback for safety alerts."""
        self._alert_callbacks.append(callback)
        logger.info("Registered safety alert callback")

    def _send_alert(self, level: SafetyLevel, message: str) -> None:
        """Send safety alert to all registered callbacks."""
        for callback in self._alert_callbacks:
            try:
                callback(level, message)
            except Exception as e:
                logger.error("Error in alert callback: %s", e)

    # Metrics and state
    def get_state(self) -> SafetyState:
        """Get current safety system state."""
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive safety metrics."""
        return {
            "is_active": self.state.is_active,
            "is_emergency": self.state.is_emergency,
            "safety_level": self.state.safety_level.value,
            "current_temperature": self.state.current_temperature,
            "current_current_ma": self.state.current_current_ma,
            "neural_activity_uv": self.state.neural_activity_uv,
            "shutdown_count": self.state.shutdown_count,
            "total_violations": self.state.total_violations,
            "last_shutdown": (
                self.state.last_shutdown.isoformat()
                if self.state.last_shutdown else None
            ),
            "thermal_history_avg": (
                sum(self._temperature_readings) / len(self._temperature_readings)
                if self._temperature_readings else 0.0
            ),
            "process_violations_count": len(self._process_violations),
        }

    def get_violation_log(self) -> List[Dict[str, Any]]:
        """Get log of all process violations."""
        return self._process_violations.copy()
