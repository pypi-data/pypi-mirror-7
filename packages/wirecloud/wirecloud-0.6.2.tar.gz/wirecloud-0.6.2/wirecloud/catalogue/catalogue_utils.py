# -*- coding: utf-8 -*-

# Copyright (c) 2011-2014 CoNWeT Lab., Universidad Politécnica de Madrid

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

import json

from django.http import HttpResponse
from django.db.models import Q

from wirecloud.catalogue.get_json_catalogue_data import get_resource_group_data
from wirecloud.catalogue.models import CatalogueResource


def group_resources(resources):

    ordered_list = []
    grouped_resources = {}

    for resource in resources:
        key = resource.short_name + '/' + resource.vendor
        if key not in grouped_resources:
            entry = {
                'short_name': resource.short_name,
                'vendor': resource.vendor,
                'type': resource.resource_type(),
                'variants': [],
            }
            grouped_resources[key] = entry
            ordered_list.append(entry)
        else:
            entry = grouped_resources[key]

        entry['variants'].append(resource)

    return ordered_list


def _valid_resource(resource, user, user_groups):

    if resource.public or resource.users.filter(id=user.id).exists():
        return True

    # Check if the user is listed in any of the resource groups
    return len(set(resource.groups.all()) & set(user_groups)) > 0


def _filter_resource_by_user(entry, user, user_groups):

    entry['variants'] = [r for r in entry['variants'] if _valid_resource(r, user, user_groups)]
    return len(entry['variants']) > 0


def filter_resources_by_user(user, resources):
    """
    Filter resources visible to a given user
    """
    user_groups = user.groups.all()
    return [r for r in resources if _filter_resource_by_user(r, user, user_groups)]


def filter_resources_by_scope(resources, scope):
    if scope != 'all':
        return resources.filter(type=CatalogueResource.RESOURCE_TYPES.index(scope))
    else:
        return resources


def get_paginatedlist(resourcelist, pag, offset):
    """Returns a list paginated with the parameters pag and offset."""
    a = int(pag)
    b = int(offset)
    if a != 0 and b != 0:
        c = ((a - 1) * b)
        d = (b * a)
        if a == 1:
            c = 0
        resourcelist = resourcelist[c:d]

    return resourcelist


def get_and_filter(criterialist, user):
    """Returns a list of resources that match all the criteria in the list passed as parameter."""

    # List of the resources that match the criteria in the database table CatalogueResource
    criteria_filter = Q()

    criterialist = criterialist.split()
    for e in criterialist:
        criteria_filter = criteria_filter & (Q(short_name__icontains=e) | Q(display_name__icontains=e) | Q(vendor__icontains=e) | Q(author__icontains=e) | Q(mail__icontains=e) | Q(description__icontains=e) | Q(version__icontains=e))

    return criteria_filter


def get_or_filter(criterialist, user):
    """Returns a list of resources that match any of the criteria in the list passed as parameter."""
    criteria_filter = Q()

    criterialist = criterialist.split()
    for e in criterialist:
        criteria_filter = criteria_filter | (Q(short_name__icontains=e) | Q(vendor__icontains=e) | Q(author__icontains=e) | Q(mail__icontains=e) | Q(description__icontains=e) | Q(version__icontains=e))

    return criteria_filter


def get_not_filter(criterialist, user):
    """Returns a list of resources that don't match any of the criteria in the list passed as parameter."""
    criteria_filter = Q()

    criterialist = criterialist.split()
    for e in criterialist:
        criteria_filter = criteria_filter & ~(Q(short_name__icontains=e) | Q(vendor__icontains=e) | Q(author__icontains=e) | Q(mail__icontains=e) | Q(description__icontains=e) | Q(version__icontains=e))

    return criteria_filter


def get_event_filter(search_criteria):
    search_criteria = search_criteria.split()
    filters = Q()
    for e in search_criteria:
        filters = filters | Q(widgetwiring__friendcode__icontains=e)
    return filters & Q(widgetwiring__wiring='out')


def get_slot_filter(search_criteria):
    search_criteria = search_criteria.split()
    filters = Q()
    for e in search_criteria:
        filters = filters | Q(widgetwiring__friendcode__icontains=e)
    return filters & Q(widgetwiring__wiring='in')


def get_resource_response(resources, format, items, user, request=None):
    data = {
        'resources': [get_resource_group_data(group, user, request) for group in resources],
        'items': items,
    }
    return HttpResponse(json.dumps(data), content_type='application/json; charset=UTF-8')

def get_latest_resource_version(name, vendor):

    resource_versions = CatalogueResource.objects.filter(vendor=vendor, short_name=name)
    if resource_versions.count() > 0:
        # convert from ["1.9", "1.10", "1.9.1"] to [[1,9], [1,10], [1,9,1]] to
        # allow comparing integers
        versions = [map(int, r.version.split(".")) for r in resource_versions]

        index = 0
        for k in range(len(versions)):
            if max(versions[index], versions[k]) == versions[k]:
                index = k

        return resource_versions[index]

    return None
