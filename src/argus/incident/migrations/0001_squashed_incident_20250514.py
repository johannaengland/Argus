# Generated by Django 5.2 on 2025-05-14 12:29

import argus.incident.fields
import argus.incident.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('argus_incident', '0001_initial'), ('argus_incident', '0002_empty_source_incident_id'), ('argus_incident', '0003_incident_level'), ('argus_incident', '0004_add_ChangeEvent_proxy'), ('argus_incident', '0005_alter_event_type'), ('argus_incident', '0006_incident_search_text'), ('argus_incident', '0007_alter_event_type'), ('argus_incident', '0008_incident_metadata'), ('argus_incident', '0009_use_bigautofield_on_quickly_growing_tables')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('received', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.TextField(choices=[('STA', 'Incident start'), ('END', 'Incident end'), ('CHI', 'Incident change'), ('CLO', 'Close'), ('REO', 'Reopen'), ('ACK', 'Acknowledge'), ('OTH', 'Other'), ('LES', 'Stateless')])),
                ('description', models.TextField(blank=True)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='caused_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(help_text='The time the incident was created.')),
                ('end_time', argus.incident.fields.DateTimeInfinityField(blank=True, help_text="The time the incident was resolved or closed. If not set, the incident is stateless; if 'infinity' is checked, the incident is stateful, but has not yet been resolved or closed - i.e. open.", null=True)),
                ('source_incident_id', models.TextField(blank=True, default='', verbose_name='source incident ID')),
                ('details_url', models.TextField(blank=True, validators=[django.core.validators.URLValidator], verbose_name='details URL')),
                ('description', models.TextField(blank=True)),
                ('ticket_url', models.TextField(blank=True, help_text='URL to existing ticket in a ticketing system.', validators=[django.core.validators.URLValidator], verbose_name='ticket URL')),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='IncidentRelationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SourceSystemType',
            fields=[
                ('name', models.TextField(primary_key=True, serialize=False, validators=[argus.incident.validators.validate_lowercase])),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Acknowledgement',
            fields=[
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='ack', serialize=False, to='argus_incident.event')),
                ('expiration', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-event__timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(validators=[argus.incident.validators.validate_key])),
                ('value', models.TextField()),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('key', 'value'), name='tag_unique_key_and_value')],
            },
        ),
        migrations.CreateModel(
            name='SourceSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('base_url', models.TextField(blank=True, help_text="Base url to combine with an incident's relative url to point to more info in the source system.")),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='argus_incident.sourcesystemtype')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='source_system', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IncidentTagRelation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('added_time', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags_added', to=settings.AUTH_USER_MODEL)),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_tag_relations', to='argus_incident.incident')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_tag_relations', to='argus_incident.tag')),
            ],
        ),
        migrations.CreateModel(
            name='IncidentRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('incident1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='argus_incident.incident')),
                ('incident2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='argus_incident.incident')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='incident_relations', to='argus_incident.incidentrelationtype')),
            ],
        ),
        migrations.AddField(
            model_name='incident',
            name='source',
            field=models.ForeignKey(help_text='The source system that the incident originated in.', on_delete=django.db.models.deletion.PROTECT, related_name='incidents', to='argus_incident.sourcesystem'),
        ),
        migrations.AddField(
            model_name='event',
            name='incident',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events', to='argus_incident.incident'),
        ),
        migrations.AddConstraint(
            model_name='sourcesystem',
            constraint=models.UniqueConstraint(fields=('name', 'type'), name='sourcesystem_unique_name_per_type'),
        ),
        migrations.AddConstraint(
            model_name='incidenttagrelation',
            constraint=models.UniqueConstraint(fields=('tag', 'incident'), name='incidenttagrelation_unique_tags_per_incident'),
        ),
        migrations.AddConstraint(
            model_name='incident',
            constraint=models.UniqueConstraint(condition=models.Q(('source_incident_id__gt', '')), fields=('source_incident_id', 'source'), name='incident_unique_source_incident_id_per_source'),
        ),
        migrations.AddField(
            model_name='incident',
            name='level',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5),
        ),
        migrations.CreateModel(
            name='ChangeEvent',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('argus_incident.event',),
        ),
        migrations.AddField(
            model_name='incident',
            name='search_text',
            field=models.TextField(blank=True, default='', verbose_name='Search Text'),
        ),
        migrations.AddField(
            model_name='incident',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
