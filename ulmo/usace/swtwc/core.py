import cStringIO as StringIO
import datetime
import os.path

from bs4 import BeautifulSoup
import numpy as np
import pandas

from ulmo import util

USACE_SWTWC_DIR = os.path.join(util.get_ulmo_dir(), 'usace/swtwc')


def get_station_data(station_code, date=None, as_dataframe=False):
    station_dict = {}

    if date is None:
        date_str = 'current'
        year = datetime.date.today().year
    else:
        date = util.parse_datestr(date)
        date_str = date.strftime('%Y%m%d')
        year = date.year

    filename = '%s.%s.html'% (station_code, date_str)
    data_url = 'http://www.swt-wc.usace.army.mil/webdata/gagedata/' + filename
    path = os.path.join(USACE_SWTWC_DIR, filename)

    with util.open_file_for_url(data_url, path) as f:
        soup = BeautifulSoup(f)
        pre = soup.find('pre')
        sio = StringIO.StringIO(pre.text.strip())

    first_line = sio.readline()
    split = first_line[8:].strip().split()

    station_dict['code'] = split[0]
    station_dict['description'] = ' '.join(split[1:])

    second_line = sio.readline()
    station_dict['station_type'] = second_line.strip().split(':')[1].strip()

    notes = []

    while 1:
        next_line = sio.readline()
        if ':' in next_line:
            notes.append(next_line.strip())
        else:
            break

    if len(notes):
        station_dict['notes'] = '\n'.join(notes)

    variable_names = _split_line(sio.readline()[15:], 10)
    variable_units = _split_line(sio.readline()[15:], 10)
    variable_sources = _split_line(sio.readline()[15:], 10)

    station_dict['variables'] = dict([
        (name, {'unit': unit, 'source': source})
        for name, unit, source in zip(variable_names, variable_units,
            variable_sources)
    ])

    station_dict['timezone'] = sio.readline().strip().strip('()')
    column_names = ['datetime'] + variable_names
    widths = [15] + ([10] * len(variable_names))
    converters = dict([
        (variable_name, lambda x: float(x))
        for variable_name in variable_names
    ])
    date_parser = lambda x: _convert_datetime(x, year)
    dataframe = pandas.read_fwf(sio, names=column_names, widths=widths,
            index_col=['datetime'], converters=converters, parse_dates=True,
            date_parser=date_parser)

    if as_dataframe:
        station_dict['values'] = dataframe
    else:
        station_dict['values'] = util.dict_from_dataframe(dataframe)

    return station_dict


def get_stations():
    stations_url = 'http://www.swt-wc.usace.army.mil/shefids.htm'
    path = os.path.join(USACE_SWTWC_DIR, 'shefids.htm')

    with util.open_file_for_url(stations_url, path) as f:
        soup = BeautifulSoup(f)
        pre = soup.find('pre')
        links = pre.find_all('a')
        stations = [
            _parse_station_link(link) for link in links
        ]

    return dict([
        (station['code'], station)
        for station in stations
    ])


def _convert_datetime(s, year):
    fmt = '%m/%d %H:%M'
    return datetime.datetime.strptime(s, fmt).replace(year=year)


def _split_line(line, n):
    return [line[i:i+n].strip() for i in range(0, len(line), n)][:-1]


def _parse_station_link(link):
    return {
        'code': link.text,
        'description': link.next_sibling.strip(),
    }


def _to_underscore(spaced):
    return spaced.sub(' ', '_').sub('(', '').sub(')', '').lower()
