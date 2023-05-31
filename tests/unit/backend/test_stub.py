from unittest import TestCase

from ragger.backend import BackendInterface
from ragger.backend.stub import StubBackend


class TestStubBackend(TestCase):

    def test_can_instantiate(self):
        stub = StubBackend(None)
        self.assertIsInstance(stub, BackendInterface)
