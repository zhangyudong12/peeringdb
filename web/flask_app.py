from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="zhangyudong12",
    password="Twitch123",
    hostname="zhangyudong12.mysql.pythonanywhere-services.com",
    databasename="zhangyudong12$peeringdb",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

class Ix(db.Model):

    __tablename__ = "ixs"

    id = db.Column(db.Integer, primary_key=True)
    Ix_name = db.Column(db.String(4096))
    Net_name = db.Column(db.String(4096))

    def __init__(self, Ix_name, Net_name):
        self.Ix_name = Ix_name
        self.Net_name = Net_name

asn_report = dict()
ix_report = dict()

with open('/home/zhangyudong12/mysite/asn_report.json') as report_file1:
     asn_report = json.load(report_file1)
report_file1.close()

existing_asn = Asn.query.filter(Asn.ASN == asn_report["ASN"]).first()

if not existing_asn:
    asn_record = Asn(asn_report["ASN"],asn_report["Total_ix"],asn_report["Total_agg_speed(Gbps)"],asn_report["Total_peers"],asn_report["Total_organizations"])
    db.session.add(asn_record)
    db.session.commit()

with open('/home/zhangyudong12/mysite/ix_net_report.json') as report_file2:
     ix_report = json.load(report_file2)
report_file2.close()

for ix,net in ix_report.items():
    net_list_str = ','.join(net)
    existing_ix = Ix.query.filter(Ix.Net_name == net_list_str).first()
    if not existing_ix:
        ix_record = Ix(ix,net_list_str)
        db.session.add(ix_record)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("main_page.html", asns=Asn.query.all(), ixs=Ix.query.all())
