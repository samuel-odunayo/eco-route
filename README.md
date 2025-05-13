# Eco-Go: Sustainable Transportation Planner

#### Video Demo: [https://youtu.be/HwQQyOHKtNw]

## Overview
Eco-Go is a web application designed to help users find environmentally friendly transportation routes by comparing the carbon footprint of different travel options. The application allows users to see the environmental impact of their transportation choices and track their carbon savings over time.

## Features
- **Route Comparison**: Compare carbon emissions across different transportation methods
- **Interactive Maps**: Visual representation of routes and their environmental impact
- **Personal Dashboard**: Track carbon savings and view environmental impact statistics
- **User Account System**: Save favorite routes and view historical data

## Technology Stack
- **Backend**: Python with Flask framework
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Maps**: Leaflet.js for interactive mapping
- **Charts**: Chart.js for data visualization

## Installation and Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/me50/samuel-odunayo/
   cd eco-route
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```
   flask shell
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

5. Run the application:
   ```
   python app.py
   ```

## Usage
1. Enter your starting point and destination in the route planner
2. View and compare different transportation options
3. Select your preferred mode of transport
4. Save your route to track carbon savings (requires account)
5. View your environmental impact on your personal dashboard

## Project Structure
- `app.py`: Main application file
- `config.py`: Configuration settings
- `models.py`: Database models
- `routes.py`: Application routes
- `carbon_calculator.py`: Carbon footprint calculation utilities
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and images


