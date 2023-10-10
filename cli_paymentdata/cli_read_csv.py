import argparse
import csv
import json
import jsonschema
import logging
import requests
import os

from collections import defaultdict
from typing import Union, Dict, List


class PurchaseCreator:
    def __init__(self, purchases_file: str):
        self.purchases_file: str = purchases_file
        self.bad_purchase_data: defaultdict = defaultdict(list)
        self.puchases_per_customer: defaultdict = self.read_purchase_csv()

    def _format_purchase_data(
        self,
        row: Dict[str, str],
    ) -> Dict[str, Union[str, int, float]]:
        """
        Format purchase data to the required format for the API.
        """
        purchase_data: Dict[str, Union[str, int, float]] = {}
        for key, value in row.items():
            if key == "product_id":
                purchase_data[key] = str(value)
            if key == "price":
                purchase_data[key] = float(value)
            elif key == "currency":
                purchase_data[key] = str(value)
            elif key == "quantity":
                purchase_data[key] = int(value)
            elif key == "date":
                purchase_data["purchased_at"] = str(value)
        return purchase_data

    def read_purchase_csv(self) -> defaultdict:
        """
        Read the purchase CSV file and return a defaultdict with `customer_id: list of purchases`.
        """
        with open(self.purchases_file) as p:
            purchases_list = list(csv.DictReader(p, delimiter=";"))

        puchases_per_customer: defaultdict = defaultdict(list)
        for row in purchases_list:
            # Extract needed data for API payload
            purchase_data = self._format_purchase_data(row)
            valid = self._validate_purchase_data(purchase_data)
            if valid:
                # Add purchase to the customer
                puchases_per_customer[row.get("customer_id")].append(purchase_data)
            else:
                self.bad_purchase_data[row.get("customer_id")].append(row)
        return puchases_per_customer

    def _validate_purchase_data(self, purchase: Dict) -> Union[Dict, None]:
        """
        Validate the purchase data against a schema.
        """

        purchase_schema = {
            "type": "object",
            "properties": {
                "price": {"type": "integer"},
                "currency": {
                    "type": "string",
                    "enum": ["USD", "EUR", "GBP"],
                },
                "quantity": {"type": "integer"},
                "purchased_at": {
                    "type": "string",
                    "format": "date",
                    "pattern": "^(\\d{4}-\\d{2}-\\d{2})$",
                },
            },
            "required": ["product_id", "price", "currency", "quantity", "purchased_at"],
        }

        try:
            jsonschema.validate(purchase, purchase_schema)
            return purchase
        except jsonschema.ValidationError as e:
            print(
                f"Schema validation error: {e} in {purchase}. Skipping this purchase."
            )
            logging.error(
                f"Schema validation error: {e} in {purchase}. Skipping this purchase."
            )
        return None

    def export_bad_data(self) -> None:
        """
        Dump bad purchase data to a JSON file.
        """
        bad_purchase_data_dict: Dict[str, Union[str, int, float]] = dict(
            self.bad_purchase_data
        )  # pragma: no cover

        bad_file = "reports/bad_purchases.json"
        with open(bad_file, "w") as json_file:
            json.dump(bad_purchase_data_dict, json_file)
        if len(bad_purchase_data_dict) > 0:
            logging.warn(
                f"n bad purchase entries found: {len(bad_purchase_data_dict)} // exported to {bad_file}"
            )
        else:
            logging.info(
                f"No bad purchase data found // exported empty file to {bad_file}"
            )


