#!/bin/sh
cd /app/retail_api

# run a flower
exec gosu nobody:nogroup celery -A retail_api flower --port=5555