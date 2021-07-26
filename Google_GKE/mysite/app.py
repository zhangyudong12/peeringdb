from flask import Flask, redirect, render_template, request, url_for, make_response,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
import json
import os
import requests
import sys
import time
import re
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
app.config["DEBUG"] = True

# Google Cloud SQL via authorised network
#SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket =/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}".format(
#    #USERNAME = "root",
#    PASSWORD = "root123",
#    PUBLIC_IP_ADDRESS = "34.132.204.107",
#    DBNAME = "peeringdb",
#    PROJECT_ID = "lucky-reactor-320314",
#    INSTANCE_NAME = "mysql-ins-1",
#    #CONNECTION_NAME = "lucky-reactor-320314:us-central1:mysql-ins-1",
#)

# Access DB via cloudsql proxy
SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST_IP_ADDRESS}/{DBNAME}".format(
    USERNAME = "root",
    PASSWORD = "root123",
    HOST_IP_ADDRESS = "10.20.11.17",
    DBNAME = "peeringdb",
)

# configuration
app.config["SECRET_KEY"] = "na"
app.config["SQLALCHEMY_DATABASE_URI"]= SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

db = SQLAlchemy(app)

class Asn(db.Model):

    __tablename__ = "asns"

    id = db.Column(db.Integer, primary_key=True)
    ASN = db.Column(db.Integer)
    Total_ix = db.Column(db.Integer)
    Total_agg_speed_Gbps = db.Column(db.Integer)
    Total_peers = db.Column(db.Integer)
    Total_organizations = db.Column(db.Integer)

    def __init__(self, ASN, Total_ix, Total_agg_speed_Gbps, Total_peers, Total_organizations):
        self.ASN = ASN
        self.Total_ix = Total_ix
        self.Total_agg_speed_Gbps = Total_agg_speed_Gbps
        self.Total_peers = Total_peers
        self.Total_organizations = Total_organizations

    def __repr__(self):
        return '[ASN {}]'.format(self.ASN)


def asn_query():
    return Asn.query

class AsnForm(FlaskForm):
    opts = QuerySelectField(query_factory=asn_query, allow_blank=True, get_label='ASN')

class Ix(db.Model):

    __tablename__ = "ixs"

    id = db.Column(db.Integer, primary_key=True)
    asn_id = db.Column(db.Integer, db.ForeignKey('asns.id'))
    Ix_name = db.Column(db.String(4096))
    Net_name = db.Column(db.Text)

    def __init__(self, asn_id,Ix_name, Net_name):
        self.asn_id = asn_id
        self.Ix_name = Ix_name
        self.Net_name = Net_name

comments = []


def db_sync():
    dirname = '/app'
    subfolders= [f.name for f in os.scandir(dirname) if f.is_dir()]
    sublog_list = []
    for subd in subfolders:
        if 'log' in subd:
            sublog_list.append(subd)

    for subd in sublog_list:
        asn_report = dict()
        ix_report = dict()
        data_reload = False
        asn_report_fn = os.path.join(dirname, subd, 'asn_report.json')
        ix_report_fn = os.path.join(dirname, subd, 'ix_net_report.json')
        with open(asn_report_fn) as report_file1:
            asn_report = json.load(report_file1)

        with open(ix_report_fn) as report_file2:
            ix_report = json.load(report_file2)

        existing_asn = Asn.query.filter(Asn.ASN == asn_report["ASN"]).first()
        if not existing_asn:
            asn_record = Asn(asn_report["ASN"],asn_report["Total_ix"],asn_report["Total_agg_speed(Gbps)"],asn_report["Total_peers"],asn_report["Total_organizations"])
            db.session.add(asn_record)
            db.session.commit()
            existing_asn = Asn.query.filter(Asn.ASN == asn_report["ASN"]).first()
            asn_id = existing_asn.id
            data_reload = True

        if data_reload:
            for ix,net in ix_report.items():
                net_list_str = ','.join(net)
                ix_record = Ix(asn_id,ix,net_list_str)
                db.session.add(ix_record)
            db.session.commit()

        report_file1.close()
        report_file2.close()

    return()

