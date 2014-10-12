# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table(u'page_page', (
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, primary_key=True)),
            ('title_en', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('title_de', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('body_en', self.gf('django.db.models.fields.TextField')()),
            ('body_de', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'page', ['Page'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table(u'page_page')


    models = {
        u'page.page': {
            'Meta': {'object_name': 'Page'},
            'body_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'body_en': ('django.db.models.fields.TextField', [], {}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'primary_key': 'True'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['page']