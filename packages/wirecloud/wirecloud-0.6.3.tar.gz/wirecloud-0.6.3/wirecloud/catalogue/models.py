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

import random
from urlparse import urlparse

from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from wirecloud.commons.models import TransModel
from wirecloud.commons.utils.http import get_absolute_reverse_url
from wirecloud.commons.utils.template.parsers import TemplateParser


@python_2_unicode_compatible
class CatalogueResource(TransModel):

    RESOURCE_TYPES = ('widget', 'mashup', 'operator')
    RESOURCE_MIMETYPES = ('application/x-widget+mashable-application-component', 'application/x-mashup+mashable-application-component', 'application/x-operator+mashable-application-component')
    TYPE_CHOICES = (
        (0, 'Widget'),
        (1, 'Mashup'),
        (2, 'Operator'),
    )

    short_name = models.CharField(_('Name'), max_length=250)
    display_name = models.CharField(_('Display Name'), max_length=250, null=True, blank=True)
    vendor = models.CharField(_('Vendor'), max_length=250)
    version = models.CharField(_('Version'), max_length=150)
    type = models.SmallIntegerField(_('Type'), choices=TYPE_CHOICES, null=False, blank=False)

    author = models.CharField(_('Author'), max_length=250)
    mail = models.CharField(_('Mail'), max_length=100)

    # Person who added the resource to catalogue!
    creator = models.ForeignKey(User, null=True, blank=True, related_name='uploaded_resources')
    public = models.BooleanField(_('Available to all users'), default=False)
    users = models.ManyToManyField(User, verbose_name=_('Users'), related_name='local_resources', blank=True)
    groups = models.ManyToManyField(Group, verbose_name=_('Groups'), related_name='local_resources', blank=True)

    description = models.TextField(_('Description'))
    license = models.CharField(_('License'), max_length=20, null=True, blank=True)

    creation_date = models.DateTimeField('creation_date')
    image_uri = models.CharField(_('imageURI'), max_length=200, blank=True)
    iphone_image_uri = models.CharField(_('iPhoneImageURI'), max_length=200, blank=True)
    wiki_page_uri = models.CharField(_('wikiURI'), max_length=200, blank=True)
    template_uri = models.CharField(_('templateURI'), max_length=200, blank=True)

    popularity = models.DecimalField(_('popularity'), default=0, max_digits=2, decimal_places=1)
    fromWGT = models.BooleanField(_('fromWGT'), default=False)

    json_description = models.TextField(_('JSON description'))

    @property
    def local_uri_part(self):

        return self.vendor + '/' + self.short_name + '/' + self.version

    @property
    def cache_version(self):
        version = cache.get('_catalogue_resource_version/' + str(self.id))
        if version is None:
            version = random.randrange(1, 100000)
            cache.set('_catalogue_resource_version/' + str(self.id), version)

        return version

    def is_available_for(self, user):

        return self.public or self.users.filter(id=user.id).exists() or len(set(self.groups.all()) & set(user.groups.all())) > 0

    def get_template(self, request=None):

        if urlparse(self.template_uri).scheme == '':
            template_uri = get_absolute_reverse_url('wirecloud.showcase_media', kwargs={
                'vendor': self.vendor,
                'name': self.short_name,
                'version': self.version,
                'file_path': self.template_uri
            }, request=request)
        else:
            template_uri = self.template_uri

        parser = TemplateParser(self.json_description, base=template_uri)
        return parser

    def get_processed_info(self, request=None):

        parser = self.get_template(request)

        return parser.get_resource_processed_info()

    def delete(self, *args, **kwargs):

        from wirecloud.catalogue.utils import wgt_deployer

        # Delete the related wiring information for that resource
        WidgetWiring.objects.filter(idResource=self.id).delete()

        if hasattr(self, 'widget'):
            from wirecloud.platform.models import Widget
            try:
                self.widget.delete()
            except Widget.DoesNotExist:
                pass

        # Delete media resources if needed
        if not self.template_uri.startswith(('http', 'https')):
            wgt_deployer.undeploy(self.vendor, self.short_name, self.version)

        old_id = self.id
        super(CatalogueResource, self).delete(*args, **kwargs)

        # Remove cache for this resource
        try:
            cache.incr('_catalogue_resource_version/' + str(old_id))
        except ValueError:
            pass

    def resource_type(self):
        return self.RESOURCE_TYPES[self.type]

    @property
    def mimetype(self):
        return self.RESOURCE_MIMETYPES[self.type]

    class Meta:
        unique_together = ("short_name", "vendor", "version")

    def __str__(self):
        return self.local_uri_part


@python_2_unicode_compatible
class WidgetWiring(models.Model):

    friendcode = models.CharField(_('Friend code'), max_length=30, blank=True, null=True)
    wiring = models.CharField(_('Wiring'), max_length=5)
    idResource = models.ForeignKey(CatalogueResource)

    def __str__(self):
        return self.friendcode
