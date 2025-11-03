"""
Social network and relationship modeling for PersonaTwin.

This module handles:
1. Explicit connections from input data (family, co-defendants, colleagues)
2. Inferred connections from demographic/geographic patterns
3. Privacy-preserving network anonymization
4. External dataset integration for realistic social structures
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import logging
from collections import defaultdict
import random

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Types of relationships between people."""
    FAMILY = "family"
    FRIEND = "friend"
    COWORKER = "coworker"
    NEIGHBOR = "neighbor"
    CODEFENDANT = "co-defendant"  # Criminal justice
    CAREGIVER = "caregiver"  # Healthcare
    ROOMMATE = "roommate"
    CLASSMATE = "classmate"  # Education
    CASEWORKER_CLIENT = "caseworker_client"  # Social services
    SUPERVISOR_EMPLOYEE = "supervisor_employee"  # Employment
    INFERRED = "inferred"  # From patterns


class ConnectionStrength(Enum):
    """Strength of social connection."""
    WEAK = "weak"  # Acquaintance
    MODERATE = "moderate"  # Regular contact
    STRONG = "strong"  # Close relationship


@dataclass
class SocialConnection:
    """
    A connection between two people/personas.
    """
    person1_id: str
    person2_id: str
    connection_type: ConnectionType
    strength: ConnectionStrength
    context: Optional[str] = None  # e.g., "Met at work", "Family member"
    shared_events: List[str] = field(default_factory=list)  # Shared event IDs
    confidence: float = 1.0  # 0-1, lower for inferred connections
    
    def __post_init__(self):
        # Ensure consistent ordering for lookups
        if self.person1_id > self.person2_id:
            self.person1_id, self.person2_id = self.person2_id, self.person1_id
    
    def get_connection_key(self) -> Tuple[str, str]:
        """Get unique key for this connection."""
        return (self.person1_id, self.person2_id)


@dataclass
class SocialCircle:
    """
    A group of connected people (community, family, organization).
    """
    circle_id: str
    members: Set[str] = field(default_factory=set)
    circle_type: str = "community"  # community, family, workplace, etc.
    geographic_area: Optional[str] = None
    size: int = 0
    
    def __post_init__(self):
        self.size = len(self.members)


