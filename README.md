# peeringdb.py

executable script

peeringdb_ms.py - multi-threading version script, test script not applied

## Usage

python peeringdb.py

python peeringdb_ms.py

# Input
ASN number :

output to file y/n ?

# Output

total IXs, total peers, total unique peering organizations, aggregate peering speed,peerings network list per IX, orgination list which has more connection points

asn_report.json file

ix_net_report.json file

report on screen ( when "output to file" is not checked)

script_cmd_output.txt file (when "output to file" is checked)


# web app

## website
http://zhangyudong12.pythonanywhere.com/

## environment 

flask + mysql

## Input
asn_report.json file

ix_net_report.json file

## Output

Create mysql table "asns" and "ixs"

Insert non-duplicated record to mysql table

Render the template with mysql data

Display ASN and IX report in table format

# File list
peeringdb.py - main script

script_cmd_output.txt - report output from script

asn_report.json - report in json format 

ix_net_report.json - report in json format 

peeringdb_test.py - unit test script

unit_test_outport.txt - unit test result capture file

flask_app.py - web app script

main_page.html - jinja2 based HTML file

mysql_records.txt - sql command line output 

web_report.png - screen shot of web app

# PeeringDB API reference
https://www.peeringdb.com/api/net?asn=xxx | net?id=xxx

{"data": [{"id": 1956, "org_id": 12067, "name": "Twitch", "aka": "Twitch, TwitchTV, Justin.tv", "name_long": "", "website": "http://www.twitch.tv", "asn": 46489, "looking_glass": "", "route_server": "", "irr_as_set": "AS-TWITCH", "info_type": "Content", "info_prefixes4": 30, "info_prefixes6": 10, "info_traffic": "", "info_ratio": "Heavy Outbound", "info_scope": "Global", "info_unicast": true, "info_multicast": false, "info_ipv6": true, "info_never_via_route_servers": false, "ix_count": 62, "fac_count": 83, "notes": "", "netixlan_updated": "2021-07-03T00:11:44.060382Z", "netfac_updated": "2021-06-03T18:00:31.712382Z", "poc_updated": "2021-03-19T20:17:08.757350Z", "policy_url": "", "policy_general": "Selective", "policy_locations": "Preferred", "policy_ratio": false, "policy_contracts": "Not Required", "netfac_set": [{"id": 5805, "name": "Equinix DC1-DC15 - Ashburn", "city": "Ashburn", "country": "US", "fac_id": 1, "local_asn": 46489, "created": "2010-07-29T00:00:00Z", "updated": "2016-03-14T21:22:38Z", "status": "ok"}], "netixlan_set": [{"id": 68272, "ix_id": 30, "name": "JPIX TOKYO", "ixlan_id": 30, "notes": "", "speed": 100000, "asn": 46489, "ipaddr4": "210.171.225.162", "ipaddr6": "2001:de8:8::4:6489:2", "is_rs_peer": false, "operational": true, "created": "2021-06-28T06:07:37Z", "updated": "2021-07-02T03:07:05Z", "status": "ok"}], "poc_set": [], "allow_ixp_update": false, "created": "2008-10-13T18:38:24Z", "updated": "2020-07-02T03:47:58Z", "status": "ok"}], "meta": {}}

https://www.peeringdb.com/api/ix?name=xxx

{"data": [{"id": 2, "org_id": 2, "name": "Equinix Chicago", "aka": "", "name_long": "Equinix Internet Exchange Chicago", "city": "Chicago", "country": "US", "region_continent": "North America", "media": "Ethernet", "notes": "", "proto_unicast": true, "proto_multicast": false, "proto_ipv6": true, "website": "https://ix.equinix.com", "url_stats": "", "tech_email": "support@equinix.com", "tech_phone": "", "policy_email": "support@equinix.com", "policy_phone": "", "net_count": 247, "fac_count": 3, "ixf_net_count": 0, "ixf_last_import": null, "service_level": "Not Disclosed", "terms": "Not Disclosed", "created": "2010-07-29T00:00:00Z", "updated": "2020-12-08T14:58:33Z", "status": "ok"}], "meta": {}}

https://www.peeringdb.com/api/netixlan?ix_id=xxx

{"data": [{"id": 68183, "net_id": 17741, "ix_id": 2, "name": "Equinix Chicago", "ixlan_id": 2, "notes": "", "speed": 10000, "asn": 13786, "ipaddr4": "208.115.137.205", "ipaddr6": "2001:504:0:4:0:1:3786:1", "is_rs_peer": true, "operational": true, "created": "2021-06-24T11:05:08Z", "updated": "2021-06-24T11:05:08Z", "status": "ok"}], "meta": {}}


## License
[MIT](https://choosealicense.com/licenses/mit/)
