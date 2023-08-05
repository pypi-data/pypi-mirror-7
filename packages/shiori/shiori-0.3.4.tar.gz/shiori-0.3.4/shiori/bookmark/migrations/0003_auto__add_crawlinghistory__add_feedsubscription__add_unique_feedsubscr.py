# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CrawlingHistory'
        db.create_table('crawling_history', (
            ('id', self.gf('shortuuidfield.fields.ShortUUIDField')(max_length=22, primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.FeedSubscription'])),
            ('update_datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'bookmark', ['CrawlingHistory'])

        # Adding model 'FeedSubscription'
        db.create_table('feed_subscription', (
            ('id', self.gf('shortuuidfield.fields.ShortUUIDField')(max_length=22, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('default_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bookmark.Category'])),
        ))
        db.send_create_signal(u'bookmark', ['FeedSubscription'])

        # Adding unique constraint on 'FeedSubscription', fields ['url', 'owner']
        db.create_unique('feed_subscription', ['url', 'owner_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FeedSubscription', fields ['url', 'owner']
        db.delete_unique('feed_subscription', ['url', 'owner_id'])

        # Deleting model 'CrawlingHistory'
        db.delete_table('crawling_history')

        # Deleting model 'FeedSubscription'
        db.delete_table('feed_subscription')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'bookmark.bookmark': {
            'Meta': {'unique_together': "(('url', 'owner'),)", 'object_name': 'Bookmark', 'db_table': "'bookmark'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bookmark.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('shortuuidfield.fields.ShortUUIDField', [], {'max_length': '22', 'primary_key': 'True'}),
            'is_hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'registered_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['bookmark.Tag']", 'through': u"orm['bookmark.BookmarkTag']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'bookmark.bookmarktag': {
            'Meta': {'unique_together': "(('bookmark', 'tag'),)", 'object_name': 'BookmarkTag', 'db_table': "'bookmark_tag'"},
            'bookmark': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bookmark.Bookmark']", 'db_column': "'bookmark_id'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bookmark.Tag']", 'db_column': "'tag_id'"})
        },
        u'bookmark.category': {
            'Meta': {'object_name': 'Category', 'db_table': "'category'"},
            'category': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('shortuuidfield.fields.ShortUUIDField', [], {'max_length': '22', 'primary_key': 'True'})
        },
        u'bookmark.crawlinghistory': {
            'Meta': {'object_name': 'CrawlingHistory', 'db_table': "'crawling_history'"},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bookmark.FeedSubscription']"}),
            'id': ('shortuuidfield.fields.ShortUUIDField', [], {'max_length': '22', 'primary_key': 'True'}),
            'update_datetime': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'bookmark.feedsubscription': {
            'Meta': {'unique_together': "(('url', 'owner'),)", 'object_name': 'FeedSubscription', 'db_table': "'feed_subscription'"},
            'default_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bookmark.Category']"}),
            'id': ('shortuuidfield.fields.ShortUUIDField', [], {'max_length': '22', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'bookmark.tag': {
            'Meta': {'object_name': 'Tag', 'db_table': "'tag'"},
            'id': ('shortuuidfield.fields.ShortUUIDField', [], {'max_length': '22', 'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bookmark']