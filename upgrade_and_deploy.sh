#!/usr/bin/env bash
set -e
source ./.env #import environment variables


echo "Check for updates on remote git repository."
git fetch
ahead_commits=$(git rev-list HEAD...origin/master --count)
# shellcheck disable=SC2071
if [[ $ahead_commits > 0 ]]
then
  echo "Pulling new updates."
  git pull
else
  echo "Already up to date."
  exit 0
fi

echo "Install Python dependencies."
./venv/bin/pip install -r requirements.txt

echo "Install NodeJS libraries."
npm ci --dev
npm audit fix

echo "Build js code."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Collect Django static."
./venv/bin/python3 manage.py collectstatic --noinput

echo "Apply Django migrations."
./venv/bin/python3 manage.py migrate --noinput

echo "Restart systemd services."
systemctl restart star-burger.service
systemctl restart postgresql.service
systemctl reload nginx.service

echo "Send deployment info to Rollbar."
sha=$(git rev-parse HEAD)
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "X-Rollbar-Access-Token: ${ROLLBAR_TOKEN}" \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
              {
                "environment": "'"${ROLLBAR_ENVIRONMENT}"'",
                "local_username": "'"${USER}"'",
                "revision": "'"${sha}"'",
                "status": "succeeded"
              }
            '

echo "Deployment completed!"
