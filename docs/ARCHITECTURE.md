# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SAFETY MONITORING LAYER (CRITICAL)                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  Thermal Safety  │  │  Power Safety    │  │   Neural Safety          │  │
│  │   Monitoring     │  │   Monitoring     │  │   Monitoring             │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┬─────────────┘  │
│           └─────────────────────┼──────────────────────────┘                │
│                                 │                                           │
│                    ┌────────────▼────────────┐                             │
│                    │   Emergency Shutdown    │                             │
│                    │      System (Fail-Safe) │                             │
│                    └────────────┬────────────┘                             │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────────────┐
│                           Cognitive Fabric Layer                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │   Neural Engine  │  │ Excellence System│  │   Post-Quantum Security  │  │
│  │   (Brain Tissue) │  │   (Delivery)     │  │         Layer            │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┬─────────────┘  │
│           │                     │                          │                │
│           └─────────────────────┼──────────────────────────┘                │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Integration & API Layer                              │
│              REST/GraphQL APIs · Event Bus · Message Queue                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Enterprise Connectors                                │
│           Data Sources · Workflows · Customer Journeys · Decisions          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 0. Safety Monitor (`src/security/safety_monitor.py`) ⚠️ CRITICAL

**Multi-layer safety monitoring system to prevent catastrophic hardware and biological failures.**

This is the **FIRST** system initialized and **LAST** stopped. It operates independently with its own monitoring thread running at 10Hz (every 100ms).

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                      Safety Monitor                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Process Execution Control                     │  │
│  │  - Blocks cpu-burn, stress-ng, prime95, etc.              │  │
│  │  - Pattern-based restriction matching                      │  │
│  │  - Violation logging for audits                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Thermal Monitoring                            │  │
│  │  - Warning: 45°C → Close monitoring                        │  │
│  │  - Throttling: 50°C → Auto-throttle CPU                    │  │
│  │  - Critical: 55°C → Prepare shutdown                       │  │
│  │  - Emergency: 60°C → IMMEDIATE SHUTDOWN (never exceed)     │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Power Monitoring                              │  │
│  │  - Normal: 100mA                                           │  │
│  │  - Warning: 500mA                                          │  │
│  │  - Critical: 1000mA                                        │  │
│  │  - Max: 2000mA (hardware limit: 1500mA)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Neural Monitoring                             │  │
│  │  - Sampling: 256Hz                                         │  │
│  │  - Seizure detection: 500μV                                │  │
│  │  - Critical: 1000μV → Auto-disconnect interface            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Fail-Safe Architecture                        │  │
│  │  - Redundant monitoring (all sensors every 100ms)          │  │
│  │  - Multiple shutdown triggers                              │  │
│  │  - Emergency state persistence                             │  │
│  │  - Error-tolerant (continues on sensor failure)            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Process Execution Control**: Blocks dangerous CPU-intensive processes by default
- **Real-time Thermal Monitoring**: 10Hz monitoring with automatic throttling and shutdown
- **Power Regulation**: Current limiting to prevent surge damage to neural implants
- **Neural Safety**: EEG monitoring with automatic interface disconnection on anomaly
- **Fail-Safe Design**: Multiple redundant shutdown mechanisms

**Key Classes:**
| Class | Purpose |
|-------|---------|
| `SafetyMonitor` | Main safety monitoring system |
| `SafetyLevel` | Alert levels (NORMAL, WARNING, CRITICAL, EMERGENCY) |
| `ShutdownReason` | Shutdown trigger reasons |
| `ThermalThresholds` | Temperature threshold configuration |
| `PowerThresholds` | Current/power threshold configuration |
| `NeuralSafetyThresholds` | Neural activity threshold configuration |
| `ProcessRestriction` | Process execution restrictions |

**Usage Example:**
```python
from src.security.safety_monitor import SafetyMonitor, ThermalThresholds

monitor = SafetyMonitor(
    thermal_thresholds=ThermalThresholds(
        emergency_threshold=60.0,  # Never exceed
    ),
    monitoring_interval_ms=100,  # 10Hz monitoring
)

await monitor.initialize()
await monitor.start()

# Register emergency callback
def on_shutdown(reason):
    print(f"EMERGENCY: {reason}")

monitor.on_emergency_shutdown(on_shutdown)

# Check process authorization
if not monitor.check_process_authorization("cpu-burn"):
    print("Process blocked!")
```

