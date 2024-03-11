# Collect buildings polygon by radius of points.

Pass csv file with name "start.csv" with columns lat, lon.

### Build Docker container by command:

`docker build -t collect_buildings .`

### Run container, where last argument = number of threads:

`docker run  --mount type=bind,source="$(pwd)",target=/parse -it collect_buildings 10`

