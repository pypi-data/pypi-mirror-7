from datetime import datetime
import json
import os
import shutil
from six import StringIO
from six.moves import configparser
import sys
import tempfile
import textwrap
from unittest import TestCase, skipIf, skipUnless

if sys.platform != 'win32':
    import numpy as np
    from osgeo import ogr, gdal
    from pthelma.spatial import idw, integrate, TimeseriesCache, \
        create_ogr_layer_from_stations, h_integrate, BitiaApp, WrongValueError
    skip_osgeo = False
    skip_osgeo_message = ''
else:
    skip_osgeo = True
    skip_osgeo_message = 'Not available on Windows'

from pthelma import enhydris_api
from pthelma.timeseries import Timeseries


def add_point_to_layer(layer, x, y, value):
    p = ogr.Geometry(ogr.wkbPoint)
    p.AddPoint(x, y)
    f = ogr.Feature(layer.GetLayerDefn())
    f.SetGeometry(p)
    f.SetField('value', value)
    layer.CreateFeature(f)


@skipIf(skip_osgeo, skip_osgeo_message)
class IdwTestCase(TestCase):

    def setUp(self):
        self.point = ogr.Geometry(ogr.wkbPoint)
        self.point.AddPoint(5.1, 2.5)

        self.data_source = ogr.GetDriverByName('memory').CreateDataSource(
            'tmp')
        self.data_layer = self.data_source.CreateLayer('test')
        self.data_layer.CreateField(ogr.FieldDefn('value', ogr.OFTReal))

    def tearDown(self):
        self.data_layer = None
        self.data_source = None
        self.point = None

    def test_idw_single_point(self):
        add_point_to_layer(self.data_layer, 5.3, 6.4, 42.8)
        self.assertAlmostEqual(idw(self.point, self.data_layer), 42.8)

    def test_idw_three_points(self):
        add_point_to_layer(self.data_layer, 6.4, 7.8, 33.0)
        add_point_to_layer(self.data_layer, 9.5, 7.4, 94.0)
        add_point_to_layer(self.data_layer, 7.1, 4.9, 67.7)
        self.assertAlmostEqual(idw(self.point, self.data_layer),
                               64.090, places=3)
        self.assertAlmostEqual(idw(self.point, self.data_layer, alpha=2.0),
                               64.188, places=3)

    def test_idw_point_with_nan(self):
        add_point_to_layer(self.data_layer, 6.4, 7.8, 33.0)
        add_point_to_layer(self.data_layer, 9.5, 7.4, 94.0)
        add_point_to_layer(self.data_layer, 7.1, 4.9, 67.7)
        add_point_to_layer(self.data_layer, 7.2, 5.4, float('nan'))
        self.assertAlmostEqual(idw(self.point, self.data_layer),
                               64.090, places=3)
        self.assertAlmostEqual(idw(self.point, self.data_layer, alpha=2.0),
                               64.188, places=3)


@skipIf(skip_osgeo, skip_osgeo_message)
class IntegrateTestCase(TestCase):

    def setUp(self):
        # We will test on a 7x15 grid
        self.mask = np.zeros((7, 15), np.int8)
        self.mask[3, 3] = 1
        self.mask[6, 14] = 1
        self.mask[4, 13] = 1
        self.dataset = gdal.GetDriverByName('mem').Create('test', 15, 7, 1,
                                                          gdal.GDT_Byte)
        self.dataset.GetRasterBand(1).WriteArray(self.mask)

        # Prepare the result band
        self.dataset.AddBand(gdal.GDT_Float32)
        self.target_band = self.dataset.GetRasterBand(self.dataset.RasterCount)

        # Our grid represents a 70x150m area, lower-left co-ordinates (0, 0).
        self.dataset.SetGeoTransform((0, 10, 0, 70, 0, -10))

        # Now the data layer, with three points
        self.data_source = ogr.GetDriverByName('memory').CreateDataSource(
            'tmp')
        self.data_layer = self.data_source.CreateLayer('test')
        self.data_layer.CreateField(ogr.FieldDefn('value', ogr.OFTReal))
        add_point_to_layer(self.data_layer,  75.2, 10.7, 37.4)
        add_point_to_layer(self.data_layer, 125.7, 19.0, 24.0)
        add_point_to_layer(self.data_layer,   9.8, 57.1, 95.4)

    def tearDown(self):
        self.data_source = None
        self.raster = None

    def test_integrate_idw(self):
        integrate(self.dataset, self.data_layer, self.target_band, idw)
        result = self.target_band.ReadAsArray()

        # All masked points and only those must be NaN
        # (^ is bitwise xor in Python)
        self.assertTrue((np.isnan(result) ^ (self.mask != 0)).all())

        self.assertAlmostEqual(result[3, 3],  62.971, places=3)
        self.assertAlmostEqual(result[6, 14], 34.838, places=3)
        self.assertAlmostEqual(result[4, 13], 30.737, places=3)


