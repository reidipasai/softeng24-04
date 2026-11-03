se2404 logout
se2404 login --username admin --passw freepasses4all
se2404 healthcheck
se2404 resetpasses
se2404 healthcheck
se2404 resetstations
se2404 healthcheck
se2404 admin --addpasses --source passes04.csv
se2404 healthcheck
se2404 tollstationpasses --station AM08 --from 20220101 --to 20220114 --format json
se2404 tollstationpasses --station NAO04 --from 20220101 --to 20220114 --format csv
se2404 tollstationpasses --station NO01 --from 20220101 --to 20220114 --format csv
se2404 tollstationpasses --station OO03 --from 20220101 --to 20220114 --format csv
se2404 tollstationpasses --station XXX --from 20220101 --to 20220114 --format csv
se2404 tollstationpasses --station OO03 --from 20220101 --to 20220114 --format YYY
se2404 errorparam --station OO03 --from 20220101 --to 20220114 --format csv
se2404 tollstationpasses --station AM08 --from 20220102 --to 20220112 --format json
se2404 tollstationpasses --station NAO04 --from 20220102 --to 20220112 --format csv
se2404 tollstationpasses --station NO01 --from 20220102 --to 20220112 --format csv
se2404 tollstationpasses --station OO03 --from 20220102 --to 20220112 --format csv
se2404 tollstationpasses --station XXX --from 20220102 --to 20220112 --format csv
se2404 tollstationpasses --station OO03 --from 20220102 --to 20220112 --format YYY
se2404 passanalysis --stationop AM --tagop NAO --from 20220101 --to 20220114 --format json
se2404 passanalysis --stationop NAO --tagop AM --from 20220101 --to 20220114 --format csv
se2404 passanalysis --stationop NO --tagop OO --from 20220101 --to 20220114 --format csv
se2404 passanalysis --stationop OO --tagop KO --from 20220101 --to 20220114 --format csv
se2404 passanalysis --stationop XXX --tagop KO --from 20220101 --to 20220114 --format csv
se2404 passanalysis --stationop AM --tagop NAO --from 20220102 --to 20220112 --format json
se2404 passanalysis --stationop NAO --tagop AM --from 20220102 --to 20220112 --format csv
se2404 passanalysis --stationop NO --tagop OO --from 20220102 --to 20220112 --format csv
se2404 passanalysis --stationop OO --tagop KO --from 20220102 --to 20220112 --format csv
se2404 passanalysis --stationop XXX --tagop KO --from 20220102 --to 20220112 --format csv
se2404 passescost --stationop AM --tagop NAO --from 20220101 --to 20220114 --format json
se2404 passescost --stationop NAO --tagop AM --from 20220101 --to 20220114 --format csv
se2404 passescost --stationop NO --tagop OO --from 20220101 --to 20220114 --format csv
se2404 passescost --stationop OO --tagop KO --from 20220101 --to 20220114 --format csv
se2404 passescost --stationop XXX --tagop KO --from 20220101 --to 20220114 --format csv
se2404 passescost --stationop AM --tagop NAO --from 20220102 --to 20220112 --format json
se2404 passescost --stationop NAO --tagop AM --from 20220102 --to 20220112 --format csv
se2404 passescost --stationop NO --tagop OO --from 20220102 --to 20220112 --format csv
se2404 passescost --stationop OO --tagop KO --from 20220102 --to 20220112 --format csv
se2404 passescost --stationop XXX --tagop KO --from 20220102 --to 20220112 --format csv
se2404 chargesby --opid NAO --from 20220101 --to 20220114 --format json
se2404 chargesby --opid GE --from 20220101 --to 20220114 --format csv
se2404 chargesby --opid OO --from 20220101 --to 20220114 --format csv
se2404 chargesby --opid KO --from 20220101 --to 20220114 --format csv
se2404 chargesby --opid NO --from 20220101 --to 20220114 --format csv
se2404 chargesby --opid NAO --from 20220102 --to 20220112 --format json
se2404 chargesby --opid GE --from 20220102 --to 20220112 --format csv
se2404 chargesby --opid OO --from 20220102 --to 20220112 --format csv
se2404 chargesby --opid KO --from 20220102 --to 20220112 --format csv
se2404 chargesby --opid NO --from 20220102 --to 20220112 --format csv
