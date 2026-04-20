from django.db.models import DateTimeField


class DateTimeWithoutTZField(DateTimeField):
    # Return a "timestamp without timezone" instead of "timestamp with timezone"
    def db_type(self, connection):
        return 'timestamp'
