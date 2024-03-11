from multiprocessing import Lock, Process
import json
import math
import requests
import re
from datetime import datetime
from fake_useragent import UserAgent
from loguru import logger
from shapely.geometry import Point, Polygon
import geopandas as gpd
import pandas as pd
from stem import Signal
from stem.control import Controller
import time
import os
import sys


logger.add(
    sink='collect_buildings.log',
    format="{time:YYYY-MM-DD HH:mm:ss!UTC} | {level} | {name}:{function}:{line} - {message}",
    level="INFO",
    backtrace=False,
    diagnose=True,
    catch=True)

poly_cols = ['coord', 'name', 'addr_country', 'addr_city', 'addr_street',
             'addr_housenumber', 'building', 'building_levels', 'type', 'geometry']


def list_filter(lst: list, c_num: int):
    n = math.ceil(len(lst) / c_num)
    for x in range(0, len(lst), n):
        e_c = lst[x: n + x]
        if len(e_c) < n:
            e_c = e_c + [None for y in range(n - len(e_c))]
        yield e_c


def collect_lonk(lat: float, lon: float, radius: int):
    return f'http://overpass-api.de/api/interpreter?data=[out:json][timeout:300];(way["building"](around:{radius},{lat},{lon});relation["building"](around:{radius},{lat},{lon}););out body;>;out skel qt;'


