import pytest
from unittest.mock import patch, Mock, MagicMock

from decimal import Decimal
from application.db_communication import DB_Communication
from application.ui_app import UI_App
from application.user import User
from application.validation_utility import ValidationUtility
from application.order import Order
from application.delivery import Delivery


@pytest.fixture
def mock_db():
    db = Mock(spec=DB_Communication)
    db.cursor = Mock()
    db.conn = Mock()
    return db


@pytest.fixture
def user():
    return User(1, 'test_login', 'password123', 'test@example.com', '1234567890', 'John', 'Doe', 'user')


@pytest.mark.parametrize("value, expected", [
    ("safe_input", True),
    ("SELECT * FROM users", False),
    ("pass1; DROP TABLE users", False),
    ("sdffsdfsd-- comment", False),
])
def test_validate_for_sql_injection(value, expected):
    assert ValidationUtility.validate_for_sql_injection(value) == expected


@pytest.mark.parametrize("value, max_length, expected", [
    ("short_string", 20, True),
    ("a" * 21, 20, False),
    (123, 20, False),
])
def test_validate_varchar(value, max_length, expected):
    assert ValidationUtility.validate_varchar(value, max_length) == expected


@pytest.mark.parametrize("value, max_length, expected", [
    ("12345", 5, True),
    ("123456", 5, False),
    ("abc", 5, False),
])
def test_validate_integer(value, max_length, expected):
    assert ValidationUtility.validate_integer(value, max_length) == expected


@pytest.mark.parametrize("value, expected", [
    ("12.34", True),
    ("5232132.45", False),
    ("abc", False),
])
def test_validate_decimal(value, expected):
    assert ValidationUtility.validate_decimal(value) == expected


def test_display_attributes(capsys, user):
    user.display_attributes()
    captured = capsys.readouterr()
    assert (
               'Login: test_login\nEmail: test@example.com\nPhone: 1234567890\nName: John\nSurname: Doe\nRole: user\n') in captured.out


@patch('builtins.input', side_effect=["newemail@example.com", "", "John", ""])
def test_update_attributes(mock_input):
    db_mock = MagicMock()
    user = User(1, 'testuser', 'password', 'test@example.com', '1234567890', 'Jane', 'Doe', 'customer')
    user.update_attributes(db_mock)
    assert user.email == "newemail@example.com"
    assert user.name == "John"


def test_user_menu_exit(mocker, user, mock_db):
    mocker.patch('builtins.input', side_effect=['4'])
    assert user.user_menu(mock_db) == 4


@patch('builtins.input', side_effect=["Test City", "Test Street", "123", "12345", "Test Country"])
def test_insert_new_delivery(mock_input):
    db_mock = MagicMock()
    delivery = Delivery()
    delivery.insert_new_delivery(db_mock)


def test_fetch_orders_by_user():
    db_mock = MagicMock()
    user_id = 1
    expected_orders = [
        (1, 100, 'completed', 'card', '2024-01-01', 'City', 'Street', 123, '12345', 'Country', 'Cotton', 'M', 'Male',
         50.0, 'Summer Collection', '2024-01-01', '2024-06-01')
    ]
    db_mock.cursor.fetchall.return_value = expected_orders
    Order.fetch_orders_by_user(db_mock, user_id)
    assert user_id in Order.orders


def test_cancel_order_success():
    db_mock = MagicMock()
    order_id = 1
    Order.cancel_order(db_mock, order_id)
    db_mock.cursor.callproc.assert_called_with("CancelOrder", [order_id])
    db_mock.conn.commit.assert_called_once()


@patch('builtins.input', side_effect=["new_user33", "password123"])
def test_complete_order_workflow(mock_input):
    db_mock = MagicMock()
    db_mock.cursor.fetchone.side_effect = [
        ("3", "new_user33", "password123", "new.user@example.com", "123-456-7890", "Bob", "Doe", "customer"),
    ]

    app = UI_App()
    app.db = db_mock
    assert app.login()
    db_mock.cursor.fetchone.side_effect = [
        (Decimal("60.00"), 3, 3, 3),
    ]
    Order.add_new_order(db_mock, Decimal("60.00"), 3, 3, 3)
    db_mock.cursor.callproc.assert_called_with("addOrder", [Decimal("60.00"), 3, 3, 3])
