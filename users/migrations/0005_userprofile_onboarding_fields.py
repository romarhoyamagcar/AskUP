from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_message_message_type_conversation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='show_onboarding',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='onboarding_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