#db_sync()

apiurl = 'https://www.peeringdb.com/api/'


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
    if not results['data']:
        print(f"AS{search} not found in PeeringDB")
        return
    ix_speed = 0
    ix_list = []
    fac_list = []
    ix_urls = []
    fac_urls = []
    for key in sorted(results['data'][0]):
        if key == 'netixlan_set':
            for ixlan in results['data'][0][key]:
                ix_speed = ix_speed + int(ixlan['speed'])
                url = "%six?ixlan_id=%s" % (apiurl, ixlan['ixlan_id'])
                ix_urls.append(url)
            with ThreadPoolExecutor(max_workers=10) as executor:
                ix_results_list = executor.map(fetchResults, ix_urls, timeout=60)
            for ix_results in ix_results_list:
                ix_list.append(ix_results['data'][0]['name'])

        elif key == 'netfac_set':
            for fac in results['data'][0][key]:
                url = "%sfac?id=%s" % (apiurl, fac['fac_id'])
                fac_urls.append(url)
            with ThreadPoolExecutor(max_workers=10) as executor:
                fac_results_list = executor.map(fetchResults, fac_urls, timeout=60)
            for fac_results in fac_results_list:
                fac_list.append(fac_results['data'][0]['name'])

    ix_list.sort()
    fac_list.sort()
    return ix_list,fac_list,ix_speed


# input:IX name and asn, output:sorted network list exclude the input asn
def findPeerings(search, asn):
    # match exact name
    url = "%six?name=%s" % (apiurl, search)
    results = fetchResults(url)
    net_list = []
    net_ids = []
    net_names = []
    net_asns = []
    for ix in results['data']:
        ix_id = ix['id']
        url2 = "%snetixlan?ix_id=%s" % (apiurl, ix_id)
        results2 = fetchResults(url2)
        for net in results2['data']:
            net_asn = net['asn']
            if net_asn != asn:
                net_id = net['net_id']
                net_ids.append(net_id)
                net_asns.append(net_asn)

        with ThreadPoolExecutor(max_workers=10) as executor:
            net_names = executor.map(lookupNet, net_ids, timeout=60)

        for net_name, net_asn in zip(net_names, net_asns):
            net_name_alias = 'AS_' + str(net_asn) + '_' + net_name
            net_list.append(net_name_alias)

            # matches = re.search(r'\u\d', net_name)
            # if matches:
            #     net_name_alias = 'AS_' + 'unprintable_name'
            # else:
            #     net_name_alias = 'AS_' + str(net_asn) + '_' + net_name
            # net_list.append(net_name_alias)

    net_list.sort()
    return net_list


def print_report(title,input,flag):
    print("\n")
    print('~' * 79)
    print(title)
    print('~' * 79)
    if type(input) == dict:
        if flag == 'join':
            for key,value in input.items():
                sub_total_peers = len(value)
                print(f"\nIX: {key}   Peering's : {sub_total_peers}")
                print('\n'.join(value))

        else:
            for key,value in input.items():
                print (key,value)
    elif type(input) == list:
        input_set = set(input)
        item_count = {item: input.count(item) for item in input_set}
        for item, count in item_count.items():
            if count > 1:
                print(f"{item} : #number of connections  {count}")
            else:
                continue
    else:
        print("Wrong input")
        exit(1)

def export_file(file_name,contents,asn):
    newdir = 'log_' + str(asn)
    try:
        os.mkdir(newdir)
    except OSError as error:
        # FileExistsError is error # 17
        if error.errno == 17:
            print('Data already exists.')
        else:
            # re-raise the exception if some other error occurred.
            raise
    filename_full = os.path.join(newdir, file_name)
    with open(filename_full, 'w') as json_file:
        json.dump(contents, json_file, indent=2)
    json_file.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AsnForm()
    form.opts.query = Asn.query.filter(Asn.id >= 1)

    if form.validate_on_submit():
        if 'query' in request.form:
            selected_asn = form.opts.data.ASN
            asns = Asn.query.filter(Asn.ASN == selected_asn).all()
            asn = Asn.query.filter(Asn.ASN == selected_asn).first()
            ixs=Ix.query.filter(Ix.asn_id == asn.id).all()
            return render_template("display.html", asns=asns, ixs=ixs)

    return render_template('index.html', form=form)


