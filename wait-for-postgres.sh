#!/bin/sh

# wait-for-postgres.sh

set -e

host="$POSTGRES_HOST"
port="$POSTGRES_PORT"

echo "Waiting for PostgreSQL at $host:$port..."

while ! nc -z "$host" "$port"; do
  sleep 1
done

echo "PostgreSQL is up — running migrations and server"
exec "$@"