@skipIf(skip_osgeo, skip_osgeo_message)
@skipUnless(os.getenv('PTHELMA_TEST_ENHYDRIS_API'),
            'set PTHELMA_TEST_ENHYDRIS_API')
class CreateOgrLayerFromStationsTestCase(TestCase):

    def setUp(self):
        # Create two stations, each one with a time series
        self.parms = json.loads(os.getenv('PTHELMA_TEST_ENHYDRIS_API'))
        self.cookies = enhydris_api.login(self.parms['base_url'],
                                          self.parms['user'],
                                          self.parms['password'])
        self.station1_id = enhydris_api.post_model(
            self.parms['base_url'], self.cookies, 'Station',
            {'name': 'station1',
             'srid': 4326,
             'point': 'POINT (23.78743 37.97385)',
             'copyright_holder': 'Joe User',
             'copyright_years': '2014',
             'stype': 1,
             'owner': self.parms['owner_id'],
             })
        self.timeseries1_id = enhydris_api.post_model(
            self.parms['base_url'], self.cookies, 'Timeseries',
            {'gentity': self.station1_id,
             'variable': self.parms['variable_id'],
             'unit_of_measurement': self.parms['unit_of_measurement_id'],
             'time_zone': self.parms['time_zone_id']})
        self.station2_id = enhydris_api.post_model(
            self.parms['base_url'], self.cookies, 'Station',
            {'name': 'station1',
             'srid': 4326,
             'point': 'POINT (24.56789 38.76543)',
             'copyright_holder': 'Joe User',
             'copyright_years': '2014',
             'stype': 1,
             'owner': self.parms['owner_id'],
             })
        self.timeseries2_id = enhydris_api.post_model(
            self.parms['base_url'], self.cookies, 'Timeseries',
            {'gentity': self.station2_id,
             'variable': self.parms['variable_id'],
             'unit_of_measurement': self.parms['unit_of_measurement_id'],
             'time_zone': self.parms['time_zone_id']})

        # Temporary directory for cache files
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        enhydris_api.delete_model(self.parms['base_url'], self.cookies,
                                  'Station', self.station1_id)
        enhydris_api.delete_model(self.parms['base_url'], self.cookies,
                                  'Station', self.station2_id)

    def test_create_ogr_layer_from_stations(self):
        data_source = ogr.GetDriverByName('memory').CreateDataSource('tmp')
        group = [{'base_url': self.parms['base_url'],
                  'user': self.parms['user'],
                  'id': self.timeseries1_id},
                 {'base_url': self.parms['base_url'],
                  'user': self.parms['user'],
                  'id': self.timeseries2_id}]
        layer = create_ogr_layer_from_stations(group, 2100, data_source,
                                               TimeseriesCache(self.tempdir,
                                                               []))
        self.assertTrue(layer.GetFeatureCount(), 2)
        # The co-ordinates below are converted from WGS84 to Greek Grid/GGRS87
        ref = [{'x': 481180.63, 'y': 4202647.01,  # 23.78743, 37.97385
                'timeseries_id': self.timeseries1_id},
               {'x': 549187.44, 'y': 4290612.25,  # 24.56789, 38.76543
                'timeseries_id': self.timeseries2_id},
               ]
        for feature, r in zip(layer, ref):
            self.assertEqual(feature.GetField('timeseries_id'),
                             r['timeseries_id'])
            self.assertAlmostEqual(feature.GetGeometryRef().GetX(), r['x'], 2)
            self.assertAlmostEqual(feature.GetGeometryRef().GetY(), r['y'], 2)


