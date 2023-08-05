# -*- coding: utf-8 -*-
"""
###############################################################################
# Copyright 2013 Grigoriy Kramarenko.
###############################################################################
# This file is part of BWP.
#
#    BWP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BWP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BWP.  If not, see <http://www.gnu.org/licenses/>.
#
# Этот файл — часть BWP.
#
#   BWP - свободная программа: вы можете перераспространять ее и/или
#   изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
#   в каком она была опубликована Фондом свободного программного обеспечения;
#   либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
#   версии.
#
#   BWP распространяется в надежде, что она будет полезной,
#   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
#   общественной лицензии GNU.
#
#   Вы должны были получить копию Стандартной общественной лицензии GNU
#   вместе с этой программой. Если это не так, см.
#   <http://www.gnu.org/licenses/>.
###############################################################################
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from bwp.contrib.abstracts.models import AbstractGroup
from bwp.contrib.contacts.models import Org, Client
from bwp.conf import settings

class Template(models.Model):
    """ Шаблоны документов """

    DOCUMENT_CHOICES = (
        ('001', _('Contract')),
        ('002', _('Invoice')),
        ('003', _('Act')),
    )
    title = models.CharField(
            max_length=255,
            verbose_name = _('title'))
    document = models.CharField(
            max_length=3,
            choices=DOCUMENT_CHOICES,
            verbose_name = _('type of document'))
    is_default = models.BooleanField(
            default=True,
            verbose_name = _('by default'))
    webodt = models.FileField(upload_to=settings.WEBODT_TEMPLATE_PATH,
            blank=True,
            verbose_name = _('template of webodt'))
    text = models.TextField(
            blank=True,
            verbose_name = _('template'))

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title', 'document' ]
        verbose_name = _('template')
        verbose_name_plural = _('templates')

    def save(self, **kwargs):
        if self.is_default:
            docs = TemplateDoc.objects.filter(document=self.document, is_default=True)
            docs.update(is_default=False)
        super(Template, self).save(**kwargs)
