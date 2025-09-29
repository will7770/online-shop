# Django online marketplace

My django pet project made to test myself and improve.

### Stack

Django 5 - main web framework and ORM

Nginx and Gunicorn - reverse proxy and WSGI server
 
Celery - as a task queue

Redis - cache and session storage, also a host for celery

PostgreSQL - as the main database

### Installation and config
`git clone https://github.com/will7770/online-shop.git`


Create 2 files named `.env.docker` and `.env` by using `.env.example` as the template

Use `.env` for your local development needs and `.env.docker` for production

You can also change `gunicorn.conf.py`, to be fitting for your needs

If you want to send real emails, go to `online_shop/settings.py` and change EMAIL_BACKEND

### Running
Proceed to project's directory

`cd online_shop`

Run with `docker-compose up -d --build`