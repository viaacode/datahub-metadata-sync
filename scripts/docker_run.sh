# work in progress, still need to add env vars here
docker container run \
  --env MEDIAHAVEN_USER=test \
  -p 8080:8080 \
  --rm --name "vkc_test" airflow_vkc