@app.route('/db', methods=['GET', 'POST'])
def db_mgmt():
    cnt_return = 0
    if request.method == "POST":
        comments.append(request.form["contents"])
        db_sync()
        return redirect(url_for('db_mgmt'))

    return render_template("db.html", comments=comments, cnt=cnt_return)

@app.route('/query', methods = ['GET','POST'])
def query():
    dirname = '/app'
    if request.method == "POST":
        asn = request.form.get('asn')
        
        # Process input variable
        orig_stdout = sys.stdout
        output_filename = 'script_cmd_output_' + str(asn) + '.txt'
        f = open(output_filename, 'w')
        sys.stdout = f
        flash('Query report generated ---')

        start_time = time.time()

        # Process ASN query data
        if getIX(asn) != None:
            ix_list_asn, fac_list_asn, total_agg_speed_m = getIX(asn)
            ix_set_asn = set(ix_list_asn)
            total_agg_speed = total_agg_speed_m/1000
            total_ix = len(ix_set_asn)
            total_fac = len(fac_list_asn)
            ix_set_asn_str = '\n'.join(ix_set_asn)
            fac_list_asn_str = '\n'.join(fac_list_asn)

            print('~' * 79)
            print(f"Network with ASN = {asn} exists in {total_ix} Public Exchange Points and {total_fac} Private Peering Facilities")
            print(f"\nPublic IXs:\n{ix_set_asn_str}")
            if total_fac != 0:
                print(f"\nPrivate FAs:\n{fac_list_asn_str}")

            # sort the output data to dict
            all_peers = dict()
            for ix in ix_set_asn:
                all_peers[ix] = findPeerings(ix,asn)

            # deduplication
            mergedlist = []
            for ix in all_peers:
                mergedlist.extend(all_peers[ix])
            mergedlist.sort()
            total_peers = len(mergedlist)
            mergedset = set(mergedlist)
            total_organizations = len(mergedset)

            asn_report = {"ASN":asn,"Total_agg_speed(Gbps)":total_agg_speed,"Total_ix":total_ix,"Total_peers":total_peers,"Total_organizations":total_organizations}

            # export report to file
            filename1 = 'asn_report.json'
            filename2 = 'ix_net_report.json'
            export_file(filename1, asn_report, asn)
            export_file(filename2, all_peers, asn)

            # print report
            print_report("ASN Network Executive Summary :", asn_report, 'na')
            print_report("ASN Peering's List per Public IX :", all_peers, 'join')
            print_report("The additional information for IXs where the ASN has more connections: ",ix_list_asn,'na')
            print_report("The additional information for peering's with more than one connection points:: ",mergedlist,'na')

            # calculate and display script running time
            elapsed_time_secs = time.time() - start_time
            elapsed_time = timedelta(seconds=round(elapsed_time_secs))
            print(f"\n\n\nScript execution took: {elapsed_time}")

            f.close()
        else:
            message = "ASN:{asn_id} is not found !".format(asn_id=asn)
            return  render_template("display2.html", message=message)

        filename = 'script_cmd_output_' + asn + '.txt'
        filename_full = os.path.join(dirname, filename)        
        if os.path.isfile(filename_full):
            f = open(filename_full,'r')
            message = f.read()
            return  render_template("display2.html", message=message)
        else:
            message = "ASN:{asn_id} output file not exist !".format(asn_id=asn)
            return  render_template("display2.html", message=message)

    elif request.method == "GET":
        return  render_template("query.html")


@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
