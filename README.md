<div align="left">

[![Foodgram workflow](https://github.com/Ivan-Grebennikov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Ivan-Grebennikov/foodgram-project-react/actions)
[![Deployed service link](https://img.shields.io/badge/Service-deployed-green.svg)](https://foodgram.ddnsking.com)

</div>

<div align="left">

[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![Gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

</div>

## Foodgram service

This is **Foodgram**, your smart food recipes organizer! :spaghetti::green_salad::sandwich:

This service may help you to find some tasty recipes, published by the community. You can add the most interesting ones in favourites and even create a shopping cart which will help you not to get lost in the market. Feel free to share you recipes with the community and subscribe to other users' dishy updates!

## Project start

### Prerequisites

The project is deployed in [Docker](https://www.docker.com/) containers.

You should [install](https://docs.docker.com/get-docker/) the Docker according to your OS and enviroment:

```
docker >= 20.10
docker compose >= 2.10.2
```

### Deployment

Clone the repo:

```
git clone https://github.com/Ivan-Grebennikov/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Go to startup scripts folder:

```
cd deploy
```

Create an ``` .env ``` settings file:

```
touch .env
```

Fill the ``` .env ``` using the sample below:

```
DEBUG=False # set debug or production mode (changeable)
DJANGO_SECRET_KEY='p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs' # django secret key (mandatory to change)
POSTGRES_USER=postgres # set database server login (changeable)
POSTGRES_PASSWORD=postgres # set database server password (mandatory to change)
POSTGRES_DB=postgres # set database name (changeable)
DB_HOST=db # the name of database Docker container
DB_PORT=5432 # default PostgreSQL server port
```

In ``` DEBUG=True ``` mode the project will use the SQLite database, regardless of the other settings.

You should generate your unique ``` DJANGO_SECRET_KEY ```using [this](https://djecrety.ir/) service.

``` DJANGO_SECRET_KEY ``` value should be wrapped in quotes.

Run the script to start the project:

```
./deploy.sh
```

The project will be started at

http://localhost/

To enter the admin zone you should open

http://localhost/admin/

And use an admin account:

```
Login: admin
Password: 1234567890
```

At the startup the service will be filled with some testing data (fixtures) - users, recipes, tags, etc.

## Start and stop

To stop the service you should run:

```
sudo docker compose down
```

To start the service again:

```
sudo docker compose up
```

### API

There is a REST API to work with the service.

Please see http://localhost/api/docs/redoc.html
