import argparse
import pytest
import tempfile

from collections import defaultdict

from cli_paymentdata.cli_read_csv import PurchaseCreator, CustomerCreator


# ----------------------------------- #
# Purchases
# ----------------------------------- #


@pytest.fixture(scope="session")
def purchase_csv():
    # Create temporary CSV files for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as purchases_file:
        purchases_file.write(
            b"purchase_identifier;customer_id;product_id;quantity;price;currency;date\n2/01;2;1221;1;10;EUR;2017-12-31"
        )
    return purchases_file


@pytest.fixture(scope="session")
def example_purchases_csv_bad():
    # Create temporary CSV files for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as purchases_file:
        purchases_file.write(
            b"purchase_identifier;customer_id;product_id;quantity;price;currency;date\n5/01;5;5678;1;10;AUD;2022-01-01\n1/01;1;4324;1;10;EUR;2030-12-31"
        )
    return purchases_file


@pytest.fixture(scope="session")
def pc(purchase_csv):
    return PurchaseCreator(purchase_csv.name)


@pytest.fixture(scope="session")
def example_purchases_csv_row_good():
    return {
        "purchase_identifier": "2/01",
        "customer_id": 2,
        "product_id": "9999",
        "quantity": 1,
        "price": 10.0,
        "currency": "EUR",
        "date": "2080-12-31",
    }


@pytest.fixture(scope="session")
def example_purchases_csv_row_bad():
    return {
        "purchase_identifier": "3/08",
        "customer_id": "",
        "product_id": "8888",
        "quantity": "1",
        "price": "99",
        "currency": "AUD",
        "date": "2001-12-31",
    }


@pytest.fixture(scope="session")
def example_purchases_csv_row_formatted():
    return {
        "product_id": "9999",
        "quantity": 1,
        "price": 10.0,
        "currency": "EUR",
        "purchased_at": "2080-12-31",
    }


@pytest.fixture(scope="session")
def example_purchases_per_customer_dic():
    purchase_dict = {
        2: [
            {
                'product_id': '1221',
                'quantity': 1,
                'price': 10.0,
                'currency': 'EUR',
                'purchased_at': '2017-12-31'
            },
            {
                'product_id': '3213',
                'quantity': 1,
                'price': 10.0,
                'currency': 'EUR',
                'purchased_at': '2030-12-31'
            }
        ],
        1: [
            {
                'product_id': '4324',
                'quantity': 1,
                'price': 10.0,
                'currency': 'EUR',
                'purchased_at': '2030-12-31'
            }
        ],
        3: [
            {
                'product_id': '75672',
                'quantity': 1,
                'price': 10.0,
                'currency': 'USD',
                'purchased_at': '2050-12-31'
            },
            {
                'product_id': '2123',
                'quantity': 1,
                'price': 10.0,
                'currency': 'EUR',
                'purchased_at': '2017-08-01'
            }
        ]
    }
    return defaultdict(list, purchase_dict)


# ----------------------------------- #
# Customers
# ----------------------------------- #

@pytest.fixture(scope="session")
def customer_csv_path():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as customers_file:
        customers_file.write(
            b"customer_id;title;lastname;firstname;email\n1;2;Doe;John;johndoe@example.com"
        )
    return customers_file


@pytest.fixture(scope="session")
def customer_csv_path_bad():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as customers_file:
        customers_file.write(
            b"customer_id;title;lastname;firstname;email\n1;2;Doe;John;"
        )
    return customers_file


@pytest.fixture(scope="session")
def cc(customer_csv_path):
    return CustomerCreator(customer_csv_path.name)


@pytest.fixture(scope="session")
def example_customer_csv_row_good():
    return {
        "customer_id": "5",
        "title": "2",
        "lastname": "Dupont",
        "firstname": "Eric",
        "postal_code": "21000",
        "city": "Dijon",
        "email": "eric.dupont@bourgogne.fr",
    }


@pytest.fixture(scope="session")
def example_customer_csv_row_formatted():
    return {
        "salutation": "M",
        "last_name": "Dupont",
        "first_name": "Eric",
        "email": "eric.dupont@bourgogne.fr",
    }


@pytest.fixture(scope="session")
def example_customers_dic():
    customer_dic = {
        1: {
            'salutation': 'M',
            'last_name': 'Norris',
            'first_name': 'Chuck',
            'email': 'chuck@norris.com'
        },
        2: {
            'salutation': 'Mme',
            'last_name': 'Galante',
            'first_name': 'Marie',
            'email': 'marie-galante@france.fr'
        },
        3: {
            'salutation': 'M',
            'last_name': 'Barbier',
            'first_name': 'Christophe',
            'email': 'christophe@fake.email'
        },
        4: {
            'salutation': 'Mme',
            'last_name': '',
            'first_name': '',
            'email': ''
        },
        5: {
            'salutation': 'M',
            'last_name': 'Dupont',
            'first_name': 'Eric',
            'email': 'eric.dupont@bourgogne.fr'
        }
    }

    return defaultdict(list, customer_dic)


@pytest.fixture(scope="session")
def payload_example():
    return [
        {
            "salutation": "Mme",
            "last_name": "Galante",
            "first_name": "Marie",
            "email": "marie-galante@france.fr",
            "purchases": [
                [
                    {
                        "product_id": "1221",
                        "quantity": 1,
                        "price": 10.0,
                        "currency": "EUR",
                        "purchased_at": "2017-12-31",
                    },
                    {
                        "product_id": "3213",
                        "quantity": 1,
                        "price": 10.0,
                        "currency": "EUR",
                        "purchased_at": "2030-12-31",
                    },
                ]
            ],
        },
        {
            "salutation": "M",
            "last_name": "Norris",
            "first_name": "Chuck",
            "email": "chuck@norris.com",
            "purchases": [
                [
                    {
                        "product_id": "4324",
                        "quantity": 1,
                        "price": 10.0,
                        "currency": "EUR",
                        "purchased_at": "2030-12-31",
                    }
                ]
            ],
        },
        {
            "salutation": "M",
            "last_name": "Barbier",
            "first_name": "Christophe",
            "email": "christophe@fake.email",
            "purchases": [
                [
                    {
                        "product_id": "75672",
                        "quantity": 1,
                        "price": 10.0,
                        "currency": "USD",
                        "purchased_at": "2050-12-31",
                    },
                    {
                        "product_id": "2123",
                        "quantity": 1,
                        "price": 10.0,
                        "currency": "EUR",
                        "purchased_at": "2017-08-01",
                    },
                ]
            ],
        },
    ]
