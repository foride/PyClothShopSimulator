import re
from decimal import Decimal, InvalidOperation


class ValidationUtility:

    @staticmethod
    def validate_for_sql_injection(value):

        patterns = [
            r'--',  # SQL comment
            r';',  # Statement separator
            r'\/\*',  # Multi-line comment
            r'\bOR\b', '\bAND\b',  # Logical operators
            r'[\s\r\n]*\bDROP\b', r'[\s\r\n]*\bTABLE\b', r'[\s\r\n]*\bINSERT\b',  # DDL/DML keywords
            r'[\s\r\n]*\bDELETE\b', r'[\s\r\n]*\bUPDATE\b',
            r'[\s\r\n]*\bSELECT\b', r'[\s\r\n]*\bFROM\b',
            r'EXEC\(', r'EXECUTE\('  # Executing stored procedures/functions
        ]

        if any(re.search(pattern, value, re.IGNORECASE) for pattern in patterns):
            print(f"Potentially harmful input detected: '{value}'. Please try again.")
            return False
        return True

    @staticmethod
    def validate_varchar(value, max_length):
        if not isinstance(value, str) or len(value) > max_length:
            print(f"String value exceeds the max allowed length of {max_length}. Please try again.")
            return False
        return True

    @staticmethod
    def validate_integer(value, max_length):
        try:

            int_value = int(value)

            if len(str(abs(int_value))) > max_length:
                print(f"Integer value exceeds the max allowed length of {max_length} digits. Please try again.")
                return False

            return True
        except ValueError:
            print(f"Value '{value}' is not a valid integer. Please try again.")
            return False

    @staticmethod
    def validate_decimal(value):
        try:

            decimal_value = Decimal(value)
            decimal_value = decimal_value.quantize(Decimal('0.00'))

            sign, digits, exponent = decimal_value.as_tuple()

            digits_before_decimal = len(digits) + exponent if exponent < 0 else len(digits)
            digits_after_decimal = -exponent if exponent < 0 else 0

            if digits_before_decimal > 6 or digits_after_decimal > 2:
                print(
                    "Value must be a decimal number with up to 6 digits before and 2 digits after the decimal point. "
                    "Please try again.")
                return False

            return True
        except (InvalidOperation, ValueError):
            print(f"Value '{value}' is not a valid decimal number. Please try again.")
            return False

    @staticmethod
    def get_validated_input_varchar(prompt, max_length):
        while True:
            user_input = input(prompt)
            if (ValidationUtility.validate_varchar(user_input, max_length) and
                    ValidationUtility.validate_for_sql_injection(user_input)):
                return user_input

    @staticmethod
    def get_validated_input_integer(prompt, max_length):
        while True:
            user_input = input(prompt)
            if ValidationUtility.validate_integer(user_input, max_length):
                return int(user_input)

    @staticmethod
    def get_validated_input_decimal(prompt):
        while True:
            user_input = input(prompt)
            if ValidationUtility.validate_decimal(user_input):
                return Decimal(user_input).quantize(Decimal('0.00'))
