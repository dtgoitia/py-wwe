## Architecture

I want to know:
- total hours left to complete my 7.5h per day (today)
- total hours missing/exceeded today at 4pm

Bear in mind:
- Bank holidays (if any)
- Start date
- Personal holidays (if any)
- Both personal and bank holidays can be added in advance, but they will be ignored until they become relevant
- Bank holidays left


## Proposed architecture

- Leverage Bank Holidays and Personal Holidays to Google Calendar (integration needed)
- Bank Holidays left can be calculated by only storing how many are you entitled to, and then looking up on Google Calendar
- Start date is something that needs to be stored to.

Therefore, to have specific models (storage) would be:
 - Start date
 - Personal bank Holiday days you are entitled to in a year
 - How many hours a week you need to work
 - When you want to be out