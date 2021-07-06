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
                net_name_alias = 'AS_' + str(net['asn']) + '_' + net_name
                net_list.append(net_name_alias)
    net_list.sort()
    return net_list


def print_report(title,input_dict,flag,input_lenth):
    print('~' * 79)
    print(title)
    print('~' * 79)
    if flag == 'join':
        for key,value in input_dict.items():
            print(f"IX: {key}   Peering's : {input_lenth}")
            print('\n'.join(value))
    else:
        for key,value in input_dict.items():
            print (key,value)


def export_file(file_name,contents):
    with open(file_name, 'w') as json_file:
        json.dump(contents, json_file, indent=2)
    json_file.close()


def main():
    asn = int(get_input('Enter Network AS number: '))
    print_to_file = get_input('Print the output to file y/n ?: ')
    if print_to_file.upper() == 'Y':
        orig_stdout = sys.stdout
        f = open('script_cmd_output.txt', 'w')
        sys.stdout = f

    asn_report = dict()
    ix_list_asn, total_agg_speed_m = getIX(asn)
    ix_list_asn.sort()
    ix_set_asn = set(ix_list_asn)
    total_agg_speed = total_agg_speed_m/1000
    total_ix = len(ix_set_asn)
    print('~' * 79)
    print(f"Network with ASN = {asn} exists in {total_ix} exchanging points \n")
    print('\n'.join(ix_set_asn))

    all_peers = dict()
    for ix in ix_set_asn:
        all_peers[ix] = findPeerings(ix,asn)
        sub_total_peers = len(all_peers[ix])
        print_report("ASN Peering's List per IX :", all_peers, 'join', sub_total_peers)

    mergedlist = []
    for ix in all_peers:
        mergedlist.extend(all_peers[ix])
    mergedlist.sort()
    total_peers = len(mergedlist)
    mergedset = set(mergedlist)
    total_organizations = len(mergedset)
    asn_report = {"ASN":asn,"Total_agg_speed(Gbps)":total_agg_speed,"Total_ix":total_ix,"Total_peers":total_peers,"Total_organizations":total_organizations}
    print_report("ASN Network Executive Summary :", asn_report, 'na', 1)


    print("\n\nThe Additional information for peering's with more than one connection points: ")
    print('~' * 79)
    peer_count = {org: mergedlist.count(org) for org in mergedset}
    for peer, count in peer_count.items():
        if count > 1:
            print(f"{peer} : #number of connection points  {count}")
        else:
            continue

    export_file('asn_report.json', asn_report)
    export_file('ix_net_report.json', all_peers)


if __name__ == "__main__":
    main()




""" Note:

 1 The specific Org might have more than one peer connections in one or more IXs.
 The additional information provides the Orgs list and nummber of connections

 2 The output json file will be exported to mysql database used for web app

 3 The peeringdb output is nested dictionary. some data need to be retrived from inner dict()

 4 Ocationally the peeringDB API server doesn't respond to https request, that will interupt the running script.
   this will occurs likely when the network being queried has widely distributed in >50 IXs

 5 Use ASN = 49909/49902/49904 or ASN = 852 for quick test as all that only exist in less than 3x IXs.


"""
