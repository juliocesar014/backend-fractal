# Generated by Django 5.1.3 on 2024-11-21 22:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_participant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.choice')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.participant')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='api.question')),
            ],
            options={
                'unique_together': {('participant', 'question')},
            },
        ),
    ]