@skipIf(skip_osgeo, skip_osgeo_message)
@skipUnless(os.getenv('PTHELMA_TEST_ENHYDRIS_API'),
            'set PTHELMA_TEST_ENHYDRIS_API')
class TimeseriesCacheTestCase(TestCase):
    test_timeseries1 = textwrap.dedent("""\
                                   2014-01-01 08:00,11,
                                   2014-01-02 08:00,12,
                                   2014-01-03 08:00,13,
                                   2014-01-04 08:00,14,
                                   2014-01-05 08:00,15,
                                   """)
    test_timeseries2 = textwrap.dedent("""\
                                   2014-07-01 08:00,9.11,
                                   2014-07-02 08:00,9.12,
                                   2014-07-03 08:00,9.13,
                                   2014-07-04 08:00,9.14,
                                   2014-07-05 08:00,9.15,
                                   """)
    timeseries1_top = ''.join(test_timeseries1.splitlines(True)[:-1])
    timeseries2_top = ''.join(test_timeseries2.splitlines(True)[:-1])
    timeseries1_bottom = test_timeseries1.splitlines(True)[-1]
    timeseries2_bottom = test_timeseries2.splitlines(True)[-1]

    def setUp(self):
        self.parms = json.loads(os.getenv('PTHELMA_TEST_ENHYDRIS_API'))
        self.cookies = enhydris_api.login(self.parms['base_url'],
                                          self.parms['user'],
                                          self.parms['password'])

        # Create two time series
        j = {
            'gentity': self.parms['station_id'],
            'variable': self.parms['variable_id'],
            'unit_of_measurement': self.parms['unit_of_measurement_id'],
            'time_zone': self.parms['time_zone_id'],
            'time_step': 3,
            'actual_offset_minutes': 0,
            'actual_offset_months': 0,
        }
        self.ts1_id = enhydris_api.post_model(
            self.parms['base_url'], self.cookies, 'Timeseries', j)
        self.ts2_id = enhydris_api.post_model(
            self.parms['base_url'], self.cookies, 'Timeseries', j)
        assert self.ts1_id != self.ts2_id

        # Add some data (all but the last record) to the database
        ts = Timeseries(self.ts1_id)
        ts.read(StringIO(self.timeseries1_top))
        enhydris_api.post_tsdata(self.parms['base_url'], self.cookies, ts)
        ts = Timeseries(self.ts2_id)
        ts.read(StringIO(self.timeseries2_top))
        enhydris_api.post_tsdata(self.parms['base_url'], self.cookies, ts)

        # Temporary directory for cache files
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_update(self):
        self.parms = json.loads(os.getenv('PTHELMA_TEST_ENHYDRIS_API'))
        timeseries_group = [{'base_url': self.parms['base_url'],
                             'id': self.ts1_id,
                             'user': self.parms['user'],
                             'password': self.parms['password'],
                             },
                            {'base_url': self.parms['base_url'],
                             'id': self.ts2_id,
                             'user': self.parms['user'],
                             'password': self.parms['password'],
                             },
                            ]
        # Cache the two timeseries
        cache = TimeseriesCache(self.tempdir, timeseries_group)
        cache.update()

        # Check that the cached stuff is what it should be
        file1, file2 = [cache.get_filename(self.parms['base_url'], x)
                        for x in (self.ts1_id, self.ts2_id)]
        with open(file1) as f:
            self.assertEqual(f.read().replace('\r', ''), self.timeseries1_top)
        with open(file2) as f:
            self.assertEqual(f.read().replace('\r', ''), self.timeseries2_top)
        with open(file1 + '_step') as f:
            self.assertEqual(f.read(), '3')
        with open(file2 + '_step') as f:
            self.assertEqual(f.read(), '3')

        # Append a record to the database for each timeseries
        ts = Timeseries(self.ts1_id)
        ts.read(StringIO(self.timeseries1_bottom))
        enhydris_api.post_tsdata(self.parms['base_url'], self.cookies, ts)
        ts = Timeseries(self.ts2_id)
        ts.read(StringIO(self.timeseries2_bottom))
        enhydris_api.post_tsdata(self.parms['base_url'], self.cookies, ts)

        # Update the cache
        cache.update()

        # Check that the cached stuff is what it should be
        file1, file2 = [cache.get_filename(self.parms['base_url'], x)
                        for x in (self.ts1_id, self.ts2_id)]
        with open(file1) as f:
            self.assertEqual(f.read().replace('\r', ''), self.test_timeseries1)
        with open(file2) as f:
            self.assertEqual(f.read().replace('\r', ''), self.test_timeseries2)


