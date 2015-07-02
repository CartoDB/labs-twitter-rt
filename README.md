# labs-twitter-rt
Template project to feed a table from Twitter using GNIP and our Power Track library.

This app uses CartoDB Powertrack library to interact with GNIP API. All the configuration should be placed on the `app.conf` and `powertrack.conf`.

Steps to set up the application:

1. Create a virtualenvironment called `env`
2. Configure your account details, categories, etc on the `conf` files
3. The`folder` parameter at `powertrack.conf` has to be the same of the script
4. Run the `initial_import.py` script and ensure the table has been populated on your cartodb account.
5. Run the `app.py` script and check new data is being added to the original table and temp files and tables are being removed correctly.
5. [OPTIONAL] Set up monit using the example file so it takes care it's running
