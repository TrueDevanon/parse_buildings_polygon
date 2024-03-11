# Collect buildings polygon by radius of points.

Multithreaded collecting the building polygon by a radius of points from OpenStreetMap using the Tor network.

Pass csv file with name **start.csv** with columns lat, lon.

Return csv file **buildings.csv** with columns:
`coord, name, addr_country, addr_city, addr_street, addr_housenumber, building, building_levels, type, geometry`

### Build Docker container by command:

`docker build -t collect_buildings .`

### Run container, where last argument = number of threads:

`docker run  --mount type=bind,source="$(pwd)",target=/parse -it collect_buildings 10`
