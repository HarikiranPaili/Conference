# Generated by Django 4.0.1 on 2022-06-03 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmpMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('Empid', models.IntegerField(blank=True, null=True)),
                ('emp_name', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.IntegerField(blank=True, null=True)),
                ('dept_code', models.CharField(blank=True, max_length=200, null=True)),
                ('college_code', models.CharField(blank=True, max_length=200, null=True)),
                ('campus', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
