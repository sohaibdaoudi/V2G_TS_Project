# Optimizing Electricity Production Costs with Vehicle-to-Grid (V2G) Technology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/) [![Streamlit Version](https://img.shields.io/badge/streamlit-1.20%2B-ff69b4.svg)](https://streamlit.io/) [![MATLAB/Simulink](https://img.shields.io/badge/MATLAB%2FSimulink-R20XXx-orange.svg)](https://www.mathworks.com/products/matlab.html) ## 📖 Overview

This project focuses on optimizing electricity production costs by intelligently integrating Vehicle-to-Grid (V2G) technology. We have adapted a foundational MATLAB & Simulink V2G simulation to model longer timeframes (monthly) and incorporate real-world solar irradiance data from Meknès, Morocco, along with a generated residential load profile representative of Moroccan consumption patterns.

The core output is a Streamlit-based web application designed to provide weekly forecasts. This application assists users in making informed decisions about whether to utilize stored energy from Electric Vehicles (EVs) via V2G or to supplement power generation with diesel, based on a comprehensive optimization study.

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
    * Python
    * (Potentially libraries like Pandas, NumPy, SciPy for optimization - *User to specify*)
* **Web Application:**
    * Streamlit
* **Data Sources:**
    * Real solar irradiation data for Meknès, Morocco.
    * Generated residential load data reflecting Moroccan consumption.

## 📂 Repository Structure

.
├── Simulation/                 # Contains the modified MATLAB & Simulink simulation files
├── Data/                       # (Recommended) For storing input data (irradiation, load profiles)
│   ├── Irradiation/
│   └── Load_Profiles/
├── App/                        # (Recommended) Contains the Streamlit application code
│   └── app.py
├── Optimization/               # (Recommended) Scripts related to the optimization study
├── Notebooks/                  # (Optional) Jupyter notebooks for data analysis, exploration
├── README.md                   # This file
└── ...                         # Other project files (e.g., requirements.txt)

## ⚙️ Simulation Details

The core simulation, located in the `Simulation/` folder, is an adapted version of a standard V2G system model. Key modifications include:

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

* Python (version specified in badges, e.g., 3.9+)
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
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have a `requirements.txt` file listing all necessary Python packages, including Streamlit)*
4.  **Navigate to the application directory (if applicable):**
    ```bash
    cd App/
    ```
5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    *(Replace `app.py` with the actual name of your main Streamlit script if different)*

## 📊 Data

* **Solar Irradiance:** Sourced from [Specify Source, e.g., a meteorological station, public database] for Meknès, Morocco.
* **Residential Load:** Generated data designed to be representative of typical household electricity consumption in Morocco. The generation methodology can be found in [Specify where - e.g., a specific script, a document in the repo].

## 🔮 Future Work

* [ ] Integrate real-time data feeds for load and solar production.
* [ ] Expand the optimization model to include more variables (e.g., battery degradation costs, dynamic electricity pricing).
* [ ] Develop more sophisticated forecasting models.
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

[Your Name / Organization Name] - [your.email@example.com]

Project Link: [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME)

---

*This README was generated with assistance from an AI model, based on project information provided by the user.*
