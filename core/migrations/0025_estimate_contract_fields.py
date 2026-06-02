from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_companyprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="estimate",
            name="contract_number",
            field=models.CharField(
                db_index=True,
                max_length=100,
                verbose_name="Номер договора",
                default="TEMP-CONTRACT",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="estimate",
            name="contract_estimate_number",
            field=models.PositiveIntegerField(
                verbose_name="Номер сметы по договору",
                default=1,
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="estimate",
            constraint=models.UniqueConstraint(
                fields=("contract_number", "contract_estimate_number"),
                name="unique_estimate_per_contract_number",
            ),
        ),
    ]