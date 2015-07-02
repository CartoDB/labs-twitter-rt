# labs-twitter-rt
Template project to feed a table from Twitter using GNIP and our Power Track library.

This app uses CartoDB Powertrack library to interact with GNIP API. All the configuration should be placed on the `app.conf` and `powertrack.conf`.

Steps to set up the application at our script server

1. Clone the repo with a proper name:
   ```
   git clone git@github.com:CartoDB/labs-twitter-rt.git beer
   ```
2. Create a virtualenvironment called `env` and activate it
3. Install the dependencies with `pip install -r requirements.txt`
4. Configure your account details, categories, etc on the `conf` files (copy from `.example` and adjust). Note the`folder` parameter at `powertrack.conf` has to be the same of the script
5. Run the `initial_import.py` script and ensure the table has been populated on your cartodb account.
6. Run the `app.py` script and check new data is being added to the original table and temp files and tables are being removed correctly.
7. Set up monit linking the `monit.conf` file to the configuration files folder
   ```
   ln -s /home/sm/scripts/beer/monit.conf /etc/monit/conf.d/beer
   ```

