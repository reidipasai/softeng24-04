# CLI client

## Installation

To install the CLI, just do the following in the root directory:
```bash
pip install -e .
```

Then, you can use any of our available API calls using the CLI intstead of our GUI. You can see all the available calls bellow.

## API calls

### Register
Registers a new user to the database
```bash
se2404 register --username [username] --password [password] --role [Admin or Employee]
```

### Login
Performs login
```bash
se2404 login --username [username] --password [password]
```

### Logout
Performs logout
```bash
se2404 logout
```

### Healthcheck
Performs a healtcheck communication with the database, also, returns some information about the database [ADMIN PRIVILEGES NEEDED].
```bash
se2404 healthcheck
```

### Getstations
Returns a json or csv file with all the tollstations information [ADMIN PRIVILEGES NEEDED].
```bash
se2404 getstations --format [format]
```

### Resetstations
Deletes every object from tollstations and fills the tollstations object with the new data [ADMIN PRIVILEGES NEEDED].
```bash
se2404 resetstations
```

### Chargesby
Returns a json or csv file with data about the passes that happened from users with different.
```bash
se2404 chargesby --opid [op] --from [datefrom] --to [dateto] --format [format]
```

### Passanalysis
Returns a json or csv file with data about the total passes.
```bash
se2404 passanalysis --stationop [stationop] --tagop [tagop] --from [datefrom] --to [dateto] --format [format]
```

### Passescost
Returns a json or csv file with data about the passes that happened from users with tagOpID on the stations with tollOpID.
```bash
se2404 passescost --stationop [tollop] --tagop [tagop] --from [datefrom] --to [dateto] --format [format]
```

### Tollstationpasses
Returns a json or csv file with data about the tollstation passes of the passed tollstation ID from date_from to date_to.
```bash
se2404 tollstationpasses --station [station] --from [datefrom] --to [dateto] --format [format]
```

You can always see more information by running `se2404` on your terminal.

## Debugging and errors

If for some reason(let's say, testing purposes) delete everything from the database, then the CLI will tell you that the connected user's token is missing. Don't worry about
this message, you can try again right after, the CLI will remove everything from the session and will fetch the database info.

## Testing

Unit and functinal tests are available at the `tests` subfolder. You can run them using the `pytest` command.
CLI tests are part of our GitHub's automated tests and will always be tested on PR's.
```bash
cd tests && pytest
```
