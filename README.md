# 🔋⚡ Intelligent Energy Management System with V2G Technology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE.txt) 
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![Streamlit Version](https://img.shields.io/badge/streamlit-1.20%2B-ff69b4.svg)](https://streamlit.io/)
[![MATLAB/Simulink](https://img.shields.io/badge/MATLAB%2FSimulink-R20XXx-orange.svg)](https://www.mathworks.com/products/matlab.html)

## 🚧 Project Status: Under Active Development 🚧
### Attention:
This application currently uses first-version models trained on limited data without standardization. An improved version will be released soon.

## Notebooks Overview

Our project includes several Jupyter notebooks that demonstrate various aspects of our data analysis and modeling approach:

| Notebook | Description |
|----------|-------------|
| **Final_Project_Simulation.ipynb** | Main project simulation and integration of all components |
| **Load-DeepLearning.ipynb** | Development of RNN models for load forecasting |
| **Load-StatisticalStudy.ipynb** | Statistical analysis of load patterns and trends |
| **SolarEnergy-DeepLearning.ipynb** | BiLSTM models for solar energy production forecasting |
| **SolarEnergy-StatisticalStudy.ipynb** | Statistical analysis of solar generation data |
| **Cars_Energy_dispo-DeepLearning.ipynb** | RNN models for V2G energy availability prediction |

## 📋 Quick Links
- [Overview](#overview)
- [V2G Technology Explained](#v2g-explained)
- [Key Features](#key-features)
- [Notebooks Overview](#notebooks-overview)
- [Streamlit App Components](#streamlit-app-components)
- [Technology Stack](#technology-stack)
- [Simulation Details](#simulation-details)
- [Repository Structure](#repository-structure)
- [Installation & Usage](#running-the-application)
- [Acknowledgements](#acknowledgements)
- [License](#license)
- [Contact](#contact)

## Overview

This project presents an intelligent energy management system that leverages Vehicle-to-Grid (V2G) technology to optimize electricity production costs. Using deep learning methods, we forecast key energy components and provide decision support for when to utilize stored energy from Electric Vehicles (EVs) versus supplementing with diesel generation.

The system integrates real-world solar irradiance data from Meknès, Morocco, along with residential load profiles representative of Moroccan consumption patterns. Our Streamlit application delivers weekly forecasts and cost-optimization recommendations based on comprehensive time series analysis.

## V2G Explained

### What is Vehicle-to-Grid (V2G)?

Vehicle-to-Grid (V2G) is a cutting-edge technology enabling bidirectional energy flow between electric vehicle batteries and the power grid. Unlike conventional EV charging, V2G allows vehicles to not only consume electricity but also return it to the grid when beneficial.

![Image](https://github.com/user-attachments/assets/f0aac5e9-e10b-41d8-8296-e3e35398dc79)

## Streamlit App Components

Our interactive web application provides a user-friendly interface for energy management decision support:

### Key App Modules

- **data_utils.py**: Functions for loading and preprocessing time series data
- **model_utils.py**: Handles model loading and prediction generation
- **optimization.py**: Implements cost optimization algorithms
- **visualization.py**: Creates interactive charts and data visualizations
- **utils.py**: General utility functions used throughout the application

### App Features

- Weekly forecasts for load, solar production, and V2G availability
- Cost comparison between V2G utilization and diesel generation
- Interactive visualizations of energy patterns
- Optimization recommendations for energy sourcing

When connected to a V2G-enabled charging station, the system manages electricity flow through:

1. **Charging Mode:** The EV draws power from the grid to charge its battery
2. **Discharging (V2G) Mode:** The EV feeds stored energy back to the grid when:
   - Grid demand peaks 
   - Energy prices are high
   - Renewable energy generation is low

This process is coordinated through sophisticated control systems with EV owner consent, typically including financial incentives for participation.

### V2G Use Cases

V2G technology offers multiple benefits across the energy ecosystem:

| Use Case | Description |
|----------|-------------|
| **Peak Shaving** | Reduces grid strain during high-demand periods by supplying stored EV energy |
| **Grid Stabilization** | Provides ancillary services like frequency regulation and voltage support |
| **Renewable Integration** | Stores surplus renewable energy for use when generation is insufficient |
| **Emergency Backup** | Offers potential backup power during outages |
| **Economic Optimization** | Creates revenue opportunities for EV owners through energy arbitrage |

Our project specifically focuses on cost optimization by determining when V2G utilization is more economical than alternative generation sources.

## Key Features

- **Advanced Time Series Forecasting:** Deep learning models (RNN, BiLSTM, GRU) for accurate prediction of energy components
- **Localized Data Integration:**
  - Actual solar irradiation data from Meknès, Morocco
  - Realistic residential load profiles mirroring Moroccan consumption patterns
- **Cost Optimization Engine:** Algorithms to determine optimal energy sourcing strategies
- **Interactive Decision Support:** Streamlit application providing:
  - Weekly energy forecasts
  - Cost-comparison between V2G and diesel generation
  - Actionable recommendations for energy management
- **Comprehensive Analytics:** Data visualization and insights on load patterns, solar production, and V2G availability

## Technology Stack

### Deep Learning Models
- TensorFlow/Keras
- Recurrent Neural Networks (RNN)
- Bidirectional LSTM (BiLSTM)
- Gated Recurrent Units (GRU)

### Data Processing & Analysis
- Python 3.x
- Pandas
- NumPy
- Scikit-learn

### Web Application
- Streamlit

### Data Sources
- Solar irradiation measurements from Meknès, Morocco
- Synthetic residential load profiles based on Moroccan consumption patterns

## Repository Structure

```
Intelligent-Energy-Management-System-with-V2G-Technology/
├── Notebooks/                  # Jupyter notebooks for data analysis
│   ├── Cars_Energy_dispo-DeepLearning.ipynb    # V2G energy availability modeling
│   ├── Final_Project_Simulation.ipynb          # Complete project simulation
│   ├── Load-DeepLearning.ipynb                 # Load forecasting with deep learning
│   ├── Load-StatisticalStudy.ipynb             # Statistical analysis of load data
│   ├── SolarEnergy-DeepLearning.ipynb          # Solar energy prediction models
│   └── SolarEnergy-StatisticalStudy.ipynb      # Statistical analysis of solar data
│
├── Best Models/                # Optimized predictive models
│   ├── best_model_BILSTM_SolarEnergy.h5        # BiLSTM model for solar prediction
│   ├── best_model_RNN_LOAD.h5                  # RNN model for load forecasting
│   └── RNN_CarsEnergy_v2g.h5                   # RNN model for V2G availability
│
├── Datasets/                   # Raw and processed datasets
│   ├── Solar_energy_cleaned.csv                # Processed solar energy data
│   ├── Total_Load.csv                          # Load profile dataset
│   └── total_power_EV_disponible.xlsx          # Available EV power data
│
├── App_version_one/            # Streamlit application
│   ├── app.py                  # Main application entry point
│   ├── data_utils.py           # Data processing utilities
│   ├── model_utils.py          # Model loading and prediction functions
│   ├── optimization.py         # Cost optimization algorithms
│   ├── utils.py                # General utility functions
│   ├── visualization.py        # Data visualization components
│   ├── style.css               # Custom CSS styling
│   ├── requirements.txt        # App-specific dependencies
│   │
│   ├── data/                   # Application data files
│   │   ├── Solar_Energy.xlsx
│   │   ├── Total_Load.xlsx
│   │   └── total_power_EV_disponible.xlsx
│   │
│   └── models/                 # Deployed model files
│       ├── best_model_GRU_solar.h5
│       ├── best_model_name_V2G_EV_energy_dispo.h5
│       └── Load_Best_model_15.h5
│
├── README.md                   # Project documentation
└── LICENSE.txt                 # MIT License
```

## Simulation Details

Our project leverages deep learning techniques to model and forecast three critical components of the V2G ecosystem:

### Key Components
- **Load Forecasting:** Predicting residential electricity demand using RNN models
- **Solar Energy Production:** Forecasting solar energy generation with BiLSTM/GRU models
- **V2G Availability:** Modeling available power from electric vehicle fleets

### Data Inputs
- **Solar Irradiance:** High-resolution measurements from Meknès region
- **Residential Load:** Load profile data reflecting Moroccan consumption patterns
- **EV Fleet Parameters:** Available power data from electric vehicles

### Forecasting Outputs
- Total Residential Load (kW)
- Solar Energy Production (kW)
- Available V2G Power Capacity (kW)
- Cost Optimization Metrics (MAD/kWh)

## Running the Application

### Prerequisites
- Python 3.7+
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone --depth 1 --filter=blob:none --sparse https://github.com/MarouaneMajidi/Intelligent-Energy-Management-System-with-V2G-Technology.git
   cd Intelligent-Energy-Management-System-with-V2G-Technology
   git sparse-checkout init --cone
   git sparse-checkout set App_version_one

   ```

2. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Streamlit app dependencies:**
   ```bash
   cd App_version_one
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

## Acknowledgements

This project draws inspiration from the "24-hour Simulation of a Vehicle-to-Grid (V2G) System" example provided by MathWorks. We extend our gratitude to MathWorks for providing this valuable conceptual foundation. The original simulation concept can be found [here](https://www.mathworks.com/help/sps/ug/24-hour-simulation-of-a-vehicle-to-grid-v2g-system.html).

We also acknowledge the following resources that contributed to this project:
- TensorFlow/Keras documentation for deep learning implementation
- Streamlit documentation for web application development
- Various academic papers on V2G optimization techniques

## License

This project is licensed under the [MIT License](./LICENSE.txt) - see the LICENSE.txt file for details.

## Contact

### Project Maintainers

- **Sohaib Daoudi**
  - Email: [soh.daoudi@gmail.com](mailto:soh.daoudi@gmail.com)
  - GitHub: [@sohaibdaoudi](https://github.com/sohaibdaoudi)

- **Marouane Majidi**
  - Email: [majidi.marouane0@gmail.com](mailto:majidi.marouane0@gmail.com)
  - GitHub: [@marouanemajidi](https://github.com/marouanemajidi)

---

<p align="center">
  <em>Powering the future, one vehicle at a time.</em>
</p>
