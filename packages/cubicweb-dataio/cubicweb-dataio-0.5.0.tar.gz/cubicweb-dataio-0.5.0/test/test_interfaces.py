# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cStringIO import StringIO
from cubicweb.devtools import testlib

from cubes.dataio.interfaces import (CSVRdfReader, CSVRdfWriter, DictFobj,
                                     build_rdf_reader, build_rdf_writer,
                                     convert_string, convert_int,
                                     convert_float, convert_date,
                                     normalize_xml, split_uri, build_uri_dict)


RDF_DATA = set([(u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://dbpedia.org/ontology/abstract',
                 u'Taman Scientex is a township in Pasir Gudang, '
                 u'Johor, Malaysia. This townships is located '
                 u'between Masai and Pasir Gudang.',
                 'literal'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://xmlns.com/foaf/0.1/isPrimaryTopicOf',
                 u'http://en.wikipedia.org/wiki/Taman_Scientex',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/2000/01/rdf-schema#label',
                 u'Taman Scientex',
                 'literal'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/ns/prov#wasDerivedFrom',
                 u'http://en.wikipedia.org/wiki/Taman_Scientex?oldid=412881153',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/2002/07/owl#sameAs',
                 u'http://rdf.freebase.com/ns/m.06wb2yz',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://dbpedia.org/property/hasPhotoCollection',
                 u'http://www4.wiwiss.fu-berlin.de/flickrwrappr/photos/Taman_Scientex',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/2000/01/rdf-schema#comment',
                 u'Taman Scientex is a township in Pasir Gudang, '
                 u'Johor, Malaysia. This townships is located '
                 u'between Masai and Pasir Gudang.',
                 'literal'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://purl.org/dc/terms/subject',
                 u'http://dbpedia.org/resource/Category:Towns_and_'
                 u'suburbs_in_Johor_Bahru_District',
                 'resource')
                ])


CSV_DATA_1 = set([('row 0', 'col 0', u'1024032', 'literal'),
                  ('row 1', 'col 0', u'1024034', 'literal'),
                  ('row 7', 'col 16', u'211', 'literal'),
                  ('row 7', 'col 17', u'Europe/Paris', 'literal'),
                  ('row 10', 'col 7', u'PPL', 'literal'),
                  ('row 9', 'col 8', u'FR', 'literal'),
                 ])

CSV_DATA_2 = set([('row 0', 'geoid', u'1024032', 'literal'),
                  ('row 1', 'geoid', u'1024034', 'literal'),
                  ('row 2', 'name', u'Rocher Sud', 'literal'),
                  ('row 2', 'longitude', u'47.3', 'literal'),
                  ])

CSV_DATA_3 = set([('1024034', 'name', u'Île du Lys', 'literal'),
                  ('1024035', 'name', u'Rocher Sud', 'literal'),
                  ('1024036', 'longitude', u'47.33333', 'literal'),
                  ])


class CsvReaderTC(testlib.CubicWebTC):
    def test_csv_no_fields(self):
        reader = CSVRdfReader()
        results = list(reader.iterate_triples_from_file(
                self.datapath('FR.txt'), separator='\t', uri_ind=None))
        for triple in CSV_DATA_1:
            self.assertIn(triple, results)

    def test_csv_fields(self):
        reader = CSVRdfReader({0: u'geoid', 1:u'name', 5: 'longitude'})
        results = list(reader.iterate_triples_from_file(
                self.datapath('FR.txt'), separator='\t', limit=3, uri_ind=None))
        for triple in CSV_DATA_2:
            self.assertIn(triple, results)

    def test_csv_fields_id(self):
        reader = CSVRdfReader({1:u'name', 5: 'longitude'})
        results = list(reader.iterate_triples_from_file(
                self.datapath('FR.txt'), separator='\t', limit=3, uri_ind=0))
        for triple in CSV_DATA_3:
            self.assertIn(triple, results)


class CsvWriterTC(testlib.CubicWebTC):

    def test_csv_fields_id(self):
        # Write data
        tmp_filename = 'tmp_rdf_test.txt'
        writer = CSVRdfWriter(separator='\t')
        for _s, _p, _o, _ot in CSV_DATA_3:
            writer.add_triple(_s, _p, _o, _ot)
        writer.write_file(tmp_filename)
        # Read them for test
        reader = CSVRdfReader({1:u'name', 2: 'longitude'})
        results = set(reader.iterate_triples_from_file(
                tmp_filename, separator=',', limit = 2, uri_ind=0))
        self.assertEqual(CSV_DATA_3, results)


class RdfReaderTC(testlib.CubicWebTC):

    def _test_format(self, library, formats):
        for _format in formats:
            reader = build_rdf_reader(library=library, rdf_format=_format,
                                      encoding='unicode_escape')
            filename = osp.join(HERE, 'data/Taman_Scientex.%s' % _format)
            triples = reader.iterate_triples_from_file(filename)
            results = set([i for i in triples])
            self.assertEqual(self.wanted, results)

    def _test_extension(self, library, extensions):
        for extension in extensions:
            reader = build_rdf_reader(library=library, encoding='unicode_escape')
            filename = self.datapath('Taman_Scientex.%s' % extension)
            triples = reader.iterate_triples_from_file(filename)
            results = set([i for i in triples])
            self.assertEqual(RDF_DATA, results)

    def test_raw(self):
        self._test_extension('rawnt', ['nt'])

    def test_rdflib(self):
        self._test_extension('rdflib', ['nt', 'rdf'])

    def test_librdf(self):
        self._test_extension('librdf', ['nt', 'rdf'])


