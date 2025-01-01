# GeoSearchAI

## Overview

The GeoSearchAI Application is a web-based tool that helps users locate businesses, services, and venues in any specified location worldwide. By leveraging the power of [Google Maps API](https://developers.google.com/maps/documentation/javascript/get-api-key) and [Groq's language model](https://console.groq.com/playground), the app extracts key details from user input and returns comprehensive search results.

## Key Features

1. AI-Powered Extraction: Uses Groq's LLM to extract business type, city, and country from natural language queries.

2. Google Maps Integration: Fetches location data and business details from Google Maps API.

3. Multi-Format Data Export: Allows users to download search results in CSV, Excel, or JSON formats.

4. Interactive Web Interface: Built with Streamlit, providing an intuitive and responsive UI.

5. Detailed Business Information: Fetches phone numbers, websites, and Google Maps URLs for each business.


## Technologies Used

- Python

- Streamlit

- Google Maps API

- Groq LLM (llama3-8b-8192)

- Pandas

- XlsxWriter

- Requests

- dotenv


### Clone the Repository

- Clone the repository
```
git clone https://github.com/muhammadtalha72014/GeoSearchAI.git
```

- Navigate to project directory
```
cd GeoSearchAI
```

### Create a Virtual Environment

- Create virtual environment
```
conda create -p venv python==3.9 -y
```

- Activate virtual environment (Windows)
```
conda activate venv/
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Environment Variables

Create a .env file in the root directory and add the following:
```
GROQ_API_KEY=your_groq_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### Running the Application
```
streamlit run app.py
```

### Output

![Screenshot 2025-01-01 160042](https://github.com/user-attachments/assets/b44517c7-1ace-4b19-99a5-d51e98da99a5)
![Screenshot 2025-01-01 160230](https://github.com/user-attachments/assets/a1cbd739-ef2d-4d15-a160-b4996b29f9c7)
![Screenshot 2025-01-01 160409](https://github.com/user-attachments/assets/9f28bc89-a3b2-4a1a-bf9e-7266414d88d5)
