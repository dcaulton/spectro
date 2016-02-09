# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-09 02:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limits_exceeded_action', models.CharField(choices=[('send_email', 'Send email to group members'), ('take_another_reading', 'Take another reading'), ('none', 'take no action')], max_length=32)),
            ],
            options={
                'db_table': 'group_limit',
            },
        ),
        migrations.CreateModel(
            name='GroupMatchCandidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'group_match_candidate',
            },
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('role', models.CharField(choices=[('access_webapp', 'Access web application'), ('receive_notifications', 'Receive notifications'), ('take_samples', 'Take samples'), ('configure_group', 'Configure group')], max_length=32)),
            ],
            options={
                'db_table': 'group_member',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('elevation', models.FloatField()),
                ('datetime', models.FloatField()),
                ('number_of_satellites', models.IntegerField()),
            ],
            options={
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=1024)),
            ],
            options={
                'db_table': 'photo',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reading_type', models.CharField(choices=[('spectro', 'Spectrometer'), ('color', 'Color'), ('fluoro', 'Fluorescence')], max_length=32)),
                ('record_type', models.CharField(choices=[('Physical', 'Physical'), ('Virtual', 'Virtual'), ('Defined', 'Derived')], max_length=32)),
                ('description', models.CharField(max_length=4096)),
                ('average_magnitude', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'sample',
            },
        ),
        migrations.CreateModel(
            name='SampleData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.IntegerField()),
                ('magnitude', models.IntegerField()),
            ],
            options={
                'db_table': 'sample_data',
            },
        ),
        migrations.CreateModel(
            name='SampleDelta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'sample_delta',
            },
        ),
        migrations.CreateModel(
            name='SampleFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_type', models.CharField(choices=[('peak', 'Peak'), ('valley', 'Valley'), ('spike', 'Spike'), ('hole', 'Hole'), ('plateau_start', 'Start of Plateau'), ('plateau_end', 'End of Plateau')], max_length=32)),
                ('sharpness', models.IntegerField()),
                ('magnitude', models.IntegerField()),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sample')),
            ],
            options={
                'db_table': 'sample_feature',
            },
        ),
        migrations.CreateModel(
            name='SampleMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(default=0.0)),
                ('delta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.SampleDelta')),
                ('reference_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samplematch_reference_sample', to='api.Sample')),
                ('source_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samplematch_source_sample', to='api.Sample')),
            ],
            options={
                'db_table': 'sample_match',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('description', models.CharField(max_length=4096)),
            ],
            options={
                'db_table': 'subject',
            },
        ),
        migrations.CreateModel(
            name='VoiceMemo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=1024)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sample')),
            ],
            options={
                'db_table': 'voice_memo',
            },
        ),
        migrations.RenameField(
            model_name='settings',
            old_name='group_id',
            new_name='current_group',
        ),
        migrations.AddField(
            model_name='group',
            name='parent_group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='api.Group'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='post_capture_processing',
            field=models.CharField(choices=[('find_match', 'Search for a match'), ('check_limits', 'Compare to upper and lower limits'), ('none', 'No post capture processing')], default='find_match', max_length=32),
        ),
        migrations.AddField(
            model_name='group',
            name='reading_type',
            field=models.CharField(choices=[('spectro', 'Spectrometer'), ('color', 'Color'), ('fluoro', 'Fluorescence')], default='spectro', max_length=32),
        ),
        migrations.AddField(
            model_name='group',
            name='try_composite_candidates',
            field=models.BooleanField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='use_photo',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='use_voice_memo',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sampledelta',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group'),
        ),
        migrations.AddField(
            model_name='sampledelta',
            name='reference_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sampledelta_reference_sample', to='api.Sample'),
        ),
        migrations.AddField(
            model_name='sampledelta',
            name='source_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sampledelta_source_sample', to='api.Sample'),
        ),
        migrations.AddField(
            model_name='sampledata',
            name='delta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.SampleDelta'),
        ),
        migrations.AddField(
            model_name='sampledata',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sample'),
        ),
        migrations.AddField(
            model_name='sample',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group'),
        ),
        migrations.AddField(
            model_name='sample',
            name='representative_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sample'),
        ),
        migrations.AddField(
            model_name='sample',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Subject'),
        ),
        migrations.AddField(
            model_name='photo',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sample'),
        ),
        migrations.AddField(
            model_name='location',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group'),
        ),
        migrations.AddField(
            model_name='location',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sample'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group'),
        ),
        migrations.AddField(
            model_name='groupmatchcandidate',
            name='group_id_of_reference_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reference_sample_group', to='api.Group'),
        ),
        migrations.AddField(
            model_name='groupmatchcandidate',
            name='group_id_of_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_sample_group', to='api.Group'),
        ),
        migrations.AddField(
            model_name='grouplimit',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group'),
        ),
        migrations.AddField(
            model_name='grouplimit',
            name='lower_limit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lower_limit', to='api.Sample'),
        ),
        migrations.AddField(
            model_name='grouplimit',
            name='upper_limit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upper_limit', to='api.Sample'),
        ),
        migrations.AddField(
            model_name='group',
            name='subject',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='api.Subject'),
            preserve_default=False,
        ),
    ]
