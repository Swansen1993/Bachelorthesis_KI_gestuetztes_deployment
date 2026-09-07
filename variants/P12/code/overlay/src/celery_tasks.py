class _EmailStub:
    def delay(self, recipients, subject, body):
        return None

    def apply_async(self, args, kwargs=None, **options):
        return None


send_email = _EmailStub()