class CollectBuildings:
    def __init__(self, num_threads: int = 1, filename: str = 'start.csv', radius: int = 100, force: bool = True):
        """
        Collect buildings polygon by radius of points.
        :param num_threads: default value 10
        :param filename: default value start.csv (require columns lat, lon)
        :param radius: default 150
        :param force: default True ; if True use without different between existent file
        """
        self.num_threads = num_threads
        self.link_list = self.get_link_list(start_df=self._init_start_df(filename, force), num_threads=num_threads,
                                            radius=radius)
        self.lock = Lock()

    @staticmethod
    def _init_start_df(filename: str, force: bool):
        start_df = pd.read_csv(filename).dropna(subset=['lat', 'lon'])
        assert len(col := [x for x in ['lat', 'lon'] if
                           not any(xs == x for xs in start_df.columns)]) == 0, f'columns not exists {col}'
        start_df['coord'] = start_df['lat'].astype(str) + ',' + start_df['lon'].astype(str)
        if force is True:
            return start_df
        else:
            if not os.path.isfile('buildings.csv'):
                pd.DataFrame(columns=poly_cols).to_csv(f'buildings.csv', index=False)
            df_t = pd.read_csv('buildings.csv', usecols=['coord'])
            start_df = start_df[~start_df['coord'].isin(df_t['coord'])]
            return start_df

    @staticmethod
    def get_link_list(start_df: pd.DataFrame, num_threads: int, radius: int):
        link_list = []
        for lat, lon in zip(start_df['lat'], start_df['lon']):
            link_list.append(collect_lonk(lat=lat, lon=lon, radius=radius))
        return list(list_filter(link_list, num_threads))

    @staticmethod
    def get_proxy(num_thread: int):
        return {'https': f'socks5h://localhost:{9080 + int(num_thread)}',
                'http': f'socks5h://localhost:{9080 + int(num_thread)}'}

    @staticmethod
    def get_headers():
        return {'Accept': '*/*',
                'Connection': 'keep-alive',
                'User-Agent': UserAgent().safari}

    @staticmethod
    def new_ip(num_thread: int):
        port = 8148 + int(num_thread)
        controller = Controller.from_port(port=port)
        controller.authenticate(password='1234')
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())

    @staticmethod
    def _get_by_relation(relation: int):
        return requests.get(f'https://polygons.openstreetmap.fr/get_wkt.py?id={relation}').text.replace('SRID=4326;',
                                                                                                        '')

    @staticmethod
    def _get_geom_nodes(row: pd.Series, cords: pd.DataFrame):
        b = pd.DataFrame({'id': row['nodes']}).merge(cords[['geometry', 'id']], 'left', 'id')
        try:
            row['geometry'] = Polygon(b['geometry'])
        except Exception as e:
            logger.error(e)
        return row

    def check_conn(self, num_thread: int):
        count = 0
        while True:
            try:
                if count > 50:
                    logger.info(f"CAN'T LOAD TEST PAGE FOR WORKER # {num_thread} ---- > {count} times")
                    return False
                if requests.get(url='http://httpbin.org/ip', proxies=self.get_proxy(num_thread),
                                headers=self.get_headers(), timeout=30).status_code == 200:
                    logger.info(f'connection established for worker # {num_thread} by {count} cycles')
                    return True
            except Exception as e:
                # logger.error(f'bad conn for worker # {num_thread} for {count} because of {type(e)}')
                self.new_ip(num_thread=num_thread)
                count += 1

    def start_collect(self):
        start = datetime.now()
        procs = []
        if self.check_conn(num_thread=0) is False:
            return None
        logger.info(f'your ip is ---> {requests.get("http://ident.me", proxies=self.get_proxy(0), timeout=10).text}')
        logger.info(f'job shape per worker: {len(self.link_list[0])}')
        for num_thread in range(self.num_threads):
            p = Process(target=self.parallel, args=(num_thread, self.link_list[num_thread]))
            procs.append(p)
            p.start()
        try:
            for pr in procs:
                pr.join()
        finally:
            for pr in procs:
                pr.kill()
        logger.info(f'time ela {datetime.now() - start}')

    def get_polygon(self, q: json, link: str):
        a = pd.DataFrame(q['elements'])
        cords = a[a['lon'].notna()]
        ids = []
        if (rel := a[a['type'] == 'relation']).shape[0] != 0:
            for item in rel['members']:
                ids += pd.json_normalize(item)['ref'].to_list()
        a = pd.json_normalize(q['elements'])
        a['geometry'] = None
        b = a.loc[a['type'] == 'relation'].drop('type', axis=1)
        b['geometry'] = b['id'].map(lambda x: self._get_by_relation(x))
        a = a.loc[(a['type'] != 'relation') & (a['nodes'].notna()) & (~a['id'].isin(ids))].drop('type', axis=1)
        #
        cords = gpd.GeoDataFrame(cords, geometry=gpd.points_from_xy(cords['lon'], cords['lat']))
        a = a.apply(lambda x: self._get_geom_nodes(x, cords), axis=1)
        #
        a = pd.concat([b, a])
        a.columns = [x.replace('tags.', '').replace(':', '_') for x in a.columns]
        a['coord'] = re.search(r'(\d+[.]\d+[,]\d+[.]\d+)', link).group(1)
        #
        return pd.concat([a, pd.DataFrame(columns=poly_cols)]).reset_index(drop=True)[poly_cols]

    def parallel(self, num_thread: int, links_list: list):
        percent_dict = {int(len(links_list) * (x / 100)): x for x in [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 105]}
        # logger.info(f'process # {num_thread} start')
        if self.check_conn(num_thread) is False:
            return None
        for ind, link in enumerate(links_list):
            # logger.info(f'worker # {num_thread} do {ind} job')
            if ind == list(percent_dict.keys())[0]:
                logger.info(f'worker # {num_thread} done {percent_dict[ind]} %')
                percent_dict.pop(ind)
            headers, proxy = self.get_headers(), self.get_proxy(num_thread)
            count = 0
            while count < 3:
                try:
                    response = requests.get(url=link, proxies=proxy, headers=headers, timeout=30)
                    if response.status_code != 200 or 'quota of your IP address' in response.text:
                        logger.error(f'QUOTA ERROR FOR WORKER # {num_thread}')
                        raise Exception('bad ip')
                    break
                except:
                    count += 1
                    logger.info(f'new proxy for worker # {num_thread}')
                    if self.check_conn(num_thread) is False:
                        return None
                    headers = self.get_headers()
            try:
                b = json.loads(response.text)
                if len(b['elements']) == 0:
                    # logger.info(f'no elements by worker # {num_thread}')
                    continue
                df = self.get_polygon(b, link)
                if df.shape[0] != 0:
                    self.lock.acquire()
                    if os.path.isfile('buildings.csv'):
                        df.to_csv(f'buildings.csv', mode='a', index=False, header=False)
                    else:
                        df.to_csv(f'buildings.csv', index=False)
                    self.lock.release()
            except Exception as e:
                # if 'Expecting value' not in str(e):
                print(e)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        num_threads = sys.argv[1]
    else:
        num_threads = 10
    logger.info(f'Collect with {sys.argv[1]} thread numbers')
    c_b = CollectBuildings(num_threads=num_threads, filename='start.csv', radius=150, force=False)
    c_b.start_collect()