@skipIf(skip_osgeo, skip_osgeo_message)
class HIntegrateTestCase(TestCase):
    """
    We will test on a 4x3 raster:

                        ABCD
                       1
                       2
                       3

    There will be three stations: two will be exactly at the center of
    gridpoints A3 and B3, and one will be slightly outside the grid (somewhere
    in E2). We assume the bottom left corner of A3 to have co-ordinates (0, 0)
    and the gridpoint to be 10 km across. We also consider C1 to be masked out.
    """
    data = [{'base_url': 'http://irrelevant.gr/',
             'id': 1234,
             'user': '',
             'password': '',
             'data': textwrap.dedent("""\
                                     2014-04-22 12:50,5.03,
                                     2014-04-22 13:00,0.54,
                                     2014-04-22 13:10,6.93,
                                     """),
             'point': 'POINT (19.55729 0.04733)',  # GGRS87=5000.00 5000.00
             },
            {'base_url': 'http://irrelevant.gr/',
             'id': 1235,
             'user': '',
             'password': '',
             'data': textwrap.dedent("""\
                                     2014-04-22 12:50,2.90,
                                     2014-04-22 13:00,2.40,
                                     2014-04-22 13:10,9.16,
                                     """),
             'point': 'POINT (19.64689 0.04734)',  # GGRS87=15000.00 5000.00
             },
            {'base_url': 'http://irrelevant.gr/',
             'id': 1236,
             'user': '',
             'password': '',
             'data': textwrap.dedent("""\
                                     2014-04-22 12:50,9.70,
                                     2014-04-22 13:00,1.84,
                                     2014-04-22 13:10,7.63,
                                     """),
             'point': 'POINT (19.88886 0.12857)',  # GGSRS87=42000.00 14000.00
             },
            {'base_url': 'http://irrelevant.gr/',
             'id': 1237,
             'user': '',
             'password': '',
             # This station is missing the date required,
             # so it should not be taken into account
             'data': textwrap.dedent("""\
                                     2014-04-22 12:50,9.70,
                                     2014-04-22 13:10,7.63,
                                     """),
             'point': 'POINT (19.66480 0.15560)',  # GGRS87=17000.00 17000.00
             },
            ]

    def write_data_to_cache(self):
        self.cache = TimeseriesCache(self.tempdir, [])
        for item in self.data:
            point_filename = self.cache.get_point_filename(item['base_url'],
                                                           item['id'])
            with open(point_filename, 'w') as f:
                f.write(item['point'])
            ts_cache_filename = self.cache.get_filename(item['base_url'],
                                                        item['id'])
            with open(ts_cache_filename, 'w') as f:
                f.write(item['data'])

    def create_mask(self):
        mask_array = np.ones((3, 4), np.int8)
        mask_array[0, 2] = 0
        self.mask = gdal.GetDriverByName('mem').Create('mask', 4, 3, 1,
                                                       gdal.GDT_Byte)
        self.mask.SetGeoTransform((0, 10000, 0, 30000, 0, -10000))
        self.mask.GetRasterBand(1).WriteArray(mask_array)

    def setUp(self):
        # Temporary directory for cache files
        self.tempdir = tempfile.mkdtemp()

        self.write_data_to_cache()
        self.create_mask()
        self.stations = ogr.GetDriverByName('memory').CreateDataSource('tmp')
        self.stations_layer = create_ogr_layer_from_stations(
            self.data, 2100, self.stations, self.cache)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_h_integrate(self):
        h_integrate(group=self.data, mask=self.mask,
                    stations_layer=self.stations_layer,
                    cache=TimeseriesCache(self.tempdir, []),
                    date=datetime(2014, 4, 22, 13, 0), output_dir=self.tempdir,
                    filename_prefix='test', date_fmt='%Y-%m-%d-%H-%M',
                    funct=idw, kwargs={})
        f = gdal.Open(os.path.join(self.tempdir, 'test-2014-04-22-13-00.tif'))
        result = f.GetRasterBand(1).ReadAsArray()
        expected_result = np.array([[1.5088, 1.6064, np.nan, 1.7237],
                                    [1.3828, 1.6671, 1.7336, 1.7662],
                                    [0.5400, 2.4000, 1.7954, 1.7504]])
        np.testing.assert_almost_equal(result, expected_result, decimal=4)


