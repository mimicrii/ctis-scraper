# CTIS-Scraper

## Description
This project is a Python-based web scraper that uses the European Clinical Trials Information System's (CTIS) internal API to gather data. The collected data is then transformed and saved in a PostgreSQL database using SQLAlchemy. 

## Features
- Web scraping using the website's internal API
- Data transformation
- CRUD operations with SQLAlchemy
- Dockerized setup

## Project Structure
- schemas.py: Defines the database schema.
- crud.py: Contains CRUD operations.
- api.py: Handles API calls to the target website.
- Dockerfile: Configuration file to build a Docker image of the project.

## Installation

### Prerequisites
- Python 3.10+
- Docker

### Clone the Repository
```bash
git clone https://github.com/mimicrii/ctis-scraper.git
cd ctis-scraper
```

## Usage

### Running the Project Locally

#### Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
A database URI with the following format has to be provided in a .env file:
```bash
DATABASE_URI="postgresql+psycopg2://username:password@db_ip:db_port/db_name"
```

#### Run the Project
```bash
python main.py scrape
```

### Running the Project with Docker

#### Build the Docker Image
```bash
docker build -t your_image_name .
```

#### Run the Image
Use the image you built in the previous step:
```bash
docker run --rm -e DATABASE_URI=your_database_uri your_image_name
```
Use this repo's prebuilt image:
```bash
docker run --rm -e DATABASE_URI=your_database_uri ghcr.io/mimicrii/ctis-scraper:latest
```
### Updating Location Coordinates
In the location table, there is a latitude and longitude column. By default, those columns stay empty as CTIS itself doesn't provide any coordinates. However, if you plan on working with coordinates, you can update these columns using the OpenStreetMap Nominatim Geocoding API by providing the update_coordinates argument when running the project. 
```bash
python main.py update_coordinates
```
```bash
docker run --rm -e DATABASE_URI=your_database_uri your_image_name update_coordinates
```
The coordinates are stored persistently in the database so that they are retained even if the actual scraper script is run regularly.

## Database
This project was developed using a PostgreSQL database. Using a different SQL dialect should not be a problem. However, the database URI must be adapted accordingly and, depending on the dialect, the database schema in schemas.py must be adapted.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.
