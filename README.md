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
