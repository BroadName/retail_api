#!/bin/sh
cd /app/retail_api
# run a worker :)
exec gosu nobody:nogroup celery -A retail_api worker --loglevel=info