class SocialNetworkBuilder:
    """
    Builds social networks from people data with privacy protection.
    
    Can handle:
    - Explicit connections from input data
    - Inferred connections from patterns
    - External dataset integration
    """
    
    def __init__(
        self,
        min_connection_confidence: float = 0.6,
        preserve_strong_connections: bool = True,
        use_external_patterns: bool = True
    ):
        self.min_confidence = min_connection_confidence
        self.preserve_strong = preserve_strong_connections
        self.use_external = use_external_patterns
        self.connections: Dict[Tuple[str, str], SocialConnection] = {}
        self.circles: Dict[str, SocialCircle] = {}
    
    def extract_connections(
        self,
        people: List['Person']  # type: ignore
    ) -> List[SocialConnection]:
        """
        Extract explicit connections from people data.
        
        Looks for:
        - Shared events (co-defendants, same hospital admission)
        - Same household/family indicators
        - Explicit relationship fields
        """
        connections = []
        
        # Index people by various attributes for fast lookup
        by_geography = defaultdict(list)
        by_event_location = defaultdict(list)
        event_participants = defaultdict(list)
        
        for person in people:
            # Index by geography
            if person.demographics.geography:
                by_geography[person.demographics.geography].append(person)
            
            # Index by events
            for event in person.events:
                event_key = f"{event.event_type}_{event.date}_{event.location}"
                event_participants[event_key].append((person, event))
                
                if event.location:
                    by_event_location[event.location].append(person)
        
        # Find people who share events (likely connected)
        for event_key, participants in event_participants.items():
            if len(participants) >= 2:
                # People at same event are connected
                for i, (person1, event1) in enumerate(participants):
                    for person2, event2 in participants[i+1:]:
                        conn_type = self._infer_connection_type_from_event(
                            event1.event_type
                        )
                        
                        connection = SocialConnection(
                            person1_id=person1.person_id,
                            person2_id=person2.person_id,
                            connection_type=conn_type,
                            strength=ConnectionStrength.MODERATE,
                            context=f"Shared event: {event1.event_type}",
                            shared_events=[event1.event_id, event2.event_id],
                            confidence=0.9  # High confidence - explicit shared event
                        )
                        connections.append(connection)
        
        # Infer family/household connections from demographics
        if self.use_external:
            inferred = self._infer_demographic_connections(people)
            connections.extend(inferred)
        
        # Store connections
        for conn in connections:
            self.connections[conn.get_connection_key()] = conn
        
        logger.info(f"Extracted {len(connections)} connections from {len(people)} people")
        return connections
    
    def _infer_connection_type_from_event(self, event_type: str) -> ConnectionType:
        """Infer connection type based on shared event type."""
        event_type_lower = event_type.lower()
        
        if any(x in event_type_lower for x in ["arrest", "trial", "charge"]):
            return ConnectionType.CODEFENDANT
        elif any(x in event_type_lower for x in ["admission", "treatment", "visit"]):
            return ConnectionType.CAREGIVER
        elif any(x in event_type_lower for x in ["class", "assessment", "grade"]):
            return ConnectionType.CLASSMATE
        elif any(x in event_type_lower for x in ["hire", "promotion", "review"]):
            return ConnectionType.COWORKER
        else:
            return ConnectionType.INFERRED
    
    def _infer_demographic_connections(
        self,
        people: List['Person']  # type: ignore
    ) -> List[SocialConnection]:
        """
        Infer likely connections from demographic patterns.
        
        Uses realistic social network patterns:
        - Same age + same geography = likely friends
        - Similar age + same last name = likely family
        - Same small geographic area = likely neighbors
        """
        connections = []
        
        # Group by geography for neighbor inference
        by_geography = defaultdict(list)
        for person in people:
            if person.demographics.geography:
                by_geography[person.demographics.geography].append(person)
        
        # Infer neighbor connections in small areas
        for geo, geo_people in by_geography.items():
            if len(geo_people) >= 2 and len(geo_people) <= 100:  # Small community
                # In small areas, people likely know each other
                for i, person1 in enumerate(geo_people):
                    # Connect to a few neighbors (not everyone)
                    sample_size = min(3, len(geo_people) - i - 1)
                    if sample_size > 0:
                        neighbors = random.sample(
                            geo_people[i+1:],
                            sample_size
                        )
                        
                        for person2 in neighbors:
                            # Age similarity increases connection likelihood
                            age_diff = abs(
                                (person1.demographics.age or 40) -
                                (person2.demographics.age or 40)
                            )
                            
                            if age_diff <= 10:
                                strength = ConnectionStrength.MODERATE
                                confidence = 0.7
                            elif age_diff <= 20:
                                strength = ConnectionStrength.WEAK
                                confidence = 0.5
                            else:
                                strength = ConnectionStrength.WEAK
                                confidence = 0.3
                            
                            if confidence >= self.min_confidence:
                                connection = SocialConnection(
                                    person1_id=person1.person_id,
                                    person2_id=person2.person_id,
                                    connection_type=ConnectionType.NEIGHBOR,
                                    strength=strength,
                                    context=f"Inferred from geographic proximity",
                                    confidence=confidence
                                )
                                connections.append(connection)
        
        logger.info(f"Inferred {len(connections)} demographic-based connections")
        return connections
    
    def detect_social_circles(
        self,
        people: List['Person'],  # type: ignore
        connections: Optional[List[SocialConnection]] = None
    ) -> List[SocialCircle]:
        """
        Detect communities/circles using connection patterns.
        
        Uses graph clustering to find groups of highly connected people.
        """
        if connections is None:
            connections = list(self.connections.values())
        
        # Build adjacency lists
        graph = defaultdict(set)
        for conn in connections:
            if conn.confidence >= self.min_confidence:
                graph[conn.person1_id].add(conn.person2_id)
                graph[conn.person2_id].add(conn.person1_id)
        
        # Find connected components (simple approach)
        visited = set()
        circles = []
        
        for person_id in graph.keys():
            if person_id not in visited:
                # BFS to find all connected people
                circle_members = set()
                queue = [person_id]
                
                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        circle_members.add(current)
                        queue.extend(graph[current] - visited)
                
                if len(circle_members) >= 2:
                    circle = SocialCircle(
                        circle_id=f"circle_{len(circles)}",
                        members=circle_members,
                        circle_type="community"
                    )
                    circles.append(circle)
                    self.circles[circle.circle_id] = circle
        
        logger.info(f"Detected {len(circles)} social circles")
        return circles
    
    def anonymize_network(
        self,
        connections: List[SocialConnection],
        personas: List['Persona'],  # type: ignore
        preserve_structure: bool = True
    ) -> List[SocialConnection]:
        """
        Anonymize social network for privacy while preserving structure.
        
        Strategy:
        1. Map original person IDs to persona IDs
        2. Preserve strong connections (family, close friends)
        3. Generalize weak connections
        4. Add noise to connection counts
        """
        # Build person -> persona mapping
        person_to_persona = {}
        for persona in personas:
            # Assume persona has merged_person_ids tracking which people were merged
            if hasattr(persona, 'merged_person_ids'):
                for person_id in persona.merged_person_ids:
                    person_to_persona[person_id] = persona.persona_id
        
        # Map connections to personas
        anonymized = []
        connection_counts = defaultdict(int)
        
        for conn in connections:
            # Get persona IDs
            persona1 = person_to_persona.get(conn.person1_id)
            persona2 = person_to_persona.get(conn.person2_id)
            
            if persona1 is None or persona2 is None:
                continue
            
            # Skip self-connections (if both people merged into same persona)
            if persona1 == persona2:
                continue
            
            # Preserve strong connections, generalize weak ones
            if self.preserve_strong and conn.strength == ConnectionStrength.STRONG:
                # Keep strong connections as-is
                new_conn = SocialConnection(
                    person1_id=persona1,
                    person2_id=persona2,
                    connection_type=conn.connection_type,
                    strength=conn.strength,
                    context=conn.context,
                    confidence=conn.confidence
                )
                anonymized.append(new_conn)
            elif preserve_structure:
                # Generalize weak connections (reduce detail)
                new_conn = SocialConnection(
                    person1_id=persona1,
                    person2_id=persona2,
                    connection_type=ConnectionType.INFERRED,
                    strength=ConnectionStrength.WEAK,
                    context="Anonymized connection",
                    confidence=min(conn.confidence, 0.5)
                )
                anonymized.append(new_conn)
            
            connection_counts[persona1] += 1
            connection_counts[persona2] += 1
        
        # Add noise to connection counts for privacy
        for persona_id in connection_counts:
            noise = random.randint(-2, 2)
            connection_counts[persona_id] = max(0, connection_counts[persona_id] + noise)
        
        logger.info(f"Anonymized {len(anonymized)} connections for {len(personas)} personas")
        return anonymized
    
    def integrate_external_network_patterns(
        self,
        people: List['Person'],  # type: ignore
        pattern_source: str = "small_world"
    ) -> List[SocialConnection]:
        """
        Add realistic network structure using external patterns.
        
        Patterns:
        - "small_world": Most people have few connections, some hubs
        - "community": Strong clusters with weak inter-cluster links
        - "hierarchical": Tree-like structure (workplaces, schools)
        """
        connections = []
        
        if pattern_source == "small_world":
            connections = self._add_small_world_pattern(people)
        elif pattern_source == "community":
            connections = self._add_community_pattern(people)
        elif pattern_source == "hierarchical":
            connections = self._add_hierarchical_pattern(people)
        
        logger.info(f"Added {len(connections)} connections from {pattern_source} pattern")
        return connections
    
    def _add_small_world_pattern(
        self,
        people: List['Person']  # type: ignore
    ) -> List[SocialConnection]:
        """
        Add small-world network pattern.
        
        Characteristics:
        - Most people have 2-5 connections
        - Few people have 10+ connections (hubs)
        - High clustering (friends of friends are friends)
        """
        connections = []
        
        # Randomly assign connection counts (power-law distribution)
        for person in people:
            # Most people have few connections
            if random.random() < 0.8:
                num_connections = random.randint(2, 5)
            else:
                # Some people are hubs
                num_connections = random.randint(10, 20)
            
            # Connect to random others (simplified)
            potential_connections = [p for p in people if p.person_id != person.person_id]
            if len(potential_connections) >= num_connections:
                connected_to = random.sample(potential_connections, num_connections)
                
                for other in connected_to:
                    connection = SocialConnection(
                        person1_id=person.person_id,
                        person2_id=other.person_id,
                        connection_type=ConnectionType.FRIEND,
                        strength=ConnectionStrength.WEAK,
                        context="Small-world pattern",
                        confidence=0.5
                    )
                    connections.append(connection)
        
        return connections
    
    def _add_community_pattern(
        self,
        people: List['Person']  # type: ignore
    ) -> List[SocialConnection]:
        """Add community structure with strong intra-cluster connections."""
        connections = []
        
        # Group people by geography
        by_geo = defaultdict(list)
        for person in people:
            geo = person.demographics.geography or "unknown"
            by_geo[geo].append(person)
        
        # Create strong connections within each community
        for geo, community in by_geo.items():
            if len(community) >= 3:
                # Each person connects to 3-5 others in community
                for person in community:
                    num_connections = min(5, len(community) - 1)
                    others = [p for p in community if p.person_id != person.person_id]
                    connected_to = random.sample(others, min(num_connections, len(others)))
                    
                    for other in connected_to:
                        connection = SocialConnection(
                            person1_id=person.person_id,
                            person2_id=other.person_id,
                            connection_type=ConnectionType.NEIGHBOR,
                            strength=ConnectionStrength.MODERATE,
                            context=f"Community: {geo}",
                            confidence=0.7
                        )
                        connections.append(connection)
        
        return connections
    
    def _add_hierarchical_pattern(
        self,
        people: List['Person']  # type: ignore
    ) -> List[SocialConnection]:
        """Add hierarchical structure (e.g., workplace, school)."""
        connections = []
        
        # Group by age ranges (proxy for hierarchy levels)
        by_age = defaultdict(list)
        for person in people:
            age = person.demographics.age or 40
            age_group = (age // 10) * 10  # 20s, 30s, 40s, etc.
            by_age[age_group].append(person)
        
        # Create supervisor-employee type connections
        age_groups = sorted(by_age.keys())
        for i in range(len(age_groups) - 1):
            older_group = by_age[age_groups[i + 1]]
            younger_group = by_age[age_groups[i]]
            
            # Each older person supervises 2-5 younger people
            for supervisor in older_group[:len(older_group)//2]:
                num_reports = min(5, len(younger_group))
                reports = random.sample(younger_group, min(num_reports, len(younger_group)))
                
                for employee in reports:
                    connection = SocialConnection(
                        person1_id=supervisor.person_id,
                        person2_id=employee.person_id,
                        connection_type=ConnectionType.SUPERVISOR_EMPLOYEE,
                        strength=ConnectionStrength.MODERATE,
                        context="Hierarchical structure",
                        confidence=0.6
                    )
                    connections.append(connection)
        
        return connections


class SocialNetworkAnalyzer:
    """
    Analyze social network properties for research and privacy assessment.
    """
    
    def __init__(self):
        self.metrics = {}
    
    def calculate_network_metrics(
        self,
        connections: List[SocialConnection]
    ) -> Dict[str, float]:
        """
        Calculate network statistics.
        
        Returns:
        - average_degree: Average number of connections per person
        - clustering_coefficient: How clustered the network is
        - density: Proportion of possible connections that exist
        - largest_component_size: Size of largest connected group
        """
        # Build graph
        graph = defaultdict(set)
        all_nodes = set()
        
        for conn in connections:
            graph[conn.person1_id].add(conn.person2_id)
            graph[conn.person2_id].add(conn.person1_id)
            all_nodes.add(conn.person1_id)
            all_nodes.add(conn.person2_id)
        
        # Calculate metrics
        num_nodes = len(all_nodes)
        num_edges = len(connections)
        
        if num_nodes == 0:
            return {}
        
        # Average degree
        degrees = [len(graph[node]) for node in all_nodes]
        avg_degree = sum(degrees) / num_nodes if num_nodes > 0 else 0
        
        # Density
        max_edges = num_nodes * (num_nodes - 1) / 2
        density = num_edges / max_edges if max_edges > 0 else 0
        
        # Clustering coefficient (simplified)
        clustering = self._calculate_clustering_coefficient(graph)
        
        # Component sizes
        components = self._find_components(graph)
        largest_component = max(len(c) for c in components) if components else 0
        
        metrics = {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "average_degree": avg_degree,
            "density": density,
            "clustering_coefficient": clustering,
            "largest_component_size": largest_component,
            "num_components": len(components)
        }
        
        self.metrics = metrics
        return metrics
    
    def _calculate_clustering_coefficient(
        self,
        graph: Dict[str, Set[str]]
    ) -> float:
        """Calculate clustering coefficient (simplified version)."""
        coefficients = []
        
        for node, neighbors in graph.items():
            if len(neighbors) < 2:
                continue
            
            # Count triangles (connections between neighbors)
            possible_edges = len(neighbors) * (len(neighbors) - 1) / 2
            actual_edges = 0
            
            neighbor_list = list(neighbors)
            for i, n1 in enumerate(neighbor_list):
                for n2 in neighbor_list[i+1:]:
                    if n2 in graph[n1]:
                        actual_edges += 1
            
            coefficient = actual_edges / possible_edges if possible_edges > 0 else 0
            coefficients.append(coefficient)
        
        return sum(coefficients) / len(coefficients) if coefficients else 0
    
    def _find_components(
        self,
        graph: Dict[str, Set[str]]
    ) -> List[Set[str]]:
        """Find connected components."""
        visited = set()
        components = []
        
        for node in graph.keys():
            if node not in visited:
                component = set()
                queue = [node]
                
                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        queue.extend(graph[current] - visited)
                
                components.append(component)
        
        return components
    
    def assess_privacy_risk_from_network(
        self,
        connections: List[SocialConnection],
        personas: List['Persona']  # type: ignore
    ) -> Dict[str, float]:
        """
        Assess privacy risks from social network structure.
        
        Risks:
        - Unique network positions (bridges, hubs) can identify people
        - Small isolated groups are vulnerable
        - Dense connections increase re-identification risk
        """
        metrics = self.calculate_network_metrics(connections)
        
        # Build persona connection counts
        persona_degrees = defaultdict(int)
        for conn in connections:
            persona_degrees[conn.person1_id] += 1
            persona_degrees[conn.person2_id] += 1
        
        # Identify high-risk network positions
        if persona_degrees:
            avg_degree = sum(persona_degrees.values()) / len(persona_degrees)
            max_degree = max(persona_degrees.values())
            
            # Hubs (many connections) are identifiable
            hub_risk = max_degree / (avg_degree + 1)
            
            # Small isolated groups are vulnerable
            isolation_risk = 1.0 - (metrics.get("largest_component_size", 0) / len(personas))
        else:
            hub_risk = 0
            isolation_risk = 0
        
        risk_assessment = {
            "network_hub_risk": min(hub_risk, 1.0),
            "network_isolation_risk": isolation_risk,
            "network_density_risk": metrics.get("density", 0),
            "overall_network_risk": (hub_risk + isolation_risk + metrics.get("density", 0)) / 3
        }
        
        return risk_assessment


# Helper function for integration with main pipeline
def add_social_network(
    people: List['Person'],  # type: ignore
    personas: List['Persona'],  # type: ignore
    use_external_patterns: bool = True,
    preserve_connections: bool = True
) -> Tuple[List[SocialConnection], Dict[str, float]]:
    """
    Add social network to personas with privacy protection.
    
    Args:
        people: Original people data
        personas: Generated personas
        use_external_patterns: Use realistic network patterns
        preserve_connections: Preserve strong connections
        
    Returns:
        Tuple of (anonymized_connections, privacy_metrics)
    """
    # Build network
    builder = SocialNetworkBuilder(
        preserve_strong_connections=preserve_connections,
        use_external_patterns=use_external_patterns
    )
    
    # Extract explicit connections
    connections = builder.extract_connections(people)
    
    # Add realistic patterns if requested
    if use_external_patterns:
        pattern_connections = builder.integrate_external_network_patterns(
            people,
            pattern_source="small_world"
        )
        connections.extend(pattern_connections)
    
    # Anonymize for personas
    anonymized = builder.anonymize_network(connections, personas)
    
    # Assess privacy risks
    analyzer = SocialNetworkAnalyzer()
    network_risk = analyzer.assess_privacy_risk_from_network(anonymized, personas)
    
    logger.info(f"Social network: {len(anonymized)} connections, "
                f"risk: {network_risk.get('overall_network_risk', 0):.2%}")
    
    return anonymized, network_risk
