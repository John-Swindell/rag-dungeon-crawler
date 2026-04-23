# Alcatraz Icarus

Alcatraz Icarus is a cloud-native narrative dungeon crawler built as a CS 499 capstone portfolio project. The application reimagines a legacy Python text adventure as a deployed, API-driven system with procedural map generation, persistent game state, adversarial pathfinding, and AI-assisted storytelling.

The game places the player inside an Alcatraz-inspired escape scenario. Each session generates a unique prison layout, scatters escape components throughout the map, and challenges the player to collect every part before reaching the roof. After enough progress is made, Brutus, the Warden, leaves his office and begins hunting the player through the map using A* pathfinding.

## Engineering Focus

This project emphasizes production-oriented backend and platform engineering rather than a static front-end demo. The original monolithic script was decomposed into a FastAPI service with a browser-based interface, containerized runtime, automated tests, and infrastructure-as-code support for serverless deployment.

Key technical features include:

- Procedural BSP map generation that creates a different navigable dungeon layout for each session.
- Graph-based room traversal with A* search powering the Warden's pursuit behavior.
- JSON session state for player position, inventory, visited rooms, generated map data, and NPC state.
- MongoDB Atlas persistence with optional Atlas Vector Search for retrieval-augmented narrative context.
- Gemini-powered narrative updates that turn structured game events into cohesive Alcatraz-themed story text.
- Dockerized FastAPI deployment designed for small serverless containers that can scale down when idle.
- Terraform-managed cloud infrastructure for repeatable deployment of the API layer and runtime configuration.

## Capstone Context

The project demonstrates the full arc from software engineering fundamentals to modern platform architecture. It combines algorithms and data structures, database design, secure configuration management, cloud deployment, and AI integration into a single cohesive artifact.

The result is intentionally compact but production-shaped: the user sees a simple playable web game, while the backend exercises the same patterns used in larger distributed systems, including containerization, API boundaries, external persistence, managed secrets, vector retrieval, and automated infrastructure provisioning.
