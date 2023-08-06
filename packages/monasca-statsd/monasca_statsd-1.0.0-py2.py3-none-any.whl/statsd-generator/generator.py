#!/usr/bin/python
# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ConfigParser
import random
import time

import monascastatsd.monasca_statsd

'''The statsd generator will provide a testbed for testing

the monasca agent statsd capability with dimensions
'''


class MonascaStatsdGenerator(object):

    '''Class to generate MonascaStatsd metrics.'''

    def __init__(self, config):
        '''Constructor.'''
        print (config)
        self.num_of_iterations = int(config["iterations"])
        self.delay = int(config["delay"])
        self.host = config["host"]
        self.port = config["port"]

    def send_messages(self):
        '''Main processing for sending messages.'''
        try:
            statsd = monascastatsd.monasca_statsd.MonascaStatsd()
            statsd.connect(self.host, self.port)
            for index in range(1, self.num_of_iterations + 1):
                print("Starting iteration " + str(index) +
                      " of " + str(self.num_of_iterations))
                statsd.increment('Teraflops', 5)
                statsd.gauge('NumOfTeraflops',
                             random.uniform(1.0, 10.0),
                             dimensions={'Origin': 'Dev',
                                         'Environment': 'Test'})
                statsd.histogram('file.upload.size',
                                 random.randrange(1, 100),
                                 dimensions={'Version': '1.0'})
                print("Completed iteration " + str(index) +
                      ".  Sleeping for " + str(self.delay) + " seconds...")
                time.sleep(self.delay)
        except Exception:
            print ("Error sending statsd messages...")
            raise


def read_config():
    '''Read in the config file.'''
    config = ConfigParser.ConfigParser()
    config.read("generator.conf")
    config_options = {}
    section = "main"
    options = config.options(section)
    for option in options:
        try:
            config_options[option] = config.get(section, option)
            if config_options[option] == -1:
                print("skip: %s" % option)
        except Exception:
            print("exception on %s!" % option)
            config_options[option] = None
    return config_options


def main():
    config = read_config()
    generator = MonascaStatsdGenerator(config)
    generator.send_messages()

if __name__ == "__main__":
    main()
