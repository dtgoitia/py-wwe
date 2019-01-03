Config
-------

The configuration file ``~/.config/wwe/config.json`` file.

.. code-block:: json

  {
    "toggl_token": "MY_TOGGL_TOKEN",
    "personal_holidays": [
      ["2018-06-08", 0.5],
      ["2018-06-20", 1],
    ],
    "company_bonus_days": [
      ["2018-12-24", 1],
      ["2018-12-31", 1]
    ],
    "client": {
      "name": "CLIENT_NAME",
      "start_date": "2018-02-05"
    },
    "working_day_hours": 7.5
}

where:

- ``MY_TOGGL_TOKEN``: token that grants you access to Toggl's API.
- ``CLIENT_NAME``: client from which you want to count the hours. All the
  working hours to account for should be under this client in Toggl.

Architecture
------------

I want to know:
- total hours left to complete my 7.5h per day (today)
- total hours missing/exceeded today at 4pm

Bear in mind:
- Bank holidays (if any)
- Start date
- Personal holidays (if any)
- Both personal and bank holidays can be added in advance, but they will be
  ignored until they become relevant.
- Bank holidays left.


Proposed architecture
------------------------

- Leverage Bank Holidays and Personal Holidays to Google Calendar (integration
  needed)
- Bank Holidays left can be calculated by only storing how many are you
  entitled to, and then looking up on Google Calendar
- Start date is something that needs to be stored to.

Therefore, to have specific models (storage) would be:

- Start date
- Personal bank Holiday days you are entitled to in a year
- How many hours a week you need to work
- When you want to be out

Configuration file
------------------

The `wwe` command will look for the file `.wweconfig.json` in the `HOME` directory.

TODO
----

- Add types to existing codebase.
- Implement `vulture` to find dead code.
- Add more unit tests.
