#!/usr/bin/env python

# Author: Boris Zhang

# Purpose: Generate a peeringDB state report for a specific network

import requests
import json
import ipaddress
import sys

apiurl = 'https://www.peeringdb.com/api/'

# Comppatible for both python2 and python3
def get_input(prompt=''):
    try:
        line = raw_input(prompt)
    except NameError:
        line = input(prompt)
    return line


def fetchResults(url):
    try:
        response = requests.get(url)
        response = json.loads(response.text)
    except:
        print("Error: Didn't receive a valid response when calling %s" % url)
        exit(1)
    return response


def lookupNet(search):
    url = "%snet?id=%s" % (apiurl, search)
    results = fetchResults(url)
    return results['data'][0]['name']


# input:asn, output:IX list and network aggrerate speed of all IXs
def getIX(search):
    url = "%snet?asn=%s&depth=2" % (apiurl, search)
    results = fetchResults(url)
    ix_speed = 0
    ix_list = []
    for key in sorted(results['data'][0]):
        if key == 'netixlan_set':
            for ixlan in results['data'][0][key]:
                ix_speed = ix_speed + int(ixlan['speed'])
                url = "%six?ixlan_id=%s" % (apiurl, ixlan['ixlan_id'])
                ix_results = fetchResults(url)
                ix_list.append(ix_results['data'][0]['name'])
    return ix_list,ix_speed


# input:IX name and asn, output:sorted network list exclude the input asn
def findPeerings(search, asn):
    # match exact name
    url = "%six?name=%s" % (apiurl, search)
    results = fetchResults(url)
    net_list = []
    for ix in results['data']:
        ix_id = ix['id']
        url2 = "%snetixlan?ix_id=%s" % (apiurl, ix_id)
        results2 = fetchResults(url2)
        for net in results2['data']:
            if net['asn'] != asn:
                net_name = lookupNet(net['net_id'])
                net_list.append(net_name)
    net_list.sort()
    return net_list


def main():
    asn_report = dict()
    asn = int(get_input('Enter Network AS number: '))

    print_to_file = get_input('Print the output to file y/n ?: ')
    if print_to_file.upper() == 'Y':
        orig_stdout = sys.stdout
        f = open('script_cmd_output.txt', 'w')
        sys.stdout = f

    ix_list_asn, total_agg_speed_m = getIX(asn)
    ix_list_asn.sort()
    total_agg_speed = total_agg_speed_m/1000
    total_ix = len(ix_list_asn)
    print('~' * 79)
    print(f"Network with ASN = {asn} exists in {total_ix} exchanging points")
    print('~' * 79)
    print('\n'.join(ix_list_asn))
    print('~' * 79)
    print(f"Total Aggregate speed =  {total_agg_speed}Gbps")
    asn_report = {"ASN":asn,"Total_agg_speed(Gbps)":total_agg_speed}

    all_peers = dict()
    for ix in ix_list_asn:
        all_peers[ix] = findPeerings(ix,asn)
        sub_total_peers = len(all_peers[ix])
        print('~' * 79)
        print(f"Internet Exchange: {ix}  Total peers : {sub_total_peers}")
        print('~' * 79)
        print('\n'.join(all_peers[ix]))

    mergedlist = []
    for ix in all_peers:
        mergedlist.extend(all_peers[ix])
    mergedlist.sort()
    total_peers = len(mergedlist)
    print('~' * 79)
    print(f"Total peering's = {total_peers}")
    mergedset = set(mergedlist)
    total_organizations = len(mergedset)
    print('~' * 79)
    print(f"Total unique organization peering's = {total_organizations}")
    asn_report["Total_peers"]  = total_peers
    asn_report["Total_organizations"] = total_organizations

    print('\n\n')
    print("Additional information : ")
    print('~' * 79)
    peer_count = {org: mergedlist.count(org) for org in mergedset}
    for peer, count in peer_count.items():
        if count > 1:
            print(f"{peer} : number of connection points  {count}")
        else:
            continue

    with open('asn_report.json','w') as json_file1:
        json.dump(asn_report, json_file1, indent=2)
    json_file1.close()

    with open('ix_net_report.json','w') as json_file2:
        json.dump(all_peers, json_file2, indent=2)
    json_file2.close()


if __name__ == "__main__":
    main()




""" Note:

 1 The specific Org might have more than one peer connections in one or more IXs.
 The additional information provides the Orgs list and nummber of connections

 2 The output json file will be exported to mysql database used for web app

 3 The peeringdb output is nested dictionary. some data need to be retrived from inner dict()

 4 Ocationally the peeringDB API server doesn't respond to https request, that will interupt the running script.
   this will occurs likely when the network being queried has widely distributed in >100 IXs

 5 Use asn = 49909 for quick test as it only exists at 3x IXs.


"""
