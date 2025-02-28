# GeoDistanceCalculator

This Python tool calculates the Haversine distance between cities based on their geographical coordinates. It uses the Haversine formula to determine the minimum distance between two points on a sphere, assuming the Earth is a sphere. The tool fetches geographical coordinates using the Maps API and processes city information from an Excel file.

## Features

- Converts degrees to radians.
- Calculates the Haversine distance between two coordinates.
- Uses reverse geocoding to get coordinates from city and country names.
- Reads city data from an Excel file and writes the results back to another Excel file.
- Handles different country encoding formats.
- Provides feedback on progress and logs cities that could not be found.

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/mpenalverguilera/geo-distance-calculator.git
    cd geo-distance-calculator
    ```

2. **Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Prepare the input Excel file:**
   
   The input Excel file should contain a sheet with the following columns:
   - Country ISO_A encoding
   - Country ISO_A2 encoding
   - Country private encoding
   - City name
   - Distance (initially empty)

2. **Fill the config file**
    - Add the API key
    - Change the I/O excel information if needed
    - Change the origin if needed

3. **Run the script:**

    ```sh
    python calculadora_distancies.py
    ```

4. **Output:**
   
   The script will generate a new Excel file with the calculated distances and log the cities that could not be found.

## Dependencies

- requests
- pandas
- math
- time

Install the dependencies using:

```sh
pip install requests pandas
```
## Future Improvements

1. **Error Handling**: Implement more robust error handling, especially for network requests and file operations.
2. **Logging**: Instead of printing progress and errors to the console, consider using Python's `logging` module for better log management.
3. **Unit Tests**: Add unit tests to ensure the functions work correctly and to facilitate future changes.
