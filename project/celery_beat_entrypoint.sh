#!/bin/sh
cd /app/retail_api

# run a celery beat
exec gosu nobody:nogroup celery -A retail_api beat --loglevel=info