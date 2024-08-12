import numpy as np
import pandas as pd
from tqdm import tqdm
import sys

from collect_building import logger


class CreateGridPoints:
    def __init__(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float, step: int = 200,
                 filename: str = 'start.csv', type: str = 'boundary'):
        """
        Generate grid of points and save it to start.csv

        :param lat_min: float
        :param lat_max: float
        :param lng_min: float
        :param lng_max: float
        :param step: grid step in meters
        :param type: boundary or radius
        """
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lng_min = lng_min
        self.lng_max = lng_max
        self.step = self.step_radian(step=step, lat_min=lat_min)
        self.grid = self.create_grid(type=type)
        self.save_csv(filename=filename)

    @staticmethod
    def step_radian(step: int, lat_min: float):
        return [step / 110540, step * np.sin(90) / (111320 * np.cos(np.radians(lat_min)))]

    def lat_calc(self, lat: float):
        return lat + self.step[0]

    def lng_calc(self, lat: float, lng: float):
        return lng + self.step[1]

    def create_grid(self, type: str):
        def append():
            if type == 'boundary':
                grid.append([f"{lat}, {lng}", f"{n_lat}, {n_lng}"])
            elif type == 'radius':
                grid.append([lat, n_lng])

        grid = []
        logger.info(f'Number of steps ~ {np.ceil((self.lat_max - self.lat_min) / self.step[0])}')
        progress = tqdm()
        lat, lng = self.lat_min, self.lng_min
        while lat <= self.lat_max:
            while lng <= self.lng_max:
                n_lat = self.lat_calc(lat=lat)
                n_lng = self.lng_calc(lat=lat, lng=lng)
                append()
                lng = n_lng
                progress.update()
            lat = self.lat_calc(lat=lat)
            lng = self.lng_min
        return grid

    def save_csv(self, filename: str):
        pd.DataFrame(self.grid, columns=['lat', 'lon']).to_csv(filename, index=False)

    def convert_boundary_to_radius(self):
        self.grid = [x[:2] for x in self.grid]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        lat_min, lat_max, lng_min, lng_max = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(
            sys.argv[4])
        cgp = CreateGridPoints(lat_min, lat_max, lng_min, lng_max, step=200, filename='start.csv', type='boundary')
