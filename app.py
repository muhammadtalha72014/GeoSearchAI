import streamlit as st
import requests
import pandas as pd
import json
import time
from groq import Groq
import xlsxwriter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access API keys
groq_api_key = os.getenv("GROQ_API_KEY")
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Function to extract information using LLM
# Function to extract information using LLM
def extract_information(user_input):
    extraction_prompt = (
        f"Identify and extract the following information from the input:\n"
        f"- Business type or service: Identify the type of business, service, or help required based on the context. "
        f"For example, if the input mentions an item like 'AC', infer 'AC shop'. If it mentions 'Laptop', infer 'Laptop shop'. "
        f"If the input mentions a need for police, ambulance, or emergency help, infer 'Police service', 'Ambulance service', etc. Generalize for any item or service mentioned.\n"
        f"- City: Extract the name of the city or region mentioned.\n"
        f"- Country: Extract the name of the country mentioned.\n\n"
        f"Input: {user_input}\n\n"
        f"Output:\n"
        f"Business type or service: <business_or_service>\nCity: <city>\nCountry: <country>"
    )

    # Request completion from LLM
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'user', 'content': extraction_prompt}],
        model='llama3-8b-8192'
    )
    return chat_completion.choices[0].message.content.strip()


# Function to safely parse extracted info
def parse_extracted_info(extracted_info):
    parsed_data = {"Business type": "", "City": "", "Country": ""}

    for line in extracted_info.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip().lower(), value.strip()
            if "business type" in key:
                parsed_data["Business type"] = value
            elif "city" in key:
                parsed_data["City"] = value
            elif "country" in key:
                parsed_data["Country"] = value

    return parsed_data


# Function to fetch all places using Google Maps API
def fetch_all_places(business_type, city, country):
    query = f"{business_type} in {city}, {country}"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    places_list = []
    next_page_token = None

    # Loop to paginate through results
    while True:
        params = {'query': query, 'key': google_maps_api_key}
        if next_page_token:
            params['pagetoken'] = next_page_token

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {"error": f"HTTP Error {response.status_code}: Unable to fetch data from Google Maps."}

        results = response.json()
        if results.get('status') != 'OK':
            return {"error": f"API Error: {results.get('status')}. Details: {results.get('error_message', '')}"}


        # Append results to the list
        places_list.extend(results.get('results', []))
        next_page_token = results.get('next_page_token')

        # Wait for next-page token to activate
        if not next_page_token:
            break
        time.sleep(2)  # Pause to allow token activation

     # Display all fetched places
    if not places_list:
        return {"error": "No locations found for the specified search query."}
    
    return places_list

def fetch_place_details(place_id):
    """
    Fetch additional details for a place using the Place Details API.
    """
    place_details_endpoint = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "key": google_maps_api_key,
        "place_id": place_id,
        "fields": "formatted_phone_number,website",
    }

    response = requests.get(place_details_endpoint, params=params)
    if response.status_code == 200:
        return response.json().get("result", {})
    else:
        return {}

# Function to process and save the data
def process_places_data(places_list):
    data = []
    for idx, place in enumerate(places_list, 1):
        
        place_id = place.get("place_id", "")
        
        # Default details
        phone_number = ""
        website = ""

        # If Place ID exists, fetch details
        if place_id:
            details = fetch_place_details(place_id)
            phone_number = details.get("formatted_phone_number", "N/A")
            website = details.get("website", "N/A")
            
        google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else ""

        entry = {
            "Name": place.get("name", ""),
            "Address": place.get("formatted_address", ""),
            "Latitude": place.get("geometry", {}).get("location", {}).get("lat", ""),
            "Longitude": place.get("geometry", {}).get("location", {}).get("lng", ""),
            "Rating": place.get("rating", ""),
            "User Ratings Total": place.get("user_ratings_total", ""),
            "Phone Number": phone_number,
            "Website": website,
            "URL": google_maps_url  # Add URL link here
        }
        data.append(entry)

    return pd.DataFrame(data)

def save_data(df, file_format):
    if file_format == "CSV":
        return df.to_csv(index=False).encode('utf-8'), 'text/csv', 'places_data.csv'
    elif file_format == "Excel":
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)  # Go to the beginning of the file-like object
        return output.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'places_data.xlsx'
    elif file_format == "JSON":
        return df.to_json(orient='records').encode('utf-8'), 'application/json', 'places_data.json'


# Streamlit UI
def main():
    st.title("GeoSearchAI")

    # Use a form to allow pressing Enter or clicking the Search button
    with st.form(key="search_form"):
        user_input = st.text_input("Enter your search query (e.g., 'Find restaurants in New York, USA')")
        search_button = st.form_submit_button("Search")  # Submit button to trigger search

    if search_button:
        if user_input:
            st.info("Extracting information...")
            extracted_info = extract_information(user_input)
            parsed_info = parse_extracted_info(extracted_info)

            business_type = parsed_info["Business type"]
            city = parsed_info["City"]
            country = parsed_info["Country"]

            if not business_type or not city or not country:
                st.error("Error: Failed to extract necessary details. Please ensure your input includes a business type, city, and country.")
            else:
                st.info(f"Searching for '{business_type}' in {city}, {country}...")
                places = fetch_all_places(business_type, city, country)

                if places:
                    st.success(f"Found {len(places)} places. Processing data...")
                    df = process_places_data(places)
                    
                    # Store the results in session_state to prevent resetting
                    st.session_state.df = df

                    # st.dataframe(df)
                    
                    # Generate files in all formats and save data in session_state
                    st.session_state.csv_data = save_data(df, "CSV")
                    st.session_state.excel_data = save_data(df, "Excel")
                    st.session_state.json_data = save_data(df, "JSON")
                        
                else:
                    st.warning("No data found. Please refine your query.")
        else:
            st.error("Error: Please provide a valid search query.")
            
    # If there is data already in session_state, display it
    if 'df' in st.session_state:
        st.dataframe(st.session_state.df)

        # Display download buttons for each format
        st.download_button(
            label="Download as CSV",
            data=st.session_state.csv_data[0],
            file_name=st.session_state.csv_data[2],
            mime=st.session_state.csv_data[1]
        )

        st.download_button(
            label="Download as Excel",
            data=st.session_state.excel_data[0],
            file_name=st.session_state.excel_data[2],
            mime=st.session_state.excel_data[1]
        )

        st.download_button(
            label="Download as JSON",
            data=st.session_state.json_data[0],
            file_name=st.session_state.json_data[2],
            mime=st.session_state.json_data[1]
        )        
    
if __name__ == "__main__":
    main()