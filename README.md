# peeringdb.py

executable script

## Usage

python peeringdb.py

# Input
ASN number

output to file Y/N ?

# Output
asn_report.json

ix_net_report.json

report on screen ( when output to file is not checked)

script_cmd_output.txt (when output to file is checked)


# web app

## environment 

flask + mysql

## Input
asn_report.json

ix_net_report.json

## Output

Create mysql table "asns" and "ixs"

Insert non-duplicated record to mysql table

Render the template using data from mysql

Display ASN and IX report in table format



## License
[MIT](https://choosealicense.com/licenses/mit/)
