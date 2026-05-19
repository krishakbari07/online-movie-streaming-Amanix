from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_movies_movie_backdrop_webseries_backdrop'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebSeriesEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('upcoming', 'Upcoming'), ('live', 'Live'), ('archived', 'Archived')], default='upcoming', max_length=20)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('cta_label', models.CharField(blank=True, help_text='Optional call-to-action label', max_length=80)),
                ('cta_url', models.URLField(blank=True, help_text='Link for the CTA button')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('webseries', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='app.webseries')),
            ],
            options={
                'verbose_name': 'Web Series Event',
                'verbose_name_plural': 'Web Series Events',
                'ordering': ('-start_time',),
            },
        ),
        migrations.CreateModel(
            name='WebSeriesRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Optional override title', max_length=150)),
                ('short_note', models.CharField(blank=True, help_text='Short note shown to viewers', max_length=280)),
                ('priority', models.PositiveIntegerField(default=0, help_text='Lower value = higher priority')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('recommended_webseries', models.ForeignKey(help_text='Web series to promote in this slot', on_delete=django.db.models.deletion.CASCADE, related_name='recommended_entries', to='app.webseries')),
                ('source_webseries', models.ForeignKey(help_text='Web series detail page where this recommendation should appear', on_delete=django.db.models.deletion.CASCADE, related_name='curated_recommendations', to='app.webseries')),
            ],
            options={
                'verbose_name': 'Web Series Recommendation',
                'verbose_name_plural': 'Web Series Recommendations',
                'ordering': ('priority', '-updated_at'),
                'unique_together': {('source_webseries', 'recommended_webseries')},
            },
        ),
        migrations.AddIndex(
            model_name='webseriesevent',
            index=models.Index(fields=['webseries', 'status'], name='app_webserie_webseri_9a4590_idx'),
        ),
        migrations.AddIndex(
            model_name='webseriesevent',
            index=models.Index(fields=['-start_time'], name='app_webserie_start_t_cb170a_idx'),
        ),
        migrations.AddIndex(
            model_name='webseriesrecommendation',
            index=models.Index(fields=['source_webseries', 'priority'], name='app_webserie_source__17e1b0_idx'),
        ),
    ]

