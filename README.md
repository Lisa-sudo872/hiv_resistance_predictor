# hiv_resistance_predictor
## Overview
The HIV Resistance Predictor is a machine learning-based tool designed to predict HIV resistance using genetic data. This project aims to assist healthcare professionals in making informed decisions regarding HIV treatment options.

## Features
- **Predictive Modeling**: Utilizes advanced machine learning algorithms to predict HIV resistance.
- **User Authentication**: Secure login system for users to access prediction tools.
- **Data Management**: Efficient handling and storage of user predictions and related data.

## Technology Stack
- **Programming Language**: Python
- **Web Framework**: Flask
- **Database**: SQLite

## Installation
To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Lisa-sudo872/hiv_resistance_predictor.git
   cd hiv_resistance_predictor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python setup_database.py
   ```

5. Run the application:
   ```bash
   flask run
   ```

## Usage
After starting the application, navigate to `http://127.0.0.1:5000` in your web browser. You will be prompted to log in or create an account. Once logged in, you can input genetic data to receive predictions on HIV resistance.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project does not currently have a specified license. Please check back for updates.

## Contact
For any questions or feedback, please reach out to [lisa.mhlanga@students.uz.ac.zw

