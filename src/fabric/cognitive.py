"""
Cognitive Fabric.

Unified intelligence layer that connects data, processes, and experiences
across the enterprise. Enables shared learning while respecting security
and compliance boundaries.
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class FabricNode:
    """Represents a node in the cognitive fabric."""

    node_id: str
    node_type: str  # "data_source", "processor", "decision_point", "output"
    capabilities: List[str] = field(default_factory=list)
    connections: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class KnowledgeUnit:
    """Represents a unit of knowledge in the fabric."""

    unit_id: str
    content: Dict[str, Any]
    source_node: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_level: str = "internal"  # "public", "internal", "restricted", "confidential"
    tags: Set[str] = field(default_factory=set)
    confidence: float = 1.0


class CognitiveFabric:
    """
    Cognitive fabric for unified enterprise intelligence.

    The fabric:
    - Connects all components of the platform
    - Enables shared learning across boundaries
    - Respects security and compliance constraints
    - Scales horizontally and vertically

    Example:
        >>> fabric = CognitiveFabric()
        >>> await fabric.initialize()
        >>> result = await fabric.coordinate(data)
    """

    def __init__(
        self,
        max_connections: int = 1000,
        shared_learning_enabled: bool = True,
    ):
        """
        Initialize the cognitive fabric.

        Args:
            max_connections: Maximum number of node connections
            shared_learning_enabled: Enable cross-node learning
        """
        self.max_connections = max_connections
        self.shared_learning_enabled = shared_learning_enabled

        self._nodes: Dict[str, FabricNode] = {}
        self._knowledge_base: Dict[str, KnowledgeUnit] = {}
        self._is_initialized = False
        self._is_running = False

        self._total_coordinations = 0
        self._shared_learnings = 0
        self._connection_count = 0

        logger.info(
            "CognitiveFabric initialized: max_connections=%d, shared_learning=%s",
            max_connections,
            shared_learning_enabled,
        )

    async def initialize(self) -> None:
        """Initialize the cognitive fabric."""
        logger.info("Initializing cognitive fabric...")

        # Create default nodes for the platform architecture
        default_nodes = [
            FabricNode(
                node_id="neural_engine",
                node_type="processor",
                capabilities=["analyze", "learn", "pattern_recognition"],
            ),
            FabricNode(
                node_id="security_layer",
                node_type="processor",
                capabilities=["encrypt", "decrypt", "sign", "verify"],
            ),
            FabricNode(
                node_id="excellence_system",
                node_type="processor",
                capabilities=["optimize", "feedback", "measure"],
            ),
            FabricNode(
                node_id="api_gateway",
                node_type="output",
                capabilities=["rest", "graphql", "websocket"],
            ),
        ]

        for node in default_nodes:
            self._nodes[node.node_id] = node

        # Create default connections
        self._connect_nodes("neural_engine", "excellence_system")
        self._connect_nodes("excellence_system", "api_gateway")
        self._connect_nodes("security_layer", "neural_engine")
        self._connect_nodes("security_layer", "excellence_system")

        self._is_initialized = True
        logger.info(
            "Cognitive fabric initialized with %d nodes and %d connections",
            len(self._nodes),
            self._connection_count,
        )

    async def start(self) -> None:
        """Start the cognitive fabric."""
        if not self._is_initialized:
            raise RuntimeError("Fabric must be initialized before starting")

        self._is_running = True
        logger.info("Cognitive fabric started")

    async def stop(self) -> None:
        """Stop the cognitive fabric."""
        self._is_running = False
        logger.info("Cognitive fabric stopped")

    def _connect_nodes(self, source_id: str, target_id: str) -> bool:
        """
        Connect two nodes in the fabric.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            True if connection was successful
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            logger.warning("Cannot connect: node not found")
            return False

        if self._connection_count >= self.max_connections:
            logger.warning("Maximum connections reached")
            return False

        source = self._nodes[source_id]
        target = self._nodes[target_id]

        if target_id not in source.connections:
            source.connections.add(target_id)
            target.connections.add(source_id)
            self._connection_count += 1
            logger.debug("Connected %s <-> %s", source_id, target_id)

        return True

    def _disconnect_nodes(self, source_id: str, target_id: str) -> bool:
        """
        Disconnect two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            True if disconnection was successful
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            return False

        source = self._nodes[source_id]
        target = self._nodes[target_id]

        if target_id in source.connections:
            source.connections.remove(target_id)
            target.connections.remove(source_id)
            self._connection_count -= 1
            return True

        return False

    async def coordinate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate data through the cognitive fabric.

        This method routes data through appropriate nodes based on
        capabilities and connections.

        Args:
            data: Input data to coordinate

        Returns:
            Coordinated result
        """
        if not self._is_running:
            raise RuntimeError("Fabric must be started before coordination")

        logger.debug("Coordinating data through cognitive fabric")

        # Determine which nodes should process this data
        processing_path = self._determine_processing_path(data)

        # Route through each node in the path
        result = data.copy()
        for node_id in processing_path:
            node = self._nodes.get(node_id)
            if node and node.is_active:
                result = await self._process_through_node(node, result)

        self._total_coordinations += 1

        logger.debug(
            "Coordination complete: path=%s",
            " -> ".join(processing_path),
        )

        return {
            "result": result,
            "processing_path": processing_path,
            "nodes_used": len(processing_path),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _determine_processing_path(self, data: Dict[str, Any]) -> List[str]:
        """
        Determine the optimal processing path through the fabric.

        Args:
            data: Input data

        Returns:
            List of node IDs to process through
        """
        # Simple path determination (in production, use graph algorithms)
        path = []

        # Always start with security
        if "security_layer" in self._nodes:
            path.append("security_layer")

        # Add neural processing if data needs analysis
        if any(k in data for k in ["patterns", "analysis", "learn"]):
            if "neural_engine" in self._nodes:
                path.append("neural_engine")

        # Add excellence optimization
        if "optimize" in data or "excellence" in data:
            if "excellence_system" in self._nodes:
                path.append("excellence_system")

        # End at API gateway for output
        if "api_gateway" in self._nodes:
            path.append("api_gateway")

        return path

    async def _process_through_node(
        self, node: FabricNode, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process data through a specific node.

        Args:
            node: Node to process through
            data: Input data

        Returns:
            Processed data
        """
        logger.debug("Processing through node: %s (%s)", node.node_id, node.node_type)

        # Add node metadata to data
        result = data.copy()
        result["_processed_by"] = result.get("_processed_by", []) + [node.node_id]
        result["_processing_timestamp"] = datetime.utcnow().isoformat()

        # Simulate node-specific processing
        await asyncio.sleep(0.01)  # Simulate processing time

        return result

    async def share_knowledge(
        self,
        content: Dict[str, Any],
        source_node: str,
        access_level: str = "internal",
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Share knowledge across the fabric.

        Args:
            content: Knowledge content
            source_node: Originating node ID
            access_level: Access level for the knowledge
            tags: Optional tags for categorization

        Returns:
            Knowledge unit ID
        """
        if not self.shared_learning_enabled:
            logger.warning("Shared learning is disabled")
            return ""

        import secrets

        unit_id = secrets.token_hex(16)
        knowledge = KnowledgeUnit(
            unit_id=unit_id,
            content=content,
            source_node=source_node,
            access_level=access_level,
            tags=set(tags) if tags else set(),
        )

        self._knowledge_base[unit_id] = knowledge
        self._shared_learnings += 1

        logger.info(
            "Knowledge shared: id=%s, source=%s, access=%s",
            unit_id,
            source_node,
            access_level,
        )

        return unit_id

    async def query_knowledge(
        self,
        query: Dict[str, Any],
        access_level: str = "internal",
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base.

        Args:
            query: Query parameters
            access_level: Maximum access level to return

        Returns:
            List of matching knowledge units
        """
        results = []
        access_hierarchy = ["public", "internal", "restricted", "confidential"]
        max_access_index = access_hierarchy.index(access_level)

        for unit in self._knowledge_base.values():
            # Check access level
            unit_access_index = access_hierarchy.index(unit.access_level)
            if unit_access_index > max_access_index:
                continue

            # Simple query matching (in production, use proper search)
            matches = True
            if "tags" in query:
                if not query["tags"].intersection(unit.tags):
                    matches = False

            if "source_node" in query:
                if unit.source_node != query["source_node"]:
                    matches = False

            if matches:
                results.append(
                    {
                        "unit_id": unit.unit_id,
                        "content": unit.content,
                        "source_node": unit.source_node,
                        "confidence": unit.confidence,
                        "created_at": unit.created_at.isoformat(),
                    }
                )

        logger.debug("Knowledge query returned %d results", len(results))
        return results

    def add_node(self, node: FabricNode) -> bool:
        """
        Add a node to the fabric.

        Args:
            node: Node to add

        Returns:
            True if successful
        """
        if node.node_id in self._nodes:
            logger.warning("Node already exists: %s", node.node_id)
            return False

        self._nodes[node.node_id] = node
        logger.info("Added node: %s (%s)", node.node_id, node.node_type)
        return True

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the fabric.

        Args:
            node_id: ID of node to remove

        Returns:
            True if successful
        """
        if node_id not in self._nodes:
            return False

        # Disconnect from all connected nodes first
        node = self._nodes[node_id]
        for connected_id in list(node.connections):
            self._disconnect_nodes(node_id, connected_id)

        del self._nodes[node_id]
        logger.info("Removed node: %s", node_id)
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get cognitive fabric metrics."""
        return {
            "max_connections": self.max_connections,
            "shared_learning_enabled": self.shared_learning_enabled,
            "total_nodes": len(self._nodes),
            "active_nodes": sum(1 for n in self._nodes.values() if n.is_active),
            "connection_count": self._connection_count,
            "knowledge_units": len(self._knowledge_base),
            "total_coordinations": self._total_coordinations,
            "shared_learnings": self._shared_learnings,
            "nodes": {
                node_id: {
                    "type": node.node_type,
                    "capabilities": node.capabilities,
                    "connections": len(node.connections),
                    "is_active": node.is_active,
                }
                for node_id, node in self._nodes.items()
            },
            "is_running": self._is_running,
        }
