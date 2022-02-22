# Generated by Django 3.2.6 on 2022-02-13 17:10

from django.db import migrations


def copy_destinations_to_phone_number_table(apps, schema_editor):
    PhoneNumber = apps.get_model("argus_auth", "PhoneNumber")
    DestinationConfig = apps.get_model("argus_notificationprofile", "DestinationConfig")
    db_alias = schema_editor.connection.alias

    for destination in DestinationConfig.objects.filter(media_id="sms"):
        PhoneNumber.objects.using(db_alias).create(
            user=destination.user,
            phone_number=destination.settings["phone_number"],
        )


class Migration(migrations.Migration):

    dependencies = [
        ("argus_notificationprofile", "0008_remove_media_phone_number"),
        ("argus_auth", "0002_alter_user_first_name"),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, copy_destinations_to_phone_number_table),
        migrations.DeleteModel(
            name="PhoneNumber",
        ),
    ]
