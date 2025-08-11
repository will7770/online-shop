# Django online marketplace

My django pet project made to test myself and improve.

### Stack

Django 5 - main web framework and ORM
 
Celery - as a task queue

Redis - cache and session storage, also a host for celery

PostgreSQL - as the main database

### Installation
`git clone https://github.com/will7770/online-shop.git`


Fill `.env.example` with neccesary data and rename to `.env`

Proceed to project's directory

`cd online_shop`

If you want to send real emails, go to `online_shop/settings.py` and change EMAIL_BACKEND

Run with `docker-compose up -d --build`
