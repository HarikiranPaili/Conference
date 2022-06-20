# Generated by Django 4.0.1 on 2022-06-02 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reviewer', '0001_initial'),
        ('scholar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewerscores',
            name='proposal_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scholar.proposal'),
        ),
        migrations.AddField(
            model_name='reviewerscores',
            name='ques',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviewer.reviewerquestions'),
        ),
        migrations.AddField(
            model_name='reviewerscores',
            name='reviewer_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviewer.reviewer'),
        ),
        migrations.AddField(
            model_name='reviewer',
            name='proposal_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scholar.proposal'),
        ),
    ]
