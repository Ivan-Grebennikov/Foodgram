#!/bin/bash

sudo docker compose pull
sudo docker compose up -d
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py loaddata /data/fixtures.json
sudo docker compose exec backend python manage.py load_fixture_related_images
sudo docker compose exec backend python manage.py collectstatic --no-input 
