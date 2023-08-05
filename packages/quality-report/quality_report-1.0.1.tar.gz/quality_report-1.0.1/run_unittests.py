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

# Run the unit tests. 

import StringIO
import logging
import unittest
import xmlrunner


if __name__ == '__main__':  # pragma: no branch
    # Make sure log messages are not shown on stdout/stderr. We can't simpy
    # increase the log level since some unit tests expect logging  to happen.
    logging.getLogger().addHandler(logging.StreamHandler(StringIO.StringIO()))
    # Run the unit test with the XML test runner so that the test output
    # can be processed by Sonar.
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
