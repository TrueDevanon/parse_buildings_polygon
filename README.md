# Collect the buildings polygon by bbox or radius of points.

Multithreaded collecting the building's polygon by a bbox or radius of points from OpenStreetMap using the Tor network.

Generate a file with a grid of points **start.csv** by passing the lower and upper corner coordinates of the area your want to _create_grid_points.py_ script. (for additional settings check the script)

### Build Docker container by command:

`docker build -t collect_buildings .`

### Run container, where last argument = number of threads: (default 10)

`docker run  --mount type=bind,source="$(pwd)",target=/parse -it collect_buildings 10`

At finish returns csv file **buildings.csv** :

|     id | coord| name| addr_country| addr_city| addr_street | addr_housenumber| building|building_levels |type | geometry |
|-------:|:------------------------------------|:-------------------------|:---------------|:------------|:-------------------------|:-------------------|:-----------|------------------:|-------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 119720 | 51.20504783722172,71.3654322625341  | nan | KZ| 2| улица Мыржакыпа Дулатова | 184| apartments |nan | nan | POLYGON ((71.3635963 51.2045634, 71.3634247 51.204615, 71.3630761 51.2041598, 71.3632477 51.2041082, 71.3635963 51.2045634))|
| 134198 | 51.16010816633189,71.45828474462733 | nan | KZ| Astana | улица Жанибека Тархана| 17 | yes|nan | nan | POLYGON ((71.4564745 51.1591407, 71.4565665 51.1592523, 71.457176 51.1590574, 71.4572363 51.1590716, 71.4575531 51.1594557, 71.4577342 51.1593961, 71.4573796 51.1589628, 71.457176 51.1589164, 71.4564745 51.1591407))  |
| 373674 | 51.19156593595477,71.32543427024778 | nan | KZ| Astana | улица Жанаконыс  | 9  | yes|nan | nan | POLYGON ((71.3258695 51.1906021, 71.3259925 51.1907056, 71.3262029 51.1906074, 71.32608 51.1905039, 71.3258695 51.1906021)) |
|  47203 | 51.12775160329121,71.4168582526165  | ForteBank| KZ| Astana | улица Достык| 8/1| yes| 6 | nan | POLYGON ((71.4189392 51.1266585, 71.418682 51.1259721, 71.4180728 51.126076, 71.4183437 51.1268586, 71.4182022 51.1268702, 71.4182415 51.1270772, 71.4190596 51.1269572, 71.4189392 51.1266585)) |
|  67446 | 51.13584074405138,71.41257275344297 | Hilton Garden Inn Astana | KZ| Astana | проспект Кабанбай Батыра | 15 | hotel | 8 | nan | POLYGON ((71.4144869 51.1357399, 71.4141199 51.1348003, 71.4138603 51.1348403, 71.414049 51.1353235, 71.4139316 51.1353416, 71.4140645 51.1356818, 71.4141704 51.1356655, 71.4142158 51.1357817, 71.4144869 51.1357399)) |

