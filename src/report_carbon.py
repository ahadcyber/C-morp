"""
Carbon Emissions Reporting Module - C-MORP
Track and report carbon emissions savings
Smart India Hackathon 2025
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CarbonMetrics:
    """Carbon emissions metrics"""
    timestamp: str
    grid_emissions: float  # kg CO2
    renewable_generation: float  # kWh
    carbon_saved: float  # kg CO2
    carbon_intensity: float  # kg CO2/kWh
    renewable_percentage: float


class CarbonReporter:
    """Calculate and report carbon emissions savings"""
    
    # Carbon intensity factors (kg CO2 per kWh)
    GRID_CARBON_INTENSITY = {
        'coal': 0.95,
        'natural_gas': 0.45,
        'mixed_grid': 0.71,  # India average
        'renewable': 0.05    # Lifecycle emissions
    }
    
    def __init__(self, grid_type: str = 'mixed_grid'):
        self.grid_type = grid_type
        self.base_intensity = self.GRID_CARBON_INTENSITY.get(grid_type, 0.71)
        self.metrics_history = []
    
    def calculate_emissions(
        self,
        grid_consumption: float,
        solar_generation: float,
        wind_generation: float,
        battery_discharge: float
    ) -> CarbonMetrics:
        """Calculate carbon emissions for current period"""
        
        # Total renewable generation
        renewable_generation = solar_generation + wind_generation + battery_discharge
        
        # Grid emissions (what would have been emitted)
        total_consumption = grid_consumption + renewable_generation
        grid_emissions = total_consumption * self.base_intensity
        
        # Actual emissions (only from grid consumption)
        actual_emissions = grid_consumption * self.base_intensity
        
        # Carbon saved by using renewables
        carbon_saved = grid_emissions - actual_emissions
        
        # Current carbon intensity
        if total_consumption > 0:
            carbon_intensity = actual_emissions / total_consumption
        else:
            carbon_intensity = 0
        
        # Renewable percentage
        if total_consumption > 0:
            renewable_percentage = (renewable_generation / total_consumption) * 100
        else:
            renewable_percentage = 0
        
        metrics = CarbonMetrics(
            timestamp=datetime.now().isoformat(),
            grid_emissions=grid_emissions,
            renewable_generation=renewable_generation,
            carbon_saved=carbon_saved,
            carbon_intensity=carbon_intensity,
            renewable_percentage=renewable_percentage
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def generate_daily_report(self) -> Dict:
        """Generate daily carbon report"""
        if not self.metrics_history:
            return {}
        
        # Get last 24 hours of data
        now = datetime.now()
        cutoff = now - timedelta(days=1)
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff
        ]
        
        if not recent_metrics:
            return {}
        
        total_carbon_saved = sum(m.carbon_saved for m in recent_metrics)
        avg_renewable_pct = np.mean([m.renewable_percentage for m in recent_metrics])
        total_renewable_gen = sum(m.renewable_generation for m in recent_metrics)
        
        # Convert to equivalent metrics
        trees_equivalent = total_carbon_saved / 21  # 1 tree absorbs ~21kg CO2/year
        cars_off_road = total_carbon_saved / 4600  # Average car emits 4.6 tons/year
        
        report = {
            'date': now.date().isoformat(),
            'total_carbon_saved_kg': round(total_carbon_saved, 2),
            'total_renewable_generation_kwh': round(total_renewable_gen, 2),
            'average_renewable_percentage': round(avg_renewable_pct, 2),
            'equivalents': {
                'trees_planted': round(trees_equivalent * 365, 2),
                'cars_off_road_days': round(cars_off_road * 365, 2),
                'homes_powered': round(total_renewable_gen / 30, 2)  # Avg home uses 30 kWh/day
            },
            'metrics': {
                'peak_renewable_percentage': round(max(m.renewable_percentage for m in recent_metrics), 2),
                'minimum_carbon_intensity': round(min(m.carbon_intensity for m in recent_metrics), 4),
                'total_data_points': len(recent_metrics)
            }
        }
        
        return report
    
    def generate_monthly_report(self) -> Dict:
        """Generate monthly carbon report with trends"""
        if not self.metrics_history:
            return {}
        
        now = datetime.now()
        cutoff = now - timedelta(days=30)
        
        monthly_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff
        ]
        
        if not monthly_metrics:
            return {}
        
        total_carbon_saved = sum(m.carbon_saved for m in monthly_metrics)
        total_renewable = sum(m.renewable_generation for m in monthly_metrics)
        avg_renewable_pct = np.mean([m.renewable_percentage for m in monthly_metrics])
        
        # Calculate weekly trends
        weekly_savings = []
        for week in range(4):
            week_start = now - timedelta(days=(4-week)*7)
            week_end = week_start + timedelta(days=7)
            
            week_metrics = [
                m for m in monthly_metrics
                if week_start <= datetime.fromisoformat(m.timestamp) < week_end
            ]
            
            if week_metrics:
                weekly_savings.append(sum(m.carbon_saved for m in week_metrics))
        
        report = {
            'period': f'{cutoff.date()} to {now.date()}',
            'total_carbon_saved_kg': round(total_carbon_saved, 2),
            'total_carbon_saved_tons': round(total_carbon_saved / 1000, 3),
            'total_renewable_generation_kwh': round(total_renewable, 2),
            'average_renewable_percentage': round(avg_renewable_pct, 2),
            'weekly_trend': [round(s, 2) for s in weekly_savings],
            'environmental_impact': {
                'trees_equivalent': round((total_carbon_saved / 21) * 12, 2),  # Annual equivalent
                'fuel_saved_liters': round(total_renewable / 10, 2),  # Rough estimate
                'coal_avoided_kg': round(total_carbon_saved / 0.95, 2)
            },
            'cost_savings_estimate': {
                'grid_cost_avoided': round(total_renewable * 8, 2),  # ₹8 per kWh average
                'carbon_credit_value': round(total_carbon_saved * 0.05, 2)  # ₹50 per ton
            }
        }
        
        return report
    
    def export_report(self, filename: str, report_type: str = 'daily'):
        """Export report to JSON file"""
        if report_type == 'daily':
            report = self.generate_daily_report()
        elif report_type == 'monthly':
            report = self.generate_monthly_report()
        else:
            raise ValueError("report_type must be 'daily' or 'monthly'")
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report exported to {filename}")


# Benchmark example
def run_carbon_benchmark():
    """Test carbon reporting system"""
    reporter = CarbonReporter(grid_type='mixed_grid')
    
    # Simulate 24 hours of data
    logger.info("Simulating 24 hours of energy data...")
    
    for hour in range(24):
        # Simulate varying renewable generation
        solar = max(0, 50 * np.sin(np.pi * hour / 12))  # Peak at noon
        wind = 30 + 20 * np.random.random()
        battery = 10 if 18 <= hour <= 22 else 0  # Discharge during peak hours
        grid = max(0, 100 - solar - wind - battery)
        
        metrics = reporter.calculate_emissions(
            grid_consumption=grid,
            solar_generation=solar,
            wind_generation=wind,
            battery_discharge=battery
        )
        
        if hour % 6 == 0:  # Log every 6 hours
            logger.info(f"Hour {hour}: Carbon saved: {metrics.carbon_saved:.2f} kg CO2, "
                       f"Renewable: {metrics.renewable_percentage:.1f}%")
    
    # Generate reports
    daily_report = reporter.generate_daily_report()
    logger.info(f"\n{'='*50}")
    logger.info("DAILY CARBON REPORT")
    logger.info(f"{'='*50}")
    logger.info(f"Total Carbon Saved: {daily_report['total_carbon_saved_kg']} kg CO2")
    logger.info(f"Renewable Generation: {daily_report['total_renewable_generation_kwh']} kWh")
    logger.info(f"Average Renewable %: {daily_report['average_renewable_percentage']}%")
    logger.info(f"Trees Equivalent: {daily_report['equivalents']['trees_planted']}")
    logger.info(f"{'='*50}\n")
    
    return daily_report


if __name__ == "__main__":
    run_carbon_benchmark()
