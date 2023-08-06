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


class SonarProductInfo(object):
    ''' Class to represent information that Sonar has about a product. '''
    def __init__(self, sonar, product):
        self.__sonar = sonar
        self.__product = product

    def all_sonar_ids(self):
        ''' Return all Sonar ids of the product: the Sonar id of the product
            itself and its unit tests if applicable. '''
        sonar_ids = set([self.__product.sonar_id()])
        for component in [self.__product.unittests(), self.__product.jsf()]:
            if component:
                sonar_ids.add(component.sonar_id())
        return sonar_ids
