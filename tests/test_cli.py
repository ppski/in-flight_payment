import jsonschema
import pytest

from collections import defaultdict
from requests_mock import Mocker

from cli_paymentdata.cli_read_csv import (
    CustomerCreator,
    PurchaseCreator,
    PayloadCreator,
    make_request,
)

# ----------------------------------- #
# PurchaseCreator Tests
# ----------------------------------- #


def test_format_purchase_data_good(
    pc, example_purchases_csv_row_good, example_purchases_csv_row_formatted
):
    formatted_purchase_data = pc._format_purchase_data(example_purchases_csv_row_good)

    assert list(formatted_purchase_data.keys()) == [
        "product_id",
        "quantity",
        "price",
        "currency",
        "purchased_at",
    ]
    assert formatted_purchase_data == example_purchases_csv_row_formatted


def test_format_purchase_data_bad(pc, example_purchases_csv_row_bad):
    formatted_purchase_data = pc._format_purchase_data(example_purchases_csv_row_bad)
    assert list(formatted_purchase_data.keys()) == [
        "product_id",
        "quantity",
        "price",
        "currency",
        "purchased_at",
    ]


def test_read_purchase_csv(pc):
    result = pc.read_purchase_csv()
    assert len(result) == 1
    assert isinstance(result, defaultdict)


def test_read_purchase_csv_bad_purchase_data(example_purchases_csv_bad):
    pc_bad = PurchaseCreator(example_purchases_csv_bad.name)
    with pytest.raises(jsonschema.ValidationError):
        pc_bad.read_purchase_csv()
        raise jsonschema.ValidationError("Schema validation error")


def test_validate_purchase_data(pc, example_purchases_csv_row_formatted):
    result = pc._validate_purchase_data(example_purchases_csv_row_formatted)
    assert result == example_purchases_csv_row_formatted


# Test unformatted row data (good row, bad API data)
def test_validate_purchase_data_schema_fail(pc, example_purchases_csv_row_good):
    with pytest.raises(jsonschema.ValidationError):
        pc._validate_purchase_data(example_purchases_csv_row_good)
        raise jsonschema.ValidationError("Schema validation error")


# ----------------------------------- #
# CustomerCreator Tests
# ----------------------------------- #
def test_format_customer_data(
    cc, example_customer_csv_row_good, example_customer_csv_row_formatted
):
    formatted_customer_data = cc._format_customer_data(example_customer_csv_row_good)
    assert list(formatted_customer_data.keys()) == [
        "salutation",
        "last_name",
        "first_name",
        "email",
    ]
    assert formatted_customer_data == example_customer_csv_row_formatted


def test_read_customer_csv(cc):
    result = cc.read_customer_csv()
    assert len(result) == 1
    assert isinstance(result, defaultdict)


# Test unformatted row data (good row, bad API data)
def test_validate_customer_data(cc, example_customer_csv_row_good):
    with pytest.raises(jsonschema.ValidationError):
        cc._validate_customer_data(example_customer_csv_row_good)
        raise jsonschema.ValidationError("Schema validation error")


def test_read_customer_csv_bad_customer_data(customer_csv_path_bad):
    cc_bad = CustomerCreator(customer_csv_path_bad.name)
    with pytest.raises(jsonschema.ValidationError):
        cc_bad.read_customer_csv()
        raise jsonschema.ValidationError("Schema validation error")


# ----------------------------------- #
# PayloadCreator Tests
# ----------------------------------- #


def test_get_payload(example_customers_dic, example_purchases_per_customer_dic, payload_example):
    result = PayloadCreator.get_payload(
        example_customers_dic, example_purchases_per_customer_dic
    )
    print("HELLO")
    print(result)
    print(example_customers_dic)
    print(example_purchases_per_customer_dic)
    assert result == payload_example

# ----------------------------------- #
# Request Tests
# ----------------------------------- #


@pytest.mark.parametrize("env", ["dev", "test"])
def test_make_request_dev(payload_example, env):
    mock = Mocker(real_http=True)
    expected_response = {"status": "success", "data": payload_example, "message": None}
    url = f"https://{env}.myhostname.com/v1/customers/"
    mock.put(url, json=expected_response)
    with mock:
        api_response = make_request(payload_example, env)
        assert api_response == expected_response


def test_make_request_prod(capfd, payload_example):
    mock = Mocker(real_http=True)
    expected_response = {"status": "success", "data": payload_example, "message": None}
    env = "prod"
    url = "https://myhostname.com/v1/customers/"
    mock.put(url, json=expected_response)
    with mock:
        api_response = make_request(payload_example, env)
        assert api_response == expected_response
        out, err = capfd.readouterr()
        assert "data sent successfully" in out


@pytest.mark.parametrize("env", ["fake"])
def test_make_request_fake(capfd, payload_example, env):
    mock = Mocker(real_http=True)
    expected_response = {"status": "success", "data": payload_example, "message": None}
    url = f"https://{env}.myhostname.com/v1/customers/"
    mock.put(url, json=expected_response)
    with mock:
        with pytest.raises(ValueError):
            api_response = make_request(payload_example, env)
            assert api_response == expected_response
            out, err = capfd.readouterr()
            assert "Failed" in out