class RdfWriterTC(testlib.CubicWebTC):

    def setUp(self):
        self.data = RDF_DATA

    def _test_format(self, library, rdf_format, with_ot=True):
        # Write data
        tmp_filename = 'tmp_rdf_test.txt'
        writer = build_rdf_writer(library=library, encoding='utf-8')
        for _s, _p, _o, _ot in self.data:
            if not with_ot:
                _ot = None
            writer.add_triple(_s, _p, _o, _ot)
        writer.write_file(tmp_filename, rdf_format=rdf_format)
        # Read them for test
        reader = build_rdf_reader(library=library,
                                  encoding='utf-8')
        triples = reader.iterate_triples_from_file(tmp_filename,
                                                   rdf_format=rdf_format)
        results = set([i for i in triples])
        self.assertEqual(self.data, results)

    def test_raw(self):
        value = self._test_format('rawnt', 'ntriples')

    def test_raw_without_type(self):
        value = self._test_format('rawnt', 'ntriples', with_ot=False)

    def test_rdflib(self):
        for rdf_format in ('ntriples', 'n3', 'rdfxml'):
            value = self._test_format('rdflib', rdf_format)

    def test_rdflib_without_type(self):
        for rdf_format in ('ntriples', 'n3', 'rdfxml'):
            value = self._test_format('rdflib', rdf_format, with_ot=False)

    def test_librdf(self):
        for rdf_format in ('ntriples', 'n3', 'rdfxml'):
            value = self._test_format('librdf', rdf_format)

    def test_librdf_without_type(self):
        for rdf_format in ('ntriples', 'n3', 'rdfxml'):
            value = self._test_format('librdf', rdf_format, with_ot=False)


class ConverterTC(testlib.CubicWebTC):

    def test_convert_string(self):
        self.assertEqual(convert_string('toto'), 'toto')

    def test_convert_int(self):
        self.assertEqual(convert_int('11'), 11)
        self.assertEqual(convert_int('X11'), None)

    def test_convert_float(self):
        self.assertEqual(convert_float('12.'), 12.)
        self.assertEqual(convert_float('X12'), None)
        self.assertEqual(convert_float('12,3'), 12.3)

    def test_convert_date(self):
        date = convert_date('14-11-2012')
        self.assertEqual(date.day, 14)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.year, 2012)
        date = convert_date('2012-11-14', datetime_format='%Y-%m-%d')
        self.assertEqual(date.day, 14)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.year, 2012)


class RDFUtilitiesTC(testlib.CubicWebTC):

    def test_split_uri(self):
        self.assertEqual(split_uri("http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation"),
                          ("http://rdvocab.info/uri/schema/FRBRentitiesRDA/" , "Manifestation"))
        self.assertEqual(split_uri("http://www.w3.org/2004/02/skos/core#concept"),
                          ("http://www.w3.org/2004/02/skos/core#", "concept"))

    def test_normalize_xml(self):
        self.assertEqual(normalize_xml("http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation"),
                         'frbr:Manifestation')
        self.assertEqual(normalize_xml("http://www.w3.org/2004/02/skos/core#concept"),
                         'skos:concept')
        self.assertEqual(normalize_xml("http://www.w3.org/test#concept"),
                         "http://www.w3.org/test#:concept")


    def test_build_uri_dict(self):
        filename = self.datapath('Taman_Scientex.rdf')
        uri_dict = build_uri_dict((filename,), library='rdflib')
        self.assertTrue('http://dbpedia.org/resource/Taman_Scientex' in uri_dict)
        rdf_properties = uri_dict['http://dbpedia.org/resource/Taman_Scientex']
        self.assertEqual(rdf_properties['http://purl.org/dc/terms/subject'],
                         [(u'http://dbpedia.org/resource/Category:Towns_and_suburbs_in_Johor_Bahru_District',
                           'resource')])
        self.assertEqual(rdf_properties[u'http://www.w3.org/ns/prov#wasDerivedFrom'],
                         [(u'http://en.wikipedia.org/wiki/Taman_Scientex?oldid=412881153', 'resource')])

    def test_mmap(self):
        filename = self.datapath('mmap.csv')
        mmap = DictFobj(filename, separator=',', cast_type=int)
        mmap.fit()
        self.assertEqual(len(mmap.internal_dict), 3)
        self.assertEqual(mmap.get(1)[1], 'Toto')
        self.assertEqual(mmap.get(2)[1], 'Tata')
        self.assertEqual(mmap.get(1)[1], 'Toto')

    def test_mmap2(self):
        filename = self.datapath('mmap2.csv')
        mmap = DictFobj(filename, separator=',', cast_type=int)
        mmap.fit(index_key=1)
        self.assertEqual(len(mmap.internal_dict), 3)
        self.assertEqual(mmap.get(1)[2], 'Toto')
        self.assertEqual(mmap.get(2)[2], 'Tata')
        self.assertEqual(mmap.get(1)[2], 'Toto')

    def test_mmap3(self):
        filename = self.datapath('mmap.csv')
        mmap = DictFobj(filename, separator=',')
        mmap.fit()
        self.assertEqual(len(mmap.internal_dict), 3)
        self.assertEqual(mmap.get('1')[1], 'Toto')
        self.assertEqual(mmap.get('2')[1], 'Tata')
        self.assertEqual(mmap.get('1')[1], 'Toto')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
