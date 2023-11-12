# Readme

The idea of this project is to pull reports out of ProductBoard on a per-customer basis. If you were to bring up 
Productboard in front of a customer to show feature request status you very well may expose other customer data.
This is less than ideal.

By running `create_report.py` and supplying a bearer token for authentication it will pull all components, features, 
and notes and assemble an Excel file. To use it in your org you may need to tweak it a bit.

This was created with Python 3.11 but should work with earlier versions of 3.x.

Released and maintained under MIT License