@skipIf(skip_osgeo, skip_osgeo_message)
class BitiaAppTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(BitiaAppTestCase, self).__init__(*args, **kwargs)

        # Python 2.7 compatibility
        try:
            self.assertRaisesRegex
        except AttributeError:
            self.assertRaisesRegex = self.assertRaisesRegexp

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.tempdir, 'cache')
        self.output_dir = os.path.join(self.tempdir, 'output')
        self.config_file = os.path.join(self.tempdir, 'bitia.conf')
        os.mkdir(self.cache_dir)
        os.mkdir(self.output_dir)
        self.mask_file = os.path.join(self.tempdir, 'mask.tif')
        self.saved_argv = sys.argv
        sys.argv = ['bitia', '--traceback', self.config_file]

        # Prepare a configuration file (some tests override it)
        with open(self.config_file, 'w') as f:
            f.write(textwrap.dedent('''\
                [General]
                mask = {0.mask_file}
                epsg = 2100
                cache_dir = {0.cache_dir}
                output_dir = {0.output_dir}
                filename_prefix = rainfall
                files_to_keep = 24
                method = idw

                [ntua]
                base_url = wrongproto://openmeteo.org/
                id = 6539

                [nedontas]
                base_url = wrongproto://openmeteo.org/
                id = 9356
                ''').format(self))

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        sys.argv = self.saved_argv

    def test_correct_configuration(self):
        application = BitiaApp()
        application.run(dry=True)

    def test_wrong_configuration1(self):
        with open(self.config_file, 'w') as f:
            f.write(textwrap.dedent('''\
                [General]
                mask = {0.mask_file}
                epsg = 2100
                cache_dir = {0.cache_dir}
                output_dir = {0.output_dir}
                filename_prefix = rainfall
                method = idw
                ''').format(self))
        application = BitiaApp()
        self.assertRaisesRegex(configparser.Error, 'files_to_keep',
                               application.run)

    def test_wrong_configuration2(self):
        with open(self.config_file, 'w') as f:
            f.write(textwrap.dedent('''\
                [General]
                mask = {0.mask_file}
                epsg = 2100
                cache_dir = {0.cache_dir}
                output_dir = {0.output_dir}
                filename_prefix = rainfall
                files_to_keep = 24
                method = idw
                nonexistent_option = irrelevant
                ''').format(self))
        application = BitiaApp()
        self.assertRaisesRegex(configparser.Error, 'nonexistent_option',
                               application.run)

    def test_wrong_configuration3(self):
        with open(self.config_file, 'w') as f:
            f.write(textwrap.dedent('''\
                [General]
                mask = {0.mask_file}
                epsg = 2100
                cache_dir = {0.cache_dir}
                output_dir = {0.output_dir}
                filename_prefix = rainfall
                files_to_keep = 24
                method = idw

                [ntua]
                id = 9876
                ''').format(self))
        application = BitiaApp()
        self.assertRaisesRegex(configparser.Error, 'base_url',
                               application.run)

    def test_wrong_configuration4(self):
        with open(self.config_file, 'w') as f:
            f.write(textwrap.dedent('''\
                [General]
                mask = {0.mask_file}
                epsg = 2100
                cache_dir = {0.cache_dir}
                output_dir = {0.output_dir}
                filename_prefix = rainfall
                files_to_keep = 24
                method = idw

                [ntua]
                base_url = https://openmeteo.org/
                id = 9876
                nonexistent_option = irrelevant
                ''').format(self))
        application = BitiaApp()
        self.assertRaisesRegex(configparser.Error, 'nonexistent_option',
                               application.run)

    def test_wrong_configuration_epsg(self):
        with open(self.config_file, 'w') as f:
            f.write(textwrap.dedent('''\
                [General]
                mask = {0.mask_file}
                epsg = 81122
                cache_dir = {0.cache_dir}
                output_dir = {0.output_dir}
                filename_prefix = rainfall
                files_to_keep = 24
                method = idw

                [ntua]
                base_url = https://openmeteo.org/
                id = 9876
                ''').format(self))
        application = BitiaApp()
        self.assertRaisesRegex(WrongValueError, 'epsg=81122',
                               application.run)

    def test_get_last_dates(self):
        filename = os.path.join(self.cache_dir, 'timeseries.hts')
        with open(filename, 'w') as f:
            f.write(textwrap.dedent('''\
                2014-04-30 11:00,18.3,
                2014-04-30 12:00,19.3,
                2014-04-30 13:00,20.4,
                2014-04-30 14:00,21.4,
                '''))
        application = BitiaApp()
        with open(filename) as f:
            self.assertEquals(application.get_last_dates(filename, 2),
                              [datetime(2014, 4, 30, 13, 0),
                               datetime(2014, 4, 30, 14, 0)])
            f.seek(0)
            self.assertEquals(application.get_last_dates(filename, 20),
                              [datetime(2014, 4, 30, 11, 0),
                               datetime(2014, 4, 30, 12, 0),
                               datetime(2014, 4, 30, 13, 0),
                               datetime(2014, 4, 30, 14, 0)])

    def test_dates_to_calculate(self):
        application = BitiaApp()
        application.read_command_line()
        application.read_configuration()
        cache = TimeseriesCache(self.cache_dir, application.timeseries_group)
        application.cache = cache
        g = application.timeseries_group
        filename1 = cache.get_filename(g[0]['base_url'], g[0]['id'])
        filename2 = cache.get_filename(g[1]['base_url'], g[1]['id'])
        with open(filename1, 'w') as f:
            f.write(textwrap.dedent('''\
                2014-04-30 11:00,18.3,
                2014-04-30 13:00,20.4,
                2014-04-30 14:00,21.4,
                2014-04-30 15:00,22.4,
                '''))
        with open(filename2, 'w') as f:
            f.write(textwrap.dedent('''\
                2014-04-30 11:00,18.3,
                2014-04-30 12:00,19.3,
                2014-04-30 13:00,20.4,
                2014-04-30 14:00,21.4,
                '''))

        # Check for files_to_keep=24
        dates = []
        for d in application.dates_to_calculate:
            dates.append(d)
        self.assertEquals(dates, [datetime(2014, 4, 30, 11, 0),
                                  datetime(2014, 4, 30, 12, 0),
                                  datetime(2014, 4, 30, 13, 0),
                                  datetime(2014, 4, 30, 14, 0),
                                  datetime(2014, 4, 30, 15, 0)])

        # Check for files_to_keep=2
        application.config['General']['files_to_keep'] = 2
        dates = []
        for d in application.dates_to_calculate:
            dates.append(d)
        self.assertEquals(dates, [datetime(2014, 4, 30, 14, 0),
                                  datetime(2014, 4, 30, 15, 0)])

        # Check for files_to_keep=4
        application.config['General']['files_to_keep'] = 4
        dates = []
        for d in application.dates_to_calculate:
            dates.append(d)
        self.assertEquals(dates, [datetime(2014, 4, 30, 12, 0),
                                  datetime(2014, 4, 30, 13, 0),
                                  datetime(2014, 4, 30, 14, 0),
                                  datetime(2014, 4, 30, 15, 0)])

    def test_date_fmt(self):
        application = BitiaApp()
        application.read_command_line()
        application.read_configuration()
        cache = TimeseriesCache(self.cache_dir, application.timeseries_group)
        application.cache = cache
        g = application.timeseries_group
        filename1 = cache.get_filename(g[0]['base_url'], g[0]['id']) + '_step'
        filename2 = cache.get_filename(g[1]['base_url'], g[1]['id']) + '_step'

        # Ten-minute
        with open(filename1, 'w') as f:
            f.write('1')
        with open(filename2, 'w') as f:
            f.write('1')
        self.assertEquals(application.date_fmt, '%Y-%m-%d-%H-%M')

        # Hourly
        with open(filename1, 'w') as f:
            f.write('2')
        with open(filename2, 'w') as f:
            f.write('2')
        self.assertEquals(application.date_fmt, '%Y-%m-%d-%H-%M')

        # Daily
        with open(filename1, 'w') as f:
            f.write('3')
        with open(filename2, 'w') as f:
            f.write('3')
        self.assertEquals(application.date_fmt, '%Y-%m-%d')

        # Monthly
        with open(filename1, 'w') as f:
            f.write('4')
        with open(filename2, 'w') as f:
            f.write('4')
        self.assertEquals(application.date_fmt, '%Y-%m')

        # Annual
        with open(filename1, 'w') as f:
            f.write('5')
        with open(filename2, 'w') as f:
            f.write('5')
        self.assertEquals(application.date_fmt, '%Y')

        # Five-minute
        with open(filename1, 'w') as f:
            f.write('6')
        with open(filename2, 'w') as f:
            f.write('6')
        self.assertEquals(application.date_fmt, '%Y-%m-%d-%H-%M')

        # Fifteen-minute
        with open(filename1, 'w') as f:
            f.write('7')
        with open(filename2, 'w') as f:
            f.write('7')
        self.assertEquals(application.date_fmt, '%Y-%m-%d-%H-%M')

        # Inconsistent
        with open(filename1, 'w') as f:
            f.write('1')
        with open(filename2, 'w') as f:
            f.write('2')
        self.assertRaises(WrongValueError, lambda: application.date_fmt)

    def test_delete_obsolete_files(self):
        application = BitiaApp()
        application.read_command_line()
        application.read_configuration()

        # Create three files
        prefix = application.config['General']['filename_prefix']
        filename1 = os.path.join(self.output_dir, '{}-1.tif'.format(prefix))
        filename2 = os.path.join(self.output_dir, '{}-2.tif'.format(prefix))
        filename3 = os.path.join(self.output_dir, '{}-3.tif'.format(prefix))
        with open(filename1, 'w'):
            pass
        with open(filename2, 'w'):
            pass
        with open(filename3, 'w'):
            pass

        # Just to make sure we didn't screw up above, check
        self.assertTrue(os.path.exists(filename1))
        self.assertTrue(os.path.exists(filename2))
        self.assertTrue(os.path.exists(filename3))

        # Execute for files_to_keep = 2 and check
        application.config['General']['files_to_keep'] = 2
        application.delete_obsolete_files()
        self.assertFalse(os.path.exists(filename1))
        self.assertTrue(os.path.exists(filename2))
        self.assertTrue(os.path.exists(filename3))

        # Re-execute; nothing should have changed
        application.delete_obsolete_files()
        self.assertFalse(os.path.exists(filename1))
        self.assertTrue(os.path.exists(filename2))
        self.assertTrue(os.path.exists(filename3))
