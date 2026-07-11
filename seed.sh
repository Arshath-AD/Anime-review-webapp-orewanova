#!/usr/bin/env bash
set -e

echo "Starting the MongoDB database seeder..."

# Check if the container is running
if ! docker ps | grep -q "orewa-web"; then
  echo "Error: The orewa-web container is not running. Please start the application with 'docker compose up -d' first."
  exit 1
fi

# Run the Python seed script inside the Docker container
echo "Running seed_data.py inside orewa-web..."
docker exec -it orewa-web python seed_data.py

echo "Database seeding process finished."
