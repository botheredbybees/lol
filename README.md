# LearnOnline.cc

## Introduction

LearnOnline.cc is a **gamified vocational training platform** leveraging the Australian Quality Training Framework (AQTF) data to deliver structured, nationally recognized training content. With integrated **game mechanics**, it enhances learner engagement and motivation. The platform syncs with **Training.gov.au (TGA)** to fetch and process training packages, units of competency, and their elements and performance criteria.

Previously, I developed **NTISthis**, a tool that generated assessment templates for vocational education using AQTF qualifications. However, due to high operational costs, I discontinued the service. LearnOnline.cc takes a more **flexible and experimental approach**—embracing “vibe programming” and AI-assisted development. I’m working with tools like **NotebookLM, Clive, Roo, Copilot, Claude, and Cline** to refine my workflow.

## Technologies Used

The platform combines:
- **Django** (Back end API)
- **Phaser.js** (Game engine for interactive front-end elements)
- **GSAP.js** (Animation framework for smooth UI transitions)
- **Docker** (Containerized deployment)
- **MySQL** (Database backend)
- **SCORM Integration** (For tracking and adaptive learning analytics)

## Setup

To get started, install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on your system.

### Clone the repository:
```sh
git clone https://github.com/botheredbybees/lol.git
cd lol
```

### Run the containers:
```sh
docker-compose up --build
```

This will build and start all required services.

## Accessing Services

Once the containers are running, use the following URLs:

- **Frontend (Phaser.js UI):**  
  [http://localhost](http://localhost) (Served via Nginx)

- **Backend API (Django, with Swagger/OpenAPI docs):**  
  [http://localhost:8008](http://localhost:8008)  

- **Database Admin (phpMyAdmin):**  
  [http://localhost:8088](http://localhost:8088)  

- **Static & Media Files:**  
  - Static assets: Served via Nginx  
  - Media uploads: [http://localhost/media](http://localhost/media)  

- **Database (MariaDB):**  
  Accessible on port `3307` (Containerized, use phpMyAdmin or local client)

*Note:* If you've changed ports in `docker-compose.yml`, adjust the URLs accordingly.

## TGA Integration

The platform integrates with **Training.gov.au (TGA)** to sync training packages, elements, qualifications, and performance criteria. It supports:
- **Automated API sync** for real-time updates
- **Local XML processing** for archived datasets
- **Admin tools** for manual data management

For more details, see [TGA Integration Documentation](docs/technical/tga_integration.md).

## Troubleshooting

If you run into Docker issues, try:
```sh
docker-compose down --volumes
docker ps -a
docker container prune -f
```

## Roadmap

Future enhancements include:
- **Streamlit dashboards** for data visualization
- **Gamification mechanics** integrated with Phaser.js
- **SCORM tracking** for adaptive learning analytics
- **Performance monitoring with Grafana/Prometheus**
- **ELK stack** for logging and debugging insights

