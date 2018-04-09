import os, os.path
import random
import string
import cherrypy
import requests, zipfile, io
import csv,redis
import sys
import datetime

REDIS_HOST = 'localhost'
conn = redis.Redis(REDIS_HOST)
@cherrypy.expose
class StockWebService(object):

    @cherrypy.tools.accept(media='application/json')
    def GET(self,keyword=''):
        
        if(keyword):
            ll=[]
            for key in conn.scan_iter(match="*"+keyword+"*"):
                ll.append(conn.get(key)+",")
            return ll;
        else:
            arr= conn.get("top_10")
            return arr
        
    def POST(self):
        def get_date():
            date=datetime.date.today().strftime('%d%m%y')
            return date
        
        try:
            r = requests.get("https://www.bseindia.com/download/BhavCopy/Equity/EQ{0}_CSV.ZIP".format(get_date()))
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return err
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("public/files")
        
    
        def store_data(conn, data):
            top_10="";
            for counter,i in enumerate(data):
                if(counter > 0 and counter<=10):
                   top_10+='{"CODE":"'+i[0]+'","NAME":"'+i[1].strip()+'","OPEN":"'+i[2]+'","HIGH":"'+i[3]+'","LOW":"'+i[4]+'","CLOSE":"'+i[5]+'"},'
                
                
                conn.setnx(i[1].strip(),'{"CODE":"'+i[0]+'","NAME":"'+i[1].strip()+'","OPEN":"'+i[2]+'","HIGH":"'+i[3]+'","LOW":"'+i[4]+'","CLOSE":"'+i[5]+'"}')
            conn.setnx("top_10",top_10)
            return data
        def read_csv_data(csv_file, code, name,opn,high,lw,clos):
            with open(csv_file, 'r') as csvf:
                csv_data = csv.reader(csvf)
                return [(r[code], r[name],r[opn],r[high],r[lw],r[clos]) for r in csv_data]

        conn = redis.Redis(REDIS_HOST)
        # deleting previous data
        conn.flushdb()
        data= read_csv_data("public/files/EQ{0}.CSV".format(get_date()),0,1,4,5,6,7)
        check=store_data(conn, data)
        
        if(check):
            return "Succesful";    
        else:
            return "Unsuccessful";


    def PUT(self, another_string):
        cherrypy.session['mystring'] = another_string

    def DELETE(self):
        cherrypy.session.pop('mystring', None)


class Generator(object):
    @cherrypy.expose
    def index(self):
          return open('index.html')

    @cherrypy.expose
    def generate(self,length=16):
        return ''.join(random.sample(string.hexdigits, int(length)))


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/stock': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    webapp = Generator()
    webapp.stock = StockWebService()
    cherrypy.quickstart(webapp, '/', conf)