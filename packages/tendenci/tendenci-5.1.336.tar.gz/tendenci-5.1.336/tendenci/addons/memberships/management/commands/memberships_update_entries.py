from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    example: python manage.py memberships_update_entries
    """
    def handle(self, *args, **kwargs):
        from tendenci.addons.memberships.models import AppEntry, AppFieldEntry, AppField

        try:
            corp_field = AppField.objects.get(field_type='corporate_membership_id')
        except AppField.DoesNotExist:
            return False

        entries = AppEntry.objects.filter(membership__gt=0)

        print 'entries', entries.count()

        for i, entry in enumerate(entries):
            corp_id = entry.get_field_value('corporate_membership_id')

            if corp_id.isdigit():
                continue  # this one is good; on to the next one

            if not entry.membership:
                continue  # on to the next one

            value = entry.membership.corporate_membership_id

            app_field_entry = AppFieldEntry.objects.create(
                entry=entry,
                field=corp_field,
                value=value,
            )

            if kwargs['verbosity'] > 0:
                print entry.pk, app_field_entry, value
