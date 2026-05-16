# 🌿 EcoMonitor System

EcoMonitor is a full-stack ecological monitoring system designed for the multitemporal analysis of Andean ecosystems using Sentinel-2 data.

The project includes a REST API built with FastAPI, a relational MySQL database, and a lightweight administrative web interface for managing ecological monitoring records, sampling points, spectral observations, satellite image metadata, biomes, species, and monitoring reports.

---

## 🚀 Main Features

- Full CRUD operations for the ecological monitoring database.
- FastAPI backend connected to a MySQL database.
- Simple HTML/CSS/JavaScript administrative interface.
- Support for Sentinel-2 image metadata.
- Management of ecological areas, biomes, species, sampling points, spectral observations, and field monitoring records.
- Image visualization from a local `Images/` folder.
- Docker-based database setup.
- Lightweight frontend with no additional JavaScript framework required.

---

## 📁 Project Structure

```txt
EcoMonitor/
├── main.py                  # FastAPI backend
├── interfaz.html            # Administrative frontend
├── eco_monitoring_db.sql    # SQL database schema
├── docker-compose.yml       # MySQL container configuration
├── requirements.txt         # Python dependencies
├── start.sh                 # Optional startup script
├── stop.sh                  # Optional stop script
├── Images/                  # Local PNG images used by the interface
├── ERD.pdf                  # Entity-Relationship Diagram
└── README.md



#✅ Prerequisites
Before running the project, install the following tools:
Git
Python 3.10 or newer
Docker and Docker Compose
Miniconda or Python venv
A modern web browser such as Firefofox, Chrome, Brave, Edge, etc.


# 🛠️ Installation and Setup
1. Clone the repository
git clone https://github.com/jammes314/Database-System-for-Multitemporal-Analysis-of-Andean-Ecosystems-Using-Sentinel-2-Data.git
cd Database-System-for-Multitemporal-Analysis-of-Andean-Ecosystems-Using-Sentinel-2-Data

2. Create a Python environment

Using Conda:
conda create -n ecomonitor python=3.10
conda activate ecomonitor


3. Install dependencies
pip install -r requirements.txt

# 🗄️ Database Setup

The project uses MySQL. The recommended way to run it is with Docker Compose.
Start the database container:

docker compose up -d
Check that the container is running:

docker ps

If it is the first time or the database is empty:
mysql -h localhost -P 3306 -u api_user -p eco_monitoring_db < eco_monitoring_db.sql

# ▶️ Running the Backend
You can use every time to start on your terminal:
cd ...( go to the directory where you get  everything from Git-Hub.)
bash start.sh
To stop it:
bash stop.sh
# ⚙️ Recommended Image Path Configuration

For public use, avoid personal absolute paths. The recommended configuration in main.py is:
IMAGES_DIR = os.getenv("IMAGES_DIR", os.path.join(os.path.dirname(__file__), "Images"))



# 🌱 Seed Data

The project includes a seed endpoint to load demonstration data:

POST /seed

The frontend includes a button called:

Seed DB

This button loads sample records into the database and is useful for testing the system.

#📚 API Documentation

FastAPI automatically generates interactive documentation.

After running the backend, open:

http://localhost:8000/docs

#📌 Important Notes
The backend must be running before using the frontend.
The database must be running before launching the API.
The Images/ folder must exist if image preview is used.
Image filenames must match database IDs exactly.
Images must use the .png extension.
The frontend does not access local files directly; images are served through FastAPI.
The project is intended for academic, educational, and research-oriented ecological monitoring workflows.

📄 License

This project can be adapted for educational and research purposes.
