# Optimizing Electricity Production Costs with Vehicle-to-Grid (V2G) Technology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![Streamlit Version](https://img.shields.io/badge/streamlit-1.20%2B-ff69b4.svg)](https://streamlit.io/)
[![MATLAB/Simulink](https://img.shields.io/badge/MATLAB%2FSimulink-R20XXx-orange.svg)](https://www.mathworks.com/products/matlab.html)

**🚧 Project Status: Under Development 🚧**

## 📖 Overview

This project focuses on optimizing electricity production costs by intelligently integrating Vehicle-to-Grid (V2G) technology. We have adapted a foundational MATLAB & Simulink V2G simulation (see "Acknowledgements" section) to model longer timeframes (monthly) and incorporate real-world solar irradiance data from Meknès, Morocco, along with a generated residential load profile representative of Moroccan consumption patterns.

The core output is a Streamlit-based web application designed to provide weekly forecasts. This application assists users in making informed decisions about whether to utilize stored energy from Electric Vehicles (EVs) via V2G or to supplement power generation with diesel, based on a comprehensive optimization study.

##  V2G Explained

**What is Vehicle-to-Grid (V2G)?**

Vehicle-to-Grid (V2G) is a technology that enables bi-directional energy flow between an electric vehicle's (EV) battery and the power grid. In simpler terms, it allows EVs not only to draw electricity from the grid to charge their batteries but also to send electricity back to the grid when needed.

**How does it work?**

When an EV is plugged into a V2G-enabled charging station, specialized hardware and software manage the flow of electricity.
1.  **Charging:** The EV charges its battery as usual.
2.  **Discharging (V2G Mode):** When the grid requires extra power (e.g., during peak demand hours or when renewable energy generation is low), or when it's economically beneficial, the V2G system can draw stored energy from the EV's battery and feed it back into the grid.
This process is controlled by an aggregator or a utility company, often with the EV owner's consent and potentially with financial incentives for participation.

**When is V2G used?**

V2G can be particularly useful in several scenarios:
* **Peak Shaving:** Discharging EV batteries during peak demand periods to reduce strain on the grid and potentially lower electricity costs for utilities (and consumers).
* **Grid Stabilization:** Providing ancillary services like frequency regulation and voltage support to maintain grid stability.
* **Renewable Energy Integration:** Storing excess renewable energy (e.g., solar power during the day) and discharging it when renewables are not generating (e.g., at night).
* **Emergency Backup Power:** In some configurations, V2G-enabled vehicles could provide backup power during outages.
* **Cost Optimization:** EV owners or fleet managers can potentially earn revenue by selling energy back to the grid or reduce their overall energy costs.

Our project leverages V2G to optimize energy costs by deciding when it's more economical to use stored EV energy versus other sources like diesel generators.

## ✨ Key Features

* **Extended V2G Simulation:** Modified MATLAB/Simulink model for monthly energy analysis, moving beyond the original 24-hour scope.
* **Real-World Data Integration:** Utilizes actual solar irradiation data for Meknès, Morocco, enhancing simulation accuracy.
* **Localized Load Profiling:** Incorporates a generated residential load profile that mirrors typical Moroccan electricity consumption.
* **Optimization-Driven Decisions:** Employs an optimization study to determine the most cost-effective energy management strategies.
* **Interactive Forecasting Tool:** A Streamlit web application provides users with:
    * Weekly energy forecasts.
    * Recommendations on using V2G energy versus purchasing diesel for overload scenarios.
* **Data-Driven Insights:** Generates and analyzes data on load, solar energy production, and available V2G power.

## 🛠️ Technology Stack

* **Simulation:**
    * MATLAB
    * Simulink
* **Data Processing & Optimization:**
    * Python 3
* **Web Application:**
    * Streamlit
* **Data Sources:**
    * Real solar irradiation data for Meknès, Morocco.
    * Generated residential load data reflecting Moroccan consumption.

## 📂 Repository Structure

.├── Notebooks/                  # Jupyter notebooks for data analysis, exploration, model development├── Best Models/                # (Recommended) Storing trained machine learning models or optimization parameters├── Datasets/                   # Storing input data (irradiation, load profiles, simulation outputs)├── README.md                   # This file└── ...                         # Other project files (e.g., requirements.txt, Streamlit app scripts)
## ⚙️ Simulation Details

The core simulation, based on a MATLAB & Simulink model (see Acknowledgements), is adapted for this project. Key modifications include:

* **Extended Time Horizon:** Simulation runs for monthly periods instead of 24 hours.
* **Component Modification:** Removal of the wind farm component from the original model.
* **Data Inputs:**
    * Solar Irradiance: Specific data for Meknès.
    * Residential Load: Custom-generated data reflecting Moroccan usage patterns.
* **Key Outputs:**
    * Total Residential Load
    * Solar Energy Production
    * Total Power Available from EV V2G

## 🚀 Streamlit Application

The Streamlit application serves as the user interface for the optimization system. Its primary functions are:

1.  **Displaying Weekly Forecasts:** Visualizing anticipated energy supply and demand.
2.  **Providing Recommendations:** Advising on whether to:
    * Utilize energy stored in EVs (V2G).
    * Purchase diesel fuel to cover potential energy deficits.
    These recommendations are based on the outputs of the optimization study.

### Prerequisites for Running the App

* Python 3.x
* Streamlit (version specified in badges, e.g., 1.20+)
* Other Python packages (list them in a `requirements.txt` file)

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd YOUR_REPOSITORY_NAME
    ```
2.  **Set up a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv  # Or `python -m venv venv`
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have a `requirements.txt` file listing all necessary Python packages, including Streamlit)*
4.  **Navigate to the application directory (if your app.py is in a subfolder, e.g., App/):**
    ```bash
    # cd App/ # Uncomment if your app is in a subfolder
    ```
5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    *(Replace `app.py` with the actual name of your main Streamlit script if different)*

## 📊 Data

* **Solar Irradiance:** Sourced from [Specify Source, e.g., a meteorological station, public database] for Meknès, Morocco. Stored in `Datasets/Irradiation/`.
* **Residential Load:** Generated data designed to be representative of typical household electricity consumption in Morocco. The generation methodology can be found in `Notebooks/`. Stored in `Datasets/Load_Profiles/`.

## 🙏 Acknowledgements

* This project adapts and builds upon the concepts demonstrated in the "24-hour Simulation of a Vehicle-to-Grid (V2G) System" example provided by MathWorks for MATLAB & Simulink. We thank MathWorks for making such examples available to the community. You can find the original simulation concept [here](https://www.mathworks.com/help/sps/ug/24-hour-simulation-of-a-vehicle-to-grid-v2g-system.html)

## 🔮 Future Work

* [ ] Integrate real-time data feeds for load and solar production.
* [ ] Expand the optimization model to include more variables (e.g., battery degradation costs, dynamic electricity pricing).
* [ ] Develop more sophisticated forecasting models and store them in `Best Models/`.
* [ ] Enhance the user interface with more detailed analytics and visualizations.
* [ ] Conduct a comparative analysis with other energy storage solutions.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or want to contribute to the project, please follow these steps:

1.  Fork the Project.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

Please ensure your code adheres to standard coding practices and includes relevant documentation.

## 📜 License

This project is licensed under the [Your Chosen License - e.g., MIT License]. See the `LICENSE` file for more details.
*(**Note:** You'll need to add a `LICENSE` file to your repository. If you chose MIT, you can easily find a template online.)*

## 📧 Contact

* **SOHAIB DAOUDI:** [soh.daoudi@gmail.com](mailto:soh.daoudi@gmail.com)
* **MAROUANE MAJIDI:** [majidi.marouane0@gmail.com](mailto:majidi.marouane0@gmail.com)

---

*This README was generated with assistance from an AI model, based on project information provided by the user.*
