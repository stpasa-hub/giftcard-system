from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0002_fix_bonus_points_column"),  # falls deine 0002 so heisst
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="bonus_points",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="merchant",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

