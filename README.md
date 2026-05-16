# 🌿 EcoMonitor System

EcoMonitor is a full-stack ecological monitoring system designed for the multitemporal analysis of Andean ecosystems using Sentinel-2 data.

This project includes a REST API built with FastAPI, a relational MySQL database, and a lightweight administrative web interface. It facilitates the management of ecological monitoring records, sampling points, spectral observations, satellite image metadata, biomes, species, and monitoring reports.

---

## 🚀 Main Features

- **Full CRUD Operations**: Complete management for the ecological monitoring database.
- **FastAPI Backend**: High-performance REST API connected to a MySQL database.
- **Administrative Interface**: Simple, lightweight HTML/CSS/JavaScript frontend requiring no additional frameworks.
- **Sentinel-2 Integration**: Native support for satellite image metadata and biophysical proxies.
- **Comprehensive Entity Management**: Track ecological areas, biomes, species, sampling points, spectral observations, and field monitoring records.
- **Local Image Visualization**: Seamlessly serve and preview images from a local `Images/` directory.
- **Containerized Database**: Docker-based MySQL setup for reproducible environments.

---

## 📁 Project Structure

```txt
EcoMonitor/
├── main.py                  # FastAPI backend application
├── interfaz.html            # Administrative frontend interface
├── eco_monitoring_db.sql    # SQL database schema and initialization
├── docker-compose.yml       # MySQL container configuration
├── requirements.txt         # Python dependencies
├── start.sh                 # Optional backend startup script
├── stop.sh                  # Optional backend stop script
├── Images/                  # Local PNG images used by the interface
├── ERD.pdf                  # Entity-Relationship Diagram
└── README.md                # Project documentation
```

---

## ✅ Prerequisites

Before running the project, ensure you have the following installed:

* **Git**
* **Python 3.10** or newer
* **Docker** and **Docker Compose**
* **Miniconda** (recommended) or Python `venv`
* A modern web browser (Firefox, Chrome, Brave, Edge, etc.)

---

## 🛠️ Installation and Setup

### 1. Clone the Repository

Download the project to your local machine and navigate into the directory:

```bash
git clone [https://github.com/jammes314/Database-System-for-Multitemporal-Analysis-of-Andean-Ecosystems-Using-Sentinel-2-Data.git](https://github.com/jammes314/Database-System-for-Multitemporal-Analysis-of-Andean-Ecosystems-Using-Sentinel-2-Data.git)
cd Database-System-for-Multitemporal-Analysis-of-Andean-Ecosystems-Using-Sentinel-2-Data
```

### 2. Create a Python Environment

It is highly recommended to isolate project dependencies using Conda:

```bash
conda create -n ecomonitor python=3.10
conda activate ecomonitor
```

### 3. Install Dependencies

Install the required Python packages for the FastAPI backend:

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

The project relies on a MySQL database. The easiest and recommended way to spin this up is via Docker Compose.

**1. Start the database container:**
```bash
docker compose up -d
```

*Note: You can verify the container is running by executing `docker ps`.*

**2. Initialize the Database:**
If this is your first time running the project or the database is empty, populate it with the provided schema:

```bash
mysql -h localhost -P 3306 -u api_user -p eco_monitoring_db < eco_monitoring_db.sql
```
*(Enter the password specified in your `docker-compose.yml` when prompted).*

---

## ▶️ Running the Application

### Starting the Backend
To launch the FastAPI server, ensure you are in the project root directory and run the provided startup script:

```bash
bash start.sh
```

To gracefully stop the server:
```bash
bash stop.sh
```

### Accessing the Frontend
Once the backend is running, simply open the `interfaz.html` file in your preferred web browser to access the administrative dashboard.

---

## 🌱 Usage & Seed Data

### Loading Test Data
The project includes a dedicated endpoint to load demonstration data, which is highly useful for testing the system's visualization and CRUD capabilities. 

To populate the database with seed data:
1. Open the frontend (`interfaz.html`).
2. Click the **"Seed DB"** button.
3. Refresh the view to see the populated records.

Alternatively, you can trigger this via the API:
```http
POST /seed
```

---

## 📚 API Documentation

FastAPI automatically generates interactive Swagger documentation. Once the backend is running, you can explore and test the API endpoints by navigating to:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## ⚙️ Configuration Notes

**Recommended Image Path Configuration:**
For stable public use, avoid using personal absolute file paths. The recommended configuration inside `main.py` is:

```python
import os
IMAGES_DIR = os.getenv("IMAGES_DIR", os.path.join(os.path.dirname(__file__), "Images"))
```

---

## 📌 Important Notes

* **Boot Order:** The database container must be running *before* launching the API, and the backend API must be running *before* interacting with the frontend.
* **Image Management:** 
  * The `Images/` folder must exist in the root directory if image previews are utilized.
  * Image filenames must exactly match their corresponding database IDs.
  * All images must use the `.png` file extension.
* **Architecture:** The frontend does not access local files directly; all images and data are served securely through the FastAPI backend.
* **Scope:** This project is explicitly intended for academic, educational, and research-oriented ecological monitoring workflows.

---

## 📄 License

This project is open for adaptation and use in educational and research contexts.