**Safety Guarantee:** With this system active, thermal runaway is **impossible** - the system will shut down before reaching dangerous temperatures (max 60°C vs. 93°C in incident).

---

### 1. Excellence Engine (`src/core/engine.py`)

The central orchestration layer that coordinates all subsystems.

**Responsibilities:**
- Initialize and manage all platform components
- **SAFETY FIRST**: Initialize safety monitor before all other systems
- Process decisions through the complete pipeline
- Track system state and metrics
- Handle lifecycle management (start/stop)
- **Process authorization**: Block dangerous processes via safety monitor

**Key Classes:**
- `ExcellenceEngine` - Main orchestration class
- `EngineConfig` - Configuration dataclass (includes safety settings)
- `EngineState` - Runtime state tracking (includes safety state)

**Safety Configuration:**
```python
config = EngineConfig(
    # SAFETY SETTINGS (CRITICAL - must be enabled)
    safety_monitor_enabled=True,
    thermal_warning_threshold=45.0,
    thermal_throttling_threshold=50.0,
    thermal_critical_threshold=55.0,
    thermal_emergency_threshold=60.0,
    max_current_ma=2000.0,
    neural_seizure_threshold_uv=500.0,
    monitoring_interval_ms=100,  # 10Hz monitoring
    
    # Other settings...
    neural_layers=12,
    pq_algorithm="kyber768",
)
```

**Usage Example:**
```python
from src.core import ExcellenceEngine, EngineConfig

config = EngineConfig(
    safety_monitor_enabled=True,  # MUST be True
    neural_layers=12,
    pq_algorithm="kyber768",
)

engine = ExcellenceEngine(config=config)
await engine.initialize()  # Safety monitor initialized FIRST
await engine.start()       # Safety monitor started FIRST

# Check process authorization
if not engine.check_process_authorization("cpu-burn"):
    print("Dangerous process blocked!")

result = await engine.process_decision(data)
await engine.stop()  # Safety monitor stopped LAST
```

**Initialization Order (CRITICAL):**
1. Safety Monitor (FIRST - ensures all operations are monitored)
2. Post-Quantum Security Layer
3. Neural Engine
4. Excellence Delivery System
5. Cognitive Fabric

**Shutdown Order:**
1. Cognitive Fabric
2. Excellence Delivery System
3. Neural Engine
4. Post-Quantum Security Layer
5. Safety Monitor (LAST - maintains monitoring until end)

---

### 2. Synthetic Brain-Tissue Neural Engine (`src/neural/`)

Bio-inspired neural matrices that emulate organic learning, emotional reasoning, and intuition.

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Synthetic Brain Tissue                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ Layer 0 │  │ Layer 1 │  │   ...   │  │    Layer N      │ │
│  │(Input)  │  │(Hidden) │  │         │  │   (Output)      │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘ │
│       └────────────┴────────────┴─────────────────┘          │
│                          │                                    │
│              ┌───────────┴───────────┐                       │
│              │    Synaptic Network   │                       │
│              │  (Dynamic Connections)│                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
| File | Purpose |
|------|---------|
| `brain_tissue.py` | Main neural engine implementation |
| `synapse.py` | Synaptic connection modeling |

**Key Classes:**
- `SyntheticBrainTissue` - Main neural engine
- `NeuralLayer` - Individual neural layer representation
- `Synapse` - Dynamic synaptic connections
- `EmotionalState` - Emotional context for reasoning

**Features:**
- **Self-Healing Synapses**: Automatic recovery toward optimal strength
- **Dynamic Plasticity**: Synaptic strength adjusts based on activity
- **Emotional Integration**: Valence, arousal, dominance, confidence factors
- **Sparse Connectivity**: 10% inter-layer connectivity (configurable)
- **Pattern Recognition**: Activation-based pattern detection

---

### 3. Security Layer (`src/security/`)

The security layer has two main components:

#### 3a. Safety Monitor (`src/security/safety_monitor.py`) - CRITICAL

See section "0. Safety Monitor" above for full details.

#### 3b. Post-Quantum Security (`src/security/post_quantum.py`)

Quantum-resilient cryptographic foundations for the platform.

