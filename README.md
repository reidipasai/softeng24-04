![backend tests](https://github.com/ntua/softeng24-04/actions/workflows/ubuntu-tests.yml/badge.svg)
![cli build](https://github.com/ntua/softeng24-04/actions/workflows/cli-build.yml/badge.svg)
![pre-commit](https://github.com/ntua/softeng24-04/actions/workflows/pre-commit.yml/badge.svg)

# TollSync: Interoperable Data Hub for Highway Networks
<div align="center">
  <img src="https://github.com/ntua/softeng24-04/blob/main/assets/tollsync_logo.png" alt="tollsync">
</div>
TollSync is a RESTful API system for Greek toll stations management. It supports a wide range of operations such as live passes addition,
charges computation, automated reports, data analysis and much more. You can use TollSync either with our CLI(see bellow) or using our GUI.
For the **full documentation**, please visit out OpenAPI 3.0 documentation at `/api/docs`, once you run the backend.

### Example:
```bash
se2404 login --username toll_user --password toll_password
se2404 resetstations
se2404 admin --addpasses --source random_passes.csv
se2404 passanalysis --stationop AM --tagop NAO --from 20220305 --to 20220319 --format json
se2404 tollstationpasses --station AM08 --from 20220306 --to 20220317 --format json
....
```

## CLI

The CLI specifics are well documented at [CLI documentation](cli_client/README.md). There are no differences from using the GUI, our CLI offers
a simpler and more efficient interaction with more experienced users.

## GUI

Our frontend is not yet deployed as we are still in prototype testing. The frontend specifics are well documented at [frontend documentation](front-end/README.md).

## Reporting

Every week, the final cost is computed for each toll company and an e-mail is sent to all of the companies regarding the amount of money that one 
owes to each other. You can see an example of this e-mail bellow:
<div align="center">
  <img src="https://github.com/ntua/softeng24-04/blob/main/assets/reporting_example.png" alt="reporting_example">
</div>

## Contact

For more information, please contact our core team:
  - el21834@mail.ntua.gr
  - el21801@mail.ntua.gr
  - el22813@mail.ntua.gr
  - el21110@mail.ntua.gr
  - el21076@mail.ntua.gr

## For Developers

Contributions are welcome! Please make sure to write tests for any new code and run them before submitting a pull request.
If you find a bug, please open an issue describing how to duplicate it.
