# Generated by Django 3.0.1 on 2019-12-20 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_datetime', models.DateTimeField(verbose_name='voting date and time')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='voting_system',
            field=models.CharField(choices=[('M', 'Majoritarian'), ('S', 'Schulze')], default='M', max_length=1),
        ),
        migrations.CreateModel(
            name='VoteChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveSmallIntegerField(verbose_name='choice ranking')),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Choice')),
                ('vote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Vote')),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Question'),
        ),
    ]
