from django.test import TestCase
from .validators import validate_codice_fiscale, validate_partita_iva
from django.core.exceptions import ValidationError


class ValidateCodiceFiscaleTestCase(TestCase):
    def test_codice_fiscale_vuoto(self):
        self.assertRaises(
            ValidationError,
            validate_codice_fiscale,
            ''
        )

    def test_codice_fiscale_16(self):
        self.assertRaises(
            ValidationError,
            validate_codice_fiscale,
            '1234567890123456'
        )

    def test_codice_fiscale_controllo(self):
        self.assertRaises(
            ValidationError,
            validate_codice_fiscale,
            'ABCDEF00A00A000A'
        )


class ValidatePartitaIva(TestCase):
    def test_partita_iva_vuota(self):
        self.assertRaises(
            ValidationError,
            validate_partita_iva,
            ''
        )

    def test_partita_iva_non_numerica(self):
        self.assertRaises(
            ValidationError,
            validate_partita_iva,
            'ABC123DEF45'
        )

    def test_partita_iva_controllo(self):
        self.assertRaises(
            ValidationError,
            validate_partita_iva,
            '12345678901'
        )