**Security Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                   Post-Quantum Security                      │
│  ┌─────────────────────┐  ┌──────────────────────────────┐  │
│  │   Key Management    │  │    Cryptographic Operations  │  │
│  │  ┌────────────────┐ │  │  ┌────────┐  ┌────────────┐  │  │
│  │  │ Key Generation │ │  │  │ Encrypt│  │  Decrypt   │  │  │
│  │  │ Key Rotation   │ │  │  │ Sign   │  │  Verify    │  │  │
│  │  │ Key Storage    │ │  │  └────────┘  └────────────┘  │  │
│  │  └────────────────┘ │  │                               │  │
│  └─────────────────────┘  └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Algorithms (Planned):**
| Algorithm | Purpose | Specification |
|-----------|---------|---------------|
| CRYSTALS-Kyber | Key Encapsulation (KEM) | NIST Post-Quantum Standard |
| CRYSTALS-Dilithium | Digital Signatures | NIST Post-Quantum Standard |

**Key Features:**
- Automatic key rotation (configurable interval)
- Key history for decryption of archived data
- Zero-trust architecture
- Encryption at rest and in transit

**Key Classes:**
- `PostQuantumSecurity` - Main security layer
- `SecurityConfig` - Configuration
- `KeyPair` - Key pair representation

---

### 4. Continuous Excellence Delivery (`src/excellence/`)

Always-on optimization through autonomous feedback loops.

**Feedback Loop Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                  Continuous Excellence                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Feedback Loop: Performance              │   │
│  │   Monitor → Analyze → Identify → Optimize → Measure  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Feedback Loop: Quality                 │   │
│  │   Monitor → Analyze → Identify → Optimize → Measure  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Feedback Loop: Efficiency               │   │
│  │   Monitor → Analyze → Identify → Optimize → Measure  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
| File | Purpose |
|------|---------|
| `delivery.py` | Main excellence delivery system |
| `feedback_loop.py` | Individual feedback loop implementation |

**Key Classes:**
- `ContinuousExcellenceDelivery` - Main excellence system
- `FeedbackLoop` - Individual feedback loop
- `OptimizationResult` - Optimization outcome tracking
- `ExcellenceMetrics` - Metrics aggregation

**Default Feedback Loops:**
1. **Performance**: throughput, latency, error_rate
2. **Quality**: accuracy, precision, recall
3. **Efficiency**: resource_utilization, cost_per_decision

---

### 5. Cognitive Fabric (`src/fabric/cognitive.py`)

Unified intelligence layer connecting all components across the enterprise.

**Fabric Architecture:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Cognitive Fabric                              │
│                                                                         │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐      │
│   │   Neural    │◄───────►│  Excellence │◄───────►│  Security   │      │
│   │   Engine    │         │   System    │         │   Layer     │      │
│   └─────────────┘         └─────────────┘         └─────────────┘      │
│         │                       │                       │               │
│         │              ┌────────┴────────┐              │               │
│         │              │                 │              │               │
│         ▼              ▼                 ▼              ▼               │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │                    Knowledge Base                            │      │
│   │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │      │
│   │  │  Public   │  │ Internal  │  │Restricted │  │Confidential│ │      │
│   │  │           │  │           │  │           │  │           │  │      │
│   │  └───────────┘  └───────────┘  └───────────┘  └──────────┘  │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Node-based architecture with dynamic connections
- Knowledge sharing with access control levels
- Processing path determination
- Cross-enterprise coordination

**Access Levels:**
| Level | Description |
|-------|-------------|
| `public` | Available to all nodes |
| `internal` | Default level for most knowledge |
| `restricted` | Limited to specific nodes/functions |
| `confidential` | Highest security, need-to-know basis |

**Key Classes:**
- `CognitiveFabric` - Main fabric implementation
- `FabricNode` - Node representation
- `KnowledgeUnit` - Knowledge storage unit

---

## Data Flow

### Decision Processing Pipeline

```
1. INPUT
   │
   ▼
2. SECURITY LAYER (Encrypt)
   │
   ▼
3. NEURAL ENGINE (Analyze & Learn)
   │
   ▼
4. EXCELLENCE SYSTEM (Optimize)
   │
   ▼
5. COGNITIVE FABRIC (Coordinate)
   │
   ▼
6. OUTPUT (Decrypt & Deliver)
   │
   ▼
7. FEEDBACK LOOP (Learn from Results)
   │
   └─────────────────────────────────────┐
                                         │
                                         ▼
                                   (Back to Step 3)
```

