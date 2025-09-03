![Python](https://img.shields.io/badge/python-3.8+-blue.svg) ![Status](https://img.shields.io/badge/status-active-success.svg)

# ✈️ Landing Rate Analysis  

This project analyzes **Approach** and **Landing** performance from any given flight data telemetry containing multiple aircraft at once (real data, DCS, MSFS, etc.) to determine all **Final Approach** glideslopes, extract key touchdown/impact parameters, and generates visualizations of the landing approach and touchdown.

## 🎯 Features
### 📉 Approach Analysis: 
-   Visualizes **final approach glideslope** for each aircraft. Each descent segment is rated by a color.
  - Also identifies if the aircraft bounces the touchdown!


    <p align="left">
    <img src="Results/[2025.08.31] Phoenix_landing_3.png" alt="Touchdown Plot" width="500"/>
    </p>


### 🛬 Touchdown Criteria: 
- Extracts and plots key touchdown quantities: 

  | Quantity | Unit | Description |
  | --- | --- | --- |
  | **Vertical Speed** |  $\textit{{fpm}}$ | Vertical speed at touchdown |
  | **Vertical Acceleration** | $\textit{{fpm}}^2$ | Vertical impact-force/acceleration on aircraft CG|
  | **Jerk** | $\textit{{fpm}}^3$ | Sudden change of impact-force/acceleration on aircraft's CG |

    <p align="left">
    <img src="Results/Detailed Touchdowns/[2025.08.31]%Phoenix_touch_3.png" alt="Touchdown Plot"  width="500"/>
    </p>

## 🚧 To be added
- **Landing Rating Criteria**: Customizable criteria for rating the landing performance.
  - Impact **G-force**.
  - $\delta$: Landing gear stroke (the compression when the gear absorbs the impact).
  - **Impact Time**: Time interval when gears are compressed until stabilization.
- **User Interface**: A user-friendly GUI for easy interaction with the analysis tools.

## 🗂️ Folder Structure

- `Datasets/`: Raw CSV data.
- `Results/`:  Analysis results: Approach plots and landing rating CSV file.
- `Detailed Touchdowns/`: Contains detailed plots of each touchdown/impact.
- `Landing Rate.ipynb`: The main Jupyter Notebook for the analysis.

## 🖥️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fardad-d1ce/Landing-Rating.git
   ```
2. Install the required Python libraries:
   ```bash
   pip install datetime numpy pandas matplotlib seaborn
   ``` 
## 📖 User Guide
1. Place your raw CSV data in the `Datasets/` folder.
2. Run the `Landing Rate.ipynb` notebook.
3. Check the `Results/` folder for the analysis outputs.
4. Explore the `Detailed Touchdowns/` folder for detailed plots of each touchdown/impact.
