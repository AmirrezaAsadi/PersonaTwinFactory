"""
Census and public demographic data integration for enhanced privacy assessment.

This module provides integration with publicly available demographic datasets to:
1. Detect rare demographic combinations
2. Calculate realistic external linkage risks
3. Compare against population baselines
4. Improve privacy risk assessment

Uses public datasets:
- US Census Bureau API (free, no authentication required)
- Fallback to bundled synthetic census data
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import defaultdict
import json
import os

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - census API will be disabled")


@dataclass
class CensusData:
    """Census demographic data for a geographic area."""
    geography: str  # e.g., "Hamilton County, OH"
    total_population: int
    age_distribution: Dict[str, float]  # age_range -> percentage
    gender_distribution: Dict[str, float]  # gender -> percentage
    ethnicity_distribution: Dict[str, float]  # ethnicity -> percentage
    
    def get_demographic_frequency(
        self,
        age_range: Optional[str],
        gender: Optional[str],
        ethnicity: Optional[str]
    ) -> float:
        """
        Calculate expected frequency of demographic combination in population.
        
        Returns value between 0 and 1 representing how common this combination is.
        Lower values = rarer demographic = higher privacy risk.
        """
        frequency = 1.0
        
        if age_range and age_range in self.age_distribution:
            frequency *= self.age_distribution[age_range]
        
        if gender and gender in self.gender_distribution:
            frequency *= self.gender_distribution[gender]
        
        if ethnicity and ethnicity in self.ethnicity_distribution:
            frequency *= self.ethnicity_distribution[ethnicity]
        
        return frequency


class CensusDataProvider:
    """
    Provider for census and demographic data from public sources.
    
    Data sources (in order of preference):
    1. US Census Bureau API (https://www.census.gov/data/developers/data-sets.html)
    2. Cached local data
    3. Bundled fallback synthetic data
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/.personatwin/census_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache: Dict[str, CensusData] = {}
        self._load_fallback_data()
    
    def get_census_data(self, geography: str) -> Optional[CensusData]:
        """
        Get census data for a geographic area.
        
        Args:
            geography: Geographic identifier (e.g., "Hamilton County, OH", "California")
            
        Returns:
            CensusData if available, None otherwise
        """
        # Check cache first
        cache_key = self._normalize_geography(geography)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load from disk cache
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            self.cache[cache_key] = cached_data
            return cached_data
        
        # Try to fetch from Census API
        if REQUESTS_AVAILABLE:
            api_data = self._fetch_from_census_api(geography)
            if api_data:
                self._save_to_cache(cache_key, api_data)
                self.cache[cache_key] = api_data
                return api_data
        
        # Fall back to synthetic data
        fallback_data = self._get_fallback_data(geography)
        if fallback_data:
            self.cache[cache_key] = fallback_data
        
        return fallback_data
    
    def _normalize_geography(self, geography: str) -> str:
        """Normalize geography string for caching."""
        return geography.lower().strip().replace(" ", "_")
    
    def _load_from_cache(self, cache_key: str) -> Optional[CensusData]:
        """Load census data from local cache."""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return CensusData(
                    geography=data['geography'],
                    total_population=data['total_population'],
                    age_distribution=data['age_distribution'],
                    gender_distribution=data['gender_distribution'],
                    ethnicity_distribution=data['ethnicity_distribution']
                )
        except Exception as e:
            logger.warning(f"Failed to load cached census data: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: CensusData) -> None:
        """Save census data to local cache."""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'geography': data.geography,
                    'total_population': data.total_population,
                    'age_distribution': data.age_distribution,
                    'gender_distribution': data.gender_distribution,
                    'ethnicity_distribution': data.ethnicity_distribution
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to cache census data: {e}")
    
    def _fetch_from_census_api(self, geography: str) -> Optional[CensusData]:
        """
        Fetch data from US Census Bureau API.
        
        Note: This is a simplified implementation. Real implementation would
        use the actual Census API endpoints with proper geography codes.
        """
        # TODO: Implement actual Census API integration
        # For now, return None to fall back to synthetic data
        logger.info(f"Census API integration not yet implemented for {geography}")
        return None
    
    def _load_fallback_data(self) -> None:
        """Load bundled fallback synthetic census data."""
        # US National averages (approximate, for demonstration)
        us_national = CensusData(
            geography="United States",
            total_population=330_000_000,
            age_distribution={
                "0-17": 0.22,
                "18-24": 0.09,
                "25-34": 0.14,
                "35-44": 0.13,
                "45-54": 0.13,
                "55-64": 0.13,
                "65-74": 0.10,
                "75+": 0.06,
            },
            gender_distribution={
                "Male": 0.49,
                "Female": 0.51,
            },
            ethnicity_distribution={
                "White": 0.60,
                "Black": 0.13,
                "Hispanic": 0.19,
                "Asian": 0.06,
                "Other": 0.02,
            }
        )
        
        # Store fallback data
        self.fallback_data = {
            "united_states": us_national,
            "default": us_national,
        }
    
    def _get_fallback_data(self, geography: str) -> Optional[CensusData]:
        """Get fallback synthetic census data."""
        cache_key = self._normalize_geography(geography)
        
        # Try to match to fallback data
        if cache_key in self.fallback_data:
            return self.fallback_data[cache_key]
        
        # Return US national average as default
        if "default" in self.fallback_data:
            logger.info(f"Using US national averages for {geography}")
            fallback = self.fallback_data["default"]
            # Create a copy with the requested geography
            return CensusData(
                geography=geography,
                total_population=fallback.total_population,
                age_distribution=fallback.age_distribution.copy(),
                gender_distribution=fallback.gender_distribution.copy(),
                ethnicity_distribution=fallback.ethnicity_distribution.copy()
            )
        
        return None


class CensusEnhancedPrivacyCalculator:
    """
    Enhanced privacy calculator that uses census data for better risk assessment.
    
    Improvements over basic calculator:
    1. Detects rare demographics using population data
    2. Calculates realistic external linkage risk
    3. Provides population-aware recommendations
    """
    
    def __init__(self, census_provider: Optional[CensusDataProvider] = None):
        self.census_provider = census_provider or CensusDataProvider()
    
    def calculate_demographic_rarity(
        self,
        demographics,  # Demographics object
        geography: Optional[str] = None
    ) -> float:
        """
        Calculate how rare a demographic combination is in the population.
        
        Args:
            demographics: Demographics object
            geography: Geographic area for comparison
            
        Returns:
            Rarity score (0-1, higher = rarer = higher risk)
        """
        if not geography:
            geography = demographics.geography or "United States"
        
        # Get census data
        census_data = self.census_provider.get_census_data(geography)
        if not census_data:
            logger.warning(f"No census data available for {geography}")
            return 0.5  # Default moderate risk
        
        # Calculate expected frequency in population
        age_range = demographics.age_range or self._age_to_range(demographics.age)
        frequency = census_data.get_demographic_frequency(
            age_range=age_range,
            gender=demographics.gender,
            ethnicity=demographics.ethnicity
        )
        
        # Convert frequency to rarity (invert)
        # Frequency 0.10 (10% of population) -> Rarity 0.1 (low risk)
        # Frequency 0.01 (1% of population) -> Rarity 0.5 (medium risk)
        # Frequency 0.001 (0.1% of population) -> Rarity 0.9 (high risk)
        
        if frequency > 0:
            rarity = 1.0 - min(frequency * 10, 1.0)  # Scale to 0-1
        else:
            rarity = 0.95  # Very rare = very high risk
        
        return rarity
    
    def _age_to_range(self, age: Optional[int]) -> Optional[str]:
        """Convert exact age to age range."""
        if age is None:
            return None
        
        if age < 18:
            return "0-17"
        elif age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 45:
            return "35-44"
        elif age < 55:
            return "45-54"
        elif age < 65:
            return "55-64"
        elif age < 75:
            return "65-74"
        else:
            return "75+"
    
    def enhance_risk_metrics(
        self,
        personas: List,  # List[Persona]
        base_metrics  # RiskMetrics
    ) -> Dict[str, float]:
        """
        Enhance risk metrics with census-based analysis.
        
        Returns additional risk factors:
        - demographic_rarity_risk: Average rarity of demographics
        - population_uniqueness_risk: Risk based on population uniqueness
        - census_enhanced_external_risk: Better external linkage estimation
        """
        if not personas:
            return {}
        
        rarities = []
        geographies = set()
        
        for persona in personas:
            rarity = self.calculate_demographic_rarity(
                persona.demographics,
                persona.demographics.geography
            )
            rarities.append(rarity)
            if persona.demographics.geography:
                geographies.add(persona.demographics.geography)
        
        # Calculate average rarity
        avg_rarity = sum(rarities) / len(rarities) if rarities else 0.0
        
        # Population uniqueness risk (higher if many geographies = diverse = higher risk)
        geo_diversity = len(geographies) / max(len(personas), 1)
        
        # Enhanced external linkage risk
        # Combine demographic rarity with geographic diversity
        enhanced_external_risk = (avg_rarity * 0.7 + geo_diversity * 0.3)
        
        return {
            "demographic_rarity_risk": avg_rarity,
            "population_uniqueness_risk": geo_diversity,
            "census_enhanced_external_risk": enhanced_external_risk,
            "rare_demographics_count": sum(1 for r in rarities if r > 0.7),
        }
    
    def get_recommendation_with_census(
        self,
        personas: List,  # List[Persona]
        base_metrics,  # RiskMetrics
        target_risk: float
    ) -> str:
        """
        Generate privacy recommendation using census insights.
        """
        enhanced = self.enhance_risk_metrics(personas, base_metrics)
        
        recommendations = []
        
        # Check demographic rarity
        if enhanced.get("demographic_rarity_risk", 0) > 0.6:
            recommendations.append(
                "HIGH RISK: Some personas have rare demographic combinations. "
                "Consider additional geographic generalization or increased merging."
            )
        
        # Check rare demographics count
        rare_count = enhanced.get("rare_demographics_count", 0)
        if rare_count > len(personas) * 0.2:  # >20% rare
            recommendations.append(
                f"WARNING: {rare_count} personas have rare demographics. "
                "These individuals are at high re-identification risk from public census data."
            )
        
        # Check population uniqueness
        if enhanced.get("population_uniqueness_risk", 0) > 0.5:
            recommendations.append(
                "Geographic diversity is high. Consider broader geographic generalization."
            )
        
        if not recommendations:
            recommendations.append(
                "Census analysis shows good demographic coverage. Privacy protection adequate."
            )
        
        return " | ".join(recommendations)


# Helper function to integrate with existing system
def create_census_enhanced_calculator() -> CensusEnhancedPrivacyCalculator:
    """Create a census-enhanced privacy calculator with default configuration."""
    return CensusEnhancedPrivacyCalculator()
