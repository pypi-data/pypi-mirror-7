# -*- coding: utf-8 -*-

# Copyright (c) 2013-2014 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import regex


__all__ = ('is_valid_name', 'is_valid_vendor', 'is_valid_version')


NAME_RE = regex.compile(r'^[^/]+$')
VENDOR_RE = regex.compile(r'^[^/]+$')
VERSION_RE = regex.compile(r'^(?:[1-9]\d*\.|0\.)*(?:[1-9]\d*|0)(?:(?:a|b|rc)[1-9]\d*)?$')


class TemplateParseException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)

    def __unicode__(self):
        return unicode(self.msg)


def is_valid_name(name):

    return regex.match(NAME_RE, name)


def is_valid_vendor(vendor):

    return regex.match(VENDOR_RE, vendor)


def is_valid_version(version):

    return regex.match(VERSION_RE, version)
