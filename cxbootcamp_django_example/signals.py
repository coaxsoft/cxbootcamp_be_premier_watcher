from django_elasticsearch_dsl.signals import BaseSignalProcessor


class FakeSignalProcessor(BaseSignalProcessor):
    """Fake signal processor

    Exists but doesn't save the model to the index
    every time you save model in the DB. In mostly
    cases it should be used for tests only
    """

    def setup(self):
        # Listen to all model saves.
        pass

    def teardown(self):
        # Listen to all model saves.
        pass
