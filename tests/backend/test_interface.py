from unittest import TestCase

from ragger import Firmware, ApplicationError
from ragger.backend import BackendInterface


class DummyBackend(BackendInterface):
    def __enter__(self): yield self
    def __exit__(self, *args, **kwargs): pass
    def both_click(self): pass
    def right_click(self): pass
    def left_click(self): pass
    def exchange_async_raw(self, *args, **kwargs): pass
    def exchange_raw(self, *args, **kwargs): pass
    def receive(self): pass
    def send_raw(self, *args, **kwargs): pass


class TestBackendInterface(TestCase):

    def setUp(self):
        self.firmware = Firmware('nanos', '2.0.1')
        self.errors = (ApplicationError(0x8888, 'ERROR1'),
                       ApplicationError(0x7777, 'ERROR2'))
        self.valid_statuses = (0x9000, 0x9001, 0x9002)
        self.backend = DummyBackend(self.firmware,
                                    valid_statuses=self.valid_statuses,
                                    errors=self.errors)

    def test_init(self):
        self.assertEqual(self.backend.firmware, self.firmware)
        self.assertIsNone(self.backend.last_async_response)
        self.assertFalse(self.backend.raises)
        for status in self.valid_statuses:
            self.assertTrue(self.backend.is_valid(status))

        backend = DummyBackend(self.firmware, raises=True)
        self.assertTrue(backend.raises)
        self.assertTrue(backend.is_valid(0x9000))
        for status in self.valid_statuses[1:]:
            self.assertFalse(backend.is_valid(status))

    def test__raise_unmanaged_error(self):
        error = ApplicationError(0x9999, data='error not managed')
        with self.assertRaises(ApplicationError) as thrown_error:
            self.backend._raise(error.status, error.data)
        self.assertEqual(error, thrown_error.exception)

    def test__raise_managed_error(self):
        indice = 0
        data = 'this error is managed'
        error = ApplicationError(self.errors[indice].status, data=data)
        expected = ApplicationError(self.errors[indice].status,
                                    self.errors[indice].name,
                                    data)
        with self.assertRaises(ApplicationError) as thrown_error:
            self.backend._raise(error.status, error.data)
        self.assertEqual(expected, thrown_error.exception)
