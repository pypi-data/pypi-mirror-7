#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2014 Rémi Duraffort
# This file is part of SMSForward.
#
# SMSForward is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMSForward is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SMSForward.  If not, see <http://www.gnu.org/licenses/>.

import argparse

from SMSForward import providers


def main():
    parser = argparse.ArgumentParser(description="Forward the given text as SMS to the right user")
    parser.add_argument('-p', '--provider', required=True, help='The provider name')
    parser.add_argument('-u', '--user', required=True, help='The user name')
    parser.add_argument('-t', '--token', required=True, help='The user token')
    parser.add_argument('-m', '--message', required=True, help='The message to forward')

    options = parser.parse_args()

    # Open the right provider
    provider = providers.create(options.provider, {'user': options.user, 'token': options.token})
    provider.send_message(options.message)

if __name__ == '__main__':
    main()
