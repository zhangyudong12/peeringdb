from flask import Flask, redirect, render_template, request, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
import json
import os

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
        filename = 'script_cmd_output_' + asn + '.txt'
        subfolder = 'log_' + asn
        filename_full = os.path.join(dirname, subfolder, filename)
        if os.path.isfile(filename_full):
            f = open(filename_full,'r')
            message = "ASN:{asn_id} query function to be intergated !".format(asn_id=asn)
            message = f.read()
            return  render_template("display2.html", message=message)
        else:
            message = "ASN:{asn_id} output file not exist !".format(asn_id=asn)
            return  render_template("display2.html", message=message)

    if request.method == "GET":
        return  render_template("query.html")

@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
