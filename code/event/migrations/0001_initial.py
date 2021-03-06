# Generated by Django 2.2.16 on 2020-10-25 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableTickets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_type', models.CharField(choices=[('VIP', 'VIP'), ('REG', 'Regular'), ('DIS', 'Discounted')], max_length=3, verbose_name='Ticket type')),
                ('price', models.IntegerField(verbose_name='Price in EUR')),
                ('amount', models.IntegerField(verbose_name='Pool of tickets')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Event name')),
                ('date', models.DateField(verbose_name='Event date and time')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Reservation creation datetime')),
                ('amount', models.IntegerField(default=1)),
                ('validated', models.BooleanField(default=False, verbose_name='Reservation paid')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='event.AvailableTickets', verbose_name="Ticket that's reserved")),
            ],
        ),
        migrations.AddField(
            model_name='availabletickets',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='event.Event', verbose_name='Event'),
        ),
    ]
