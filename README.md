# Disease Spread Simulation App

## Authors
- Michał Pędrak 
- Andrzej Wacławik

## Requirements
```bash
pip install pygame pandas matplotlib
```

## Running simulation

Run the main simulation script:
```bash
python simulator.py
```
* **Configuration:** adjust initial parameters in the GUI start screen, then click **Start Simulation**.
* **Controls:** press `Space` to pause or resume, click on any agent to inspect its properties.
* **Statistics:** when `Gather stats data` is set to `True` (default), daily simulation stats are automatically written to `./stats/total-counts.csv` once the simulation completes.

## Generating plots

To generate visualization plots from the collected simulation data:
```bash
python make-plots.py <experiment_index>
```
This reads `./stats/total-counts.csv` and saves generated charts into the `./plots/` folder using the provided index prefix for PNG path.
