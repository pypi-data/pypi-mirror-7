'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unittest
import logging
import StringIO
import urllib2
from qualitylib.metric_source import Pom
from qualitylib import domain


MINIMAL_POM = '<version>1</version>'
ONE_DEPENDENCY = MINIMAL_POM + '''
    <dependency>
        <artifactid>artifact_id</artifactid>
        <version>1.0</version>
    </dependency>'''
ONE_PROPERTY = '''
    <properties>
        <version>2.0 </version><!-- Spaces should be ignored -->
    </properties>
    <dependency>
        <artifactid>artifact_id</artifactid>
        <version>${version}</version>
    </dependency>'''
RECURSIVE_PROPERTY = '''
    <properties>
        <empty></empty>
        <other>3.0</other>
        <version>${other}</version>
    </properties>
    <dependency>
        <artifactid>artifact_id</artifactid>
        <version>${version}</version>
    </dependency>'''


class PomUnderTest(Pom):
    ''' Override class to return a static pom file. '''
    def url_open(self, url):
        if 'raise' in url:
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            return url


class PomTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the pom file metric source. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__pom = PomUnderTest()

    def test_no_dependencies(self):
        ''' Test pom without dependencies. '''
        self.assertEqual(set(), self.__pom.dependencies(MINIMAL_POM, []))
        
    def test_log_http_error(self):
        ''' Test that a HTTP error while opening a pom file is logged. '''
        stream = StringIO.StringIO()
        logging.getLogger().addHandler(logging.StreamHandler(stream))
        self.__pom.dependencies('raise', [])
        stream.seek(0)
        self.assertEqual("Couldn't open raise/pom.xml: HTTP Error None: None\n",
                         stream.getvalue())

    def test_dependency(self):
        ''' Test a pom with one dependency. '''
        product = domain.Product(domain.Project(), 'product',
                                 'group_id:artifact_id')
        self.assertEqual(set([('artifact_id', '1.0')]), 
                         self.__pom.dependencies(ONE_DEPENDENCY, [product]))
        
    def test_property(self):
        ''' Test a pom with a property. '''
        product = domain.Product(domain.Project(), 'product',
                                 'group_id:artifact_id')
        self.assertEqual(set([('artifact_id', '2.0')]), 
                         self.__pom.dependencies(ONE_PROPERTY, [product]))
        
    def test_recursive_property(self):
        ''' Test a pom with a property whose value is a property. '''
        product = domain.Product(domain.Project(), 'product',
                                 'group_id:artifact_id')
        self.assertEqual(set([('artifact_id', '3.0')]), 
                         self.__pom.dependencies(RECURSIVE_PROPERTY, [product]))
