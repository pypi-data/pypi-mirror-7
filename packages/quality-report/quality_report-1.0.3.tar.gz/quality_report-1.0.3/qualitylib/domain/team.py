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

from qualitylib.domain.measurement.measurable import MeasurableObject


class Team(MeasurableObject):
    ''' Class for representing a team. '''

    def __init__(self, name, short_name=None, streets=None, is_scrum_team=False,
                 is_support_team=False, birt_id=None, release_archives=None,
                 technical_debt_targets=None, days_per_sprint=21):
        super(Team, self).__init__( \
            technical_debt_targets=technical_debt_targets)
        self.__name = name
        if short_name:
            assert len(short_name) == 2
        self.__short_name = short_name or self.__name[:2].upper()
        self.__streets = streets or []
        self.__release_archives = release_archives or []
        self.__is_scrum_team = is_scrum_team
        self.__is_support_team = is_support_team
        self.__birt_id = birt_id
        self.__days_per_sprint = days_per_sprint

    def __str__(self):
        return self.__name

    def name(self):
        ''' Return the full name of the team. '''
        return self.__name

    def id_string(self):
        ''' Return an id string for the team. '''
        return self.__name.lower().replace(' ', '_')

    def short_name(self):
        ''' Return an abbreviation of the team name. '''
        return self.__short_name

    def streets(self):
        ''' Return the development streets that the team uses. '''
        return self.__streets

    def release_archives(self):
        ''' Return the release archives of the team. '''
        return self.__release_archives

    def is_scrum_team(self):
        ''' Return whether this team is a Scrum team, which means it is
            doing product development. '''
        return self.__is_scrum_team

    def is_support_team(self):
        ''' Return whether this team is a support team, which means it is not
            doing direct product development. '''
        return self.__is_support_team

    def birt_id(self):
        ''' Return the id for this team in Birt. '''
        return self.__birt_id

    def days_per_sprint(self):
        ''' Return the sprint length in days that the team uses. '''
        return self.__days_per_sprint
