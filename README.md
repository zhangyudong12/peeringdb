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

# File list
peeringdb.py - main script

script_cmd_output.txt - report output from script

asn_report.json - report in json format 

ix_net_report.json - report in json format 

peeringdb_test.py - unit test result capture

unit_test_outport.txt - unit test result capture 

flask_app.py - web app script

main_page.html - jinja2 based HTML file

mysql_records.txt - web app test result capture 

web_report.png - screen capture of web report page

## License
[MIT](https://choosealicense.com/licenses/mit/)