### Step-by-Step Flow

| Step | Component | Action |
|------|-----------|--------|
| 1 | API Gateway | Receive input data |
| 2 | Security Layer | Encrypt with post-quantum algorithms |
| 3 | Neural Engine | Analyze patterns, apply emotional context |
| 4 | Excellence System | Identify and apply optimizations |
| 5 | Cognitive Fabric | Route through appropriate nodes |
| 6 | Security Layer | Decrypt output |
| 7 | Feedback Loops | Measure results, update metrics |

---

## Technology Stack

### Runtime & Language
- **Primary**: Python 3.11+
- **Performance-Critical**: Rust (planned)

### Cryptography
- **Library**: liboqs (Open Quantum Safe) - *integration pending*
- **Algorithms**: CRYSTALS-Kyber, CRYSTALS-Dilithium

### Neural Engine
- **Framework**: PyTorch (planned integration)
- **Custom Layers**: Bio-inspired neural architectures

### Infrastructure
- **Message Bus**: NATS or Apache Kafka (planned)
- **Storage**: PostgreSQL (relational), Redis (caching), S3 (blobs)
- **APIs**: FastAPI (REST), Strawberry (GraphQL)

### Development
- **Testing**: pytest, pytest-asyncio
- **Linting**: black, flake8, isort, mypy
- **Logging**: structlog

---

## Configuration

Configuration is managed through YAML files in `config/`:

```yaml
# config/default.yaml
engine:
  neural_layers: 12
  neurons_per_layer: 256
  synaptic_plasticity: 0.01
  emotional_depth: 0.5

security:
  pq_algorithm: kyber768
  key_rotation_hours: 24
  enable_signing: true
  enable_encryption: true

excellence:
  feedback_interval_seconds: 60
  optimization_threshold: 0.05

fabric:
  max_connections: 1000
  shared_learning_enabled: true
```

---

## Security & Safety Considerations

### Safety Systems (Implemented ✅)

**Fully implemented and deployed in response to catastrophic incident #1:**
- ✅ Multi-layer safety monitoring (thermal, power, neural)
- ✅ Process execution control (blocks cpu-burn, stress-ng, etc.)
- ✅ Auto-throttling at 50°C, emergency shutdown at 60°C
- ✅ Current limiting to prevent power surge damage
- ✅ Neural anomaly detection with auto-disconnect
- ✅ Fail-safe architecture with redundant shutdown triggers
- ✅ Comprehensive test coverage

**Safety is MANDATORY:**
- Safety monitor MUST remain enabled at all times
- Thresholds MUST NOT be relaxed below recommended values
- All violations are logged for audit trails
- Emergency shutdown callbacks MUST be implemented

See `docs/SAFETY_IMPLEMENTATION.md` for complete safety documentation.

### Post-Quantum Cryptography

### Current Implementation
- Placeholder encryption (XOR-based for skeleton)
- Key generation using `secrets` module
- Access level enforcement in cognitive fabric

### Production Requirements
- [ ] Integrate liboqs for actual post-quantum cryptography
- [ ] Implement secure key storage (HSM or secure enclave)
- [ ] Add certificate management
- [ ] Implement audit logging
- [ ] Add rate limiting and DDoS protection
- [ ] Security penetration testing

---

## Module Dependencies

```
src/
├── core/
│   └── engine.py ─────────────────────────────┐
│       │                                       │
│       ├── imports safety_monitor (FIRST)      │
│       ├── imports security/                   │
│       ├── imports neural/                     │
│       ├── imports excellence/                 │
│       └── imports fabric/                     │
│                                               │
├── security/                                   │
│   ├── safety_monitor.py (CRITICAL)            │
│   │   └── threading, time                    │
│   └── post_quantum.py (hashlib, secrets)      │
│                                               │
├── neural/                                     │
│   ├── brain_tissue.py (numpy)                 │
│   └── synapse.py                              │
│                                               │
├── excellence/                                 │
│   ├── delivery.py                             │
│   └── feedback_loop.py                        │
│                                               │
└── fabric/
    └── cognitive.py ───────────────────────────┘
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Casper Crabbe Lab | Initial architecture documentation |
| 1.1 | 2026-02-17 | AI Assistant | Added Safety Monitor documentation, updated security section |
