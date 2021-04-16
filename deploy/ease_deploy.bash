#!/usr/bin/bash

sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl

pip3 install virtualenv

virtualenv ../venv

source ../venv/bin/activate

pip3 install -r ../requirements.txt
pip3 install gunicorn

cd ../backend

mkdir ./app/migrations
touch ./app/migrations/__init__.py


python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

cp ../deploy/gunicorn.service /etc/systemd/system/gunicorn.service
cp ../deploy/post_generator_backend ln -s /etc/nginx/sites-available/post_generator_backend


sudo systemctl restart gunicorn
sudo systemctl enable gunicorn
sudo ln -s /etc/nginx/sites-available/post_generator_backend /etc/nginx/sites-enabled
sudo systemctl restart nginx
