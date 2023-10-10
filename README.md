# in-flight_payment
A package for reading in-flight payment and customer data in and sending it to an API.


## Installation

In the root directory of the project, run:

```
pip install -r requirements.txt
pip install . 
```


## How to run

You must provide 2 `;` delimited CSV files to run the command:

```
inflightpayment -c path/to/customer/csv -p path/to/payment/csv
```

The default option sends data to the dev endpoint. Use `inflightpayment --help` for a full list of options. 

## Reports

In the `/reports` directory, you can find a report:

- `cli_paymentdata.log`: logs
- `payload.json`: data sent to the API
- `bad_purchases.json`: any "bad" rows in the purchases CSV.
- `bad_customers.json`: any "bad" rows in the customer CSV for customers with purchases. "Bad" rows without purchases are not included.