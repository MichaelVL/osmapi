from __future__ import (unicode_literals, absolute_import)
from nose.tools import *  # noqa
from . import osmapi_tests
import mock
import xmltodict
try:
    import urlparse
except:
    import urllib
    urlparse = urllib.parse


def recursive_sort(col):  # noqa
    """
    Function to recursive sort a collection
    that might contain lists, dicts etc.
    In Python 3.x a list of dicts is sorted by it's hash
    """
    if hasattr(col, '__iter__'):
        if isinstance(col, list):
            try:
                col = sorted(col)
            except TypeError:  # in Python 3.x: lists of dicts are not sortable
                col = sorted(col, key=lambda k: hash(frozenset(k.items())))
            except:
                pass

            for idx, elem in enumerate(col):
                col[idx] = recursive_sort(elem)
        elif isinstance(col, dict):
            for elem in col:
                try:
                    col[elem] = recursive_sort(col[elem])
                except IndexError:
                    pass
    return col


def xmltosorteddict(xml):
    xml_dict = xmltodict.parse(xml, dict_constructor=dict)
    return recursive_sort(xml_dict)


def debug(result):
    from pprint import pprint
    pprint(result)
    assert_equals(0, 1)


class TestOsmApiChangeset(osmapi_tests.TestOsmApi):
    def test_ChangesetGet(self):
        self._http_mock()

        result = self.api.ChangesetGet(123)

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'GET')
        self.assertEquals(args[1], '/api/0.6/changeset/123')
        self.assertFalse(args[2])

        self.assertEquals(result, {
            'id': 123,
            'closed_at': '2009-09-07T22:57:37Z',
            'created_at': '2009-09-07T21:57:36Z',
            'max_lat': '52.4710193',
            'max_lon': '-1.4831815',
            'min_lat': '45.9667901',
            'min_lon': '-1.4998534',
            'open': False,
            'user': 'randomjunk',
            'uid': 3,
            'tag': {
                'comment': 'correct node bug',
                'created_by': 'Potlatch 1.2a',
            },
        })

    def test_ChangesetUpdate(self):
        self._http_mock()

        # setup mock
        self.api.ChangesetCreate = mock.Mock(
            return_value=4444
        )
        self.api._CurrentChangesetId = 4444

        result = self.api.ChangesetUpdate(
            {
                'test': 'foobar'
            }
        )

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'PUT')
        self.assertEquals(args[1], '/api/0.6/changeset/4444')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osm version="0.6" generator="osmapi/0.3.0">\n'
                b'  <changeset visible="true">\n'
                b'    <tag k="test" v="foobar"/>\n'
                b'    <tag k="created_by" v="osmapi/0.3.0"/>\n'
                b'  </changeset>\n'
                b'</osm>\n'
            )
        )
        self.assertEquals(result, 4444)

    def test_ChangesetUpdate_with_created_by(self):
        self._http_mock()

        # setup mock
        self.api.ChangesetCreate = mock.Mock(
            return_value=4444
        )
        self.api._CurrentChangesetId = 4444

        result = self.api.ChangesetUpdate(
            {
                'test': 'foobar',
                'created_by': 'MyTestOSMApp'
            }
        )

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'PUT')
        self.assertEquals(args[1], '/api/0.6/changeset/4444')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osm version="0.6" generator="osmapi/0.3.0">\n'
                b'  <changeset visible="true">\n'
                b'    <tag k="test" v="foobar"/>\n'
                b'    <tag k="created_by" v="MyTestOSMApp"/>\n'
                b'  </changeset>\n'
                b'</osm>\n'
            )
        )
        self.assertEquals(result, 4444)

    def test_ChangesetUpdate_wo_changeset(self):
        self._http_mock()

        with self.assertRaisesRegexp(
                Exception,
                'No changeset currently opened'):
            self.api.ChangesetUpdate(
                {
                    'test': 'foobar'
                }
            )

    def test_ChangesetCreate(self):
        self._http_mock()

        result = self.api.ChangesetCreate(
            {
                'foobar': 'A new test changeset'
            }
        )

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'PUT')
        self.assertEquals(args[1], '/api/0.6/changeset/create')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osm version="0.6" generator="osmapi/0.3.0">\n'
                b'  <changeset visible="true">\n'
                b'    <tag k="foobar" v="A new test changeset"/>\n'
                b'    <tag k="created_by" v="osmapi/0.3.0"/>\n'
                b'  </changeset>\n'
                b'</osm>\n'
            )
        )
        self.assertEquals(result, 4321)

    def test_ChangesetCreate_with_created_by(self):
        self._http_mock()

        result = self.api.ChangesetCreate(
            {
                'foobar': 'A new test changeset',
                'created_by': 'CoolTestApp',
            }
        )

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'PUT')
        self.assertEquals(args[1], '/api/0.6/changeset/create')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osm version="0.6" generator="osmapi/0.3.0">\n'
                b'  <changeset visible="true">\n'
                b'    <tag k="foobar" v="A new test changeset"/>\n'
                b'    <tag k="created_by" v="CoolTestApp"/>\n'
                b'  </changeset>\n'
                b'</osm>\n'
            )
        )
        self.assertEquals(result, 1234)

    def test_ChangesetCreate_with_open_changeset(self):
        self._http_mock()

        self.api.ChangesetCreate(
            {
                'test': 'an already open changeset',
            }
        )

        with self.assertRaisesRegexp(
                Exception,
                'Changeset already opened'):
            self.api.ChangesetCreate(
                {
                    'test': 'foobar'
                }
            )

    def test_ChangesetClose(self):
        self._http_mock()

        # setup mock
        self.api.ChangesetCreate = mock.Mock(
            return_value=4444
        )
        self.api._CurrentChangesetId = 4444

        self.api.ChangesetClose()

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'PUT')
        self.assertEquals(args[1], '/api/0.6/changeset/4444/close')
        self.assertTrue(args[2])

    def test_ChangesetClose_with_no_changeset(self):
        self._http_mock()

        with self.assertRaisesRegexp(
                Exception,
                'No changeset currently opened'):
            self.api.ChangesetClose()

    def test_ChangesetUpload_create_node(self):
        self._http_mock()

        # setup mock
        self.api.ChangesetCreate = mock.Mock(
            return_value=4444
        )
        self.api._CurrentChangesetId = 4444

        changesdata = [
            {
                'type': 'node',
                'action': 'create',
                'data': {
                    'lat': 47.123,
                    'lon': 8.555,
                    'tag': {
                        'amenity': 'place_of_worship',
                        'religion': 'pastafarian'
                    }
                }
            }
        ]

        result = self.api.ChangesetUpload(changesdata)

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'POST')
        self.assertEquals(args[1], '/api/0.6/changeset/4444/upload')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osmChange version="0.6" generator="osmapi/0.3.0">\n'
                b'<create>\n'
                b'  <node lat="47.123" lon="8.555" visible="true" '
                b'changeset="4444">\n'
                b'    <tag k="religion" v="pastafarian"/>\n'
                b'    <tag k="amenity" v="place_of_worship"/>\n'
                b'  </node>\n'
                b'</create>\n'
                b'</osmChange>'
            )
        )

        self.assertEquals(result[0]['type'], changesdata[0]['type'])
        self.assertEquals(result[0]['action'], changesdata[0]['action'])

        data = result[0]['data']
        self.assertEquals(data['lat'], changesdata[0]['data']['lat'])
        self.assertEquals(data['lon'], changesdata[0]['data']['lon'])
        self.assertEquals(data['tag'], changesdata[0]['data']['tag'])
        self.assertEquals(data['id'], 4295832900)
        self.assertEquals(result[0]['data']['version'], 1)

    def test_ChangesetUpload_modify_way(self):
        self._http_mock()

        # setup mock
        self.api.ChangesetCreate = mock.Mock(
            return_value=4444
        )
        self.api._CurrentChangesetId = 4444

        changesdata = [
            {
                'type': 'way',
                'action': 'modify',
                'data': {
                    'id': 4294967296,
                    'version': 2,
                    'nd': [
                        4295832773,
                        4295832773,
                        4294967304,
                        4294967303,
                        4294967300,
                        4608751,
                        4294967305,
                        4294967302,
                        8548430,
                        4294967296,
                        4294967301,
                        4294967298,
                        4294967306,
                        7855737,
                        4294967297,
                        4294967299
                    ],
                    'tag': {
                        'highway': 'secondary',
                        'name': 'Stansted Road'
                    }
                }
            }
        ]

        result = self.api.ChangesetUpload(changesdata)

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'POST')
        self.assertEquals(args[1], '/api/0.6/changeset/4444/upload')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osmChange version="0.6" generator="osmapi/0.3.0">\n'
                b'<modify>\n'
                b'  <way id="4294967296" version="2" visible="true" '
                b'changeset="4444">\n'
                b'    <tag k="name" v="Stansted Road"/>\n'
                b'    <tag k="highway" v="secondary"/>\n'
                b'    <nd ref="4295832773"/>\n'
                b'    <nd ref="4295832773"/>\n'
                b'    <nd ref="4294967304"/>\n'
                b'    <nd ref="4294967303"/>\n'
                b'    <nd ref="4294967300"/>\n'
                b'    <nd ref="4608751"/>\n'
                b'    <nd ref="4294967305"/>\n'
                b'    <nd ref="4294967302"/>\n'
                b'    <nd ref="8548430"/>\n'
                b'    <nd ref="4294967296"/>\n'
                b'    <nd ref="4294967301"/>\n'
                b'    <nd ref="4294967298"/>\n'
                b'    <nd ref="4294967306"/>\n'
                b'    <nd ref="7855737"/>\n'
                b'    <nd ref="4294967297"/>\n'
                b'    <nd ref="4294967299"/>\n'
                b'  </way>\n'
                b'</modify>\n'
                b'</osmChange>'
            )
        )

        self.assertEquals(result[0]['type'], changesdata[0]['type'])
        self.assertEquals(result[0]['action'], changesdata[0]['action'])

        data = result[0]['data']
        self.assertEquals(data['nd'], changesdata[0]['data']['nd'])
        self.assertEquals(data['tag'], changesdata[0]['data']['tag'])
        self.assertEquals(data['id'], 4294967296)
        self.assertEquals(data['version'], 3)

    def test_ChangesetUpload_delete_relation(self):
        self._http_mock()

        # setup mock
        self.api.ChangesetCreate = mock.Mock(
            return_value=4444
        )
        self.api._CurrentChangesetId = 4444

        changesdata = [
            {
                'type': 'relation',
                'action': 'delete',
                'data': {
                    'id': 676,
                    'version': 2,
                    'member': [
                        {
                            'ref': 4799,
                            'role': 'outer',
                            'type': 'way'
                        },
                        {
                            'ref': 9391,
                            'role': 'outer',
                            'type': 'way'
                        },
                    ],
                    'tag': {
                        'admin_level': '9',
                        'boundary': 'administrative',
                        'type': 'multipolygon'
                    }
                }
            }
        ]

        result = self.api.ChangesetUpload(changesdata)

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'POST')
        self.assertEquals(args[1], '/api/0.6/changeset/4444/upload')
        self.assertTrue(args[2])
        self.assertEquals(
            xmltosorteddict(args[3]),
            xmltosorteddict(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<osmChange version="0.6" generator="osmapi/0.3.0">\n'
                b'<delete>\n'
                b'  <relation id="676" version="2" visible="true" '
                b'changeset="4444">\n'
                b'    <tag k="admin_level" v="9"/>\n'
                b'    <tag k="boundary" v="administrative"/>\n'
                b'    <tag k="type" v="multipolygon"/>\n'
                b'    <member type="way" ref="4799" role="outer"/>\n'
                b'    <member type="way" ref="9391" role="outer"/>\n'
                b'  </relation>\n'
                b'</delete>\n'
                b'</osmChange>'
            )
        )

        self.assertEquals(result[0]['type'], changesdata[0]['type'])
        self.assertEquals(result[0]['action'], changesdata[0]['action'])

        data = result[0]['data']
        self.assertEquals(data['member'], changesdata[0]['data']['member'])
        self.assertEquals(data['tag'], changesdata[0]['data']['tag'])
        self.assertEquals(data['id'], 676)
        self.assertNotIn('version', data)

    def test_ChangesetDownload(self):
        self._http_mock()

        result = self.api.ChangesetDownload(23123)

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'GET')
        self.assertEquals(args[1], '/api/0.6/changeset/23123/download')
        self.assertFalse(args[2])

        self.assertEquals(len(result), 16)
        self.assertEquals(
            result[1],
            {
                'action': 'create',
                'type': 'node',
                'data': {
                    'changeset': 23123,
                    'id': 4295668171,
                    'lat': 46.4909781,
                    'lon': 11.2743295,
                    'tag': {
                        'highway': 'traffic_signals'
                    },
                    'timestamp': '2013-05-14T10:33:04Z',
                    'uid': 1178,
                    'user': 'tyrTester06',
                    'version': 1,
                    'visible': True
                }
            }
        )

    def test_ChangesetsGet(self):
        self._http_mock()

        result = self.api.ChangesetsGet(
            only_closed=True,
            username='metaodi'
        )

        args, kwargs = self.api._http_request.call_args
        self.assertEquals(args[0], 'GET')
        self.assertEquals(
            dict(urlparse.parse_qsl(urlparse.urlparse(args[1])[4])),
            {
                'display_name': 'metaodi',
                'closed': '1'
            }
        )
        self.assertFalse(args[2])

        self.assertEquals(len(result), 10)

        self.assertEquals(result[41417], {
            'closed_at': '2014-04-29T20:25:01Z',
            'created_at': '2014-04-29T20:25:01Z',
            'id': 41417,
            'max_lat': '58.8997467',
            'max_lon': '22.7364427',
            'min_lat': '58.8501594',
            'min_lon': '22.6984333',
            'open': False,
            'tag': {
                'comment': 'Test delete of relation',
                'created_by': 'iD 1.3.9',
                'imagery_used': 'Bing'
            },
            'uid': 1841,
            'user': 'metaodi'
        })