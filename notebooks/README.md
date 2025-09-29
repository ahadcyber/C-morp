# C-MORP Analysis Notebooks

This folder contains Jupyter notebooks for advanced analysis and edge case studies.

## Available Notebooks

### blackout_edge.ipynb
**Purpose**: Analysis of grid blackout scenarios and edge cases

**Features**:
- Blackout detection algorithms
- Emergency response protocols
- Battery discharge optimization during grid failures
- Historical blackout pattern analysis
- Predictive blackout risk modeling

**Usage**:
```bash
jupyter notebook blackout_edge.ipynb
```

**Key Analyses**:
1. **Grid Failure Detection**: Real-time monitoring for grid voltage drops
2. **Island Mode Transition**: Automatic switch to off-grid operation
3. **Load Prioritization**: Critical load identification during emergencies
4. **Battery Reserve Management**: Optimal SOC maintenance for emergencies
5. **Recovery Protocols**: Grid reconnection procedures

## Sample Output

The notebook generates:
- Blackout probability heatmaps
- Energy reserve duration charts
- Critical load coverage analysis
- Historical incident reports

## Requirements

```
jupyter>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=0.24.0
```

## Data Sources

- Historical grid data: `/data/grid_history.csv`
- Weather patterns: `/data/weather_data.csv`
- Load profiles: `/data/campus_loads.csv`

## Running Benchmarks

```python
# Inside the notebook
from benchmark_utils import run_blackout_simulation

results = run_blackout_simulation(
    duration_hours=24,
    battery_capacity=500,  # kWh
    critical_load=50  # kW
)

print(f"Blackout survival time: {results['survival_hours']} hours")
```

## Smart India Hackathon 2025

This notebook demonstrates:
- ✅ Advanced edge case handling
- ✅ Predictive analytics capabilities
- ✅ Real-world scenario testing
- ✅ Robust emergency response systems
