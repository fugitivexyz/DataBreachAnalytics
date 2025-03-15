# DataBreachAnalytics 🔒

A comprehensive data visualization dashboard built with Streamlit that analyzes and presents insights from data breaches tracked by HaveIBeenPwned.

## Project Overview

This dashboard provides interactive visualizations and analysis of data breaches, helping users understand:
- Timeline trends of data breaches
- Types of compromised data
- Breach size distributions
- Security insights and recommendations

## Features

### 1. Home Dashboard
- Overview metrics of data breaches
- Interactive filters for date range, verification status, and breach size
- Dynamic visualizations of breach trends

### 2. Timeline Analysis
- Yearly and monthly breach distribution
- Breach size evolution over time
- Seasonal pattern identification

### 3. Data Classes Analysis
- Distribution of compromised data types
- Common data class combinations
- Temporal analysis of data types
- Security recommendations

## Data Source

The data is sourced from the [HaveIBeenPwned API v3](https://haveibeenpwned.com/api/v3/breaches). Currently, the project uses a local JSON file (`breaches.json`) that contains the API response. This approach was chosen to:
- Reduce API calls during development
- Enable offline development
- Avoid rate limiting issues

To update the data, you can fetch the latest breaches from the API and save them to `breaches.json`.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fugitivexyz/DataBreachAnalytics.git
cd DataBreachAnalytics
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run Home.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Use the sidebar filters to customize your analysis

## Project Structure

```
DataBreaches/
├── Home.py                 # Main dashboard file
├── breaches.json           # Data file containing breach information
├── requirements.txt        # Project dependencies
└── pages/
    ├── 1_Timeline_Analysis.py    # Timeline analysis page
    └── 2_Data_Classes_Analysis.py # Data classes analysis page
```

## Dependencies

- streamlit
- pandas
- plotly
- python-dateutil

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Data provided by [HaveIBeenPwned](https://haveibeenpwned.com/)
- Built with [Streamlit](https://streamlit.io/)