class CustomerCreator:
    def __init__(self, customers_file: str):
        self.customers_file: str = customers_file
        self.salutation: dict = {"1": "Mme", "2": "M", None: "", "": ""}
        self.customer_dic: list = []
        self.bad_customer_data: defaultdict = defaultdict(list)

    def _format_customer_data(self, row: Dict) -> Dict:
        """
        Format customer data to the required format for the API.
        """

        customer_data = {
            "salutation": self.salutation[row.get("title", "")],
            "last_name": row.get("lastname", ""),
            "first_name": row.get("firstname", ""),
            "email": row.get("email", ""),
        }

        # Convert missing data (None) to empty string
        customer_data = {k: v if v else "" for k, v in customer_data.items()}
        return customer_data

    def read_customer_csv(self) -> defaultdict:
        """
        Assume that the customer data is unique.
        """
        with open(self.customers_file) as c:
            customers_reader = csv.DictReader(c, delimiter=";")
            customers_list = list(customers_reader)

        customer_data: defaultdict = defaultdict(dict)
        for customer in customers_list:
            formatted_customer_data = self._format_customer_data(customer)
            valid_data = self._validate_customer_data(formatted_customer_data)

            if valid_data:
                customer_data[
                    customer.get("customer_id")
                ] = formatted_customer_data  # noqa: E501
            else:
                self.bad_customer_data[customer.get("customer_id")].append(
                    customer
                )  # noqa: E501
        return customer_data

    def _validate_customer_data(
        self,
        customer_data: Dict,
    ) -> Union[Dict, None]:
        """
        Validate the customer data against a schema.
        """

        customer_schema = {
            "type": "object",
            "properties": {
                "salutation": {
                    "type": "string",
                    "enum": ["M", "Mme", ""],
                },
                "last_name": {"type": "string"},
                "first_name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
            },
            "required": ["salutation", "last_name", "first_name", "email"],
        }
        try:
            jsonschema.validate(customer_data, customer_schema)
            return customer_data
        except jsonschema.ValidationError as e:
            print(f"Schema validation error: {e}")
            logging.error(
                f"Schema validation error: {e} in {customer_data}. \
                    Skipping this purchase."
            )
        return None

    def export_bad_data(self) -> None:
        """
        Dump bad customer data to a JSON file.
        """
        bad_customers_data_dict = dict(self.bad_customer_data)
        bad_file = "reports/bad_customers.json"
        with open(bad_file, "w") as json_file:
            json.dump(bad_customers_data_dict, json_file)
        if len(bad_customers_data_dict) > 0:
            logging.warn(
                f"n bad customer with purchases entries found:\
                    {len(bad_customers_data_dict)} // exported to {bad_file}"
            )
        else:
            logging.info(
                f"No bad customer with purchases found // \
                    exported empty fileto {bad_file}"
            )


class PayloadCreator:
    @staticmethod
    def get_payload(
        customers_dic: defaultdict, purchases_per_customer: defaultdict
    ) -> List[Dict]:
        """
        Get the payload for the API.
        """

        payload = []
        for customer_id in purchases_per_customer:
            final_dict = customers_dic[customer_id]
            final_dict["purchases"] = [purchases_per_customer[customer_id]]
            payload.append(final_dict)
        return payload


def make_request(payload: List[Dict], env):
    """
    Send the payload to the API.
    """

    if env in ["dev", "test"]:
        url = f"https://{env}.myhostname.com/v1/customers/"
    elif env == "prod":
        url = "https://myhostname.com/v1/customers/"
    else:
        msg = f"Environment {env} not supported. Please use 'dev', 'test' or 'prod'."  # noqa: E501
        logging.error(msg)
        raise ValueError(msg)

    # Save JSON payload locally
    with open("reports/payload.json", "w") as json_file:
        json.dump(payload, json_file)

    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        msg = "In-flight payment data sent successfully to the API."
        logging.info(msg)
    else:
        msg = f"Failed to send in-flight payment data. \
            Status code: {response.status_code}"
        logging.error(msg)
    print(msg)
    return response.json()


def run():
    if not os.path.exists("reports"):
        os.makedirs("reports")

    logging.basicConfig(
        filename="reports/cli_paymentdata.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Send CSV files to API")
    parser.add_argument(
        "-p",
        "--purchases",
        required=True,
        type=str,
        help="Path to a CSV file containing purchase data.",
    )
    parser.add_argument(
        "-c",
        "--customers",
        required=True,
        type=str,
        help="Path to a CSV file containing customer data.",
    )
    parser.add_argument(
        "-e",
        "--env",
        type=str,
        nargs="?",
        default="dev",
        choices=["dev", "test", "prod"],
        help="Environment to use.",
    )

    args = parser.parse_args()

    logging.info(f"# --- Starting the script with arguments: {args} --- #")

    if not args.purchases or not args.customers:
        msg_files = (
            "Provide 2 paths to CSV files: one for purchases and one for customers."
        )
        print(msg_files)
        logging.warning(msg_files)
        return None

    if not args.purchases.endswith(".csv"):
        msg_p = "Please provide a valid path to a CSV file containing purchase data."
        print(msg_p)
        logging.warning(msg_p)
        if not args.customers.endswith(".csv"):
            msg_c = (
                "Please provide a valid path to a CSV file containing customer data."
            )
            print(msg_c)
            logging.warning(msg_c)
        return None

    purchases = PurchaseCreator(args.purchases)
    purchases_per_customer = purchases.read_purchase_csv()

    customers = CustomerCreator(args.customers)
    customers_dic = customers.read_customer_csv()

    payload = PayloadCreator().get_payload(customers_dic, purchases_per_customer)

    msg = f"Sending payload to the API: {len(payload)} customers with purchases"  # noqa: E501
    logging.info(msg)
    print(msg)

    make_request(payload, args.env)

    purchases.export_bad_data()
    customers.export_bad_data()


if __name__ == "__main__":
    run()
