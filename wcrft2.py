#!/usr/bin/python2
user="mojadresemail"
lpmn="any2txt|wcrft2"
import json
import urllib2
import glob
import os
import time
import sys
url="http://ws.clarin-pl.eu/nlprest2/base"

def upload(file):
        with open (file, "rb") as myfile:
            doc=myfile.read()
        return urllib2.urlopen(urllib2.Request(url+'/upload/',doc,{'Content-Type': 'binary/octet-stream'})).read();

def process(data):
        doc=json.dumps(data)
        taskid = urllib2.urlopen(urllib2.Request(url+'/startTask/',doc,{'Content-Type': 'application/json'})).read();
        time.sleep(0.2);
        resp = urllib2.urlopen(urllib2.Request(url+'/getStatus/'+taskid));
        data=json.load(resp)
        while data["status"] == "QUEUE" or data["status"] == "PROCESSING" :
            time.sleep(0.5);
            resp = urllib2.urlopen(urllib2.Request(url+'/getStatus/'+taskid));
            data=json.load(resp)
        if data["status"]=="ERROR":
            print("Error "+data["value"]);
            return None;
        return data["value"]

def main():
    if len(sys.argv) < 3:
        print("Usage: wcrft2.py input_dir output_dir")
        return
    
    in_path=sys.argv[1]
    out_path=sys.argv[2]

    global_time = time.time()
    for file in glob.glob(in_path):
        start_time = time.time()
        fileid=upload(file)
        print("Processing: "+file);
        data={'lpmn':lpmn,'user':user,'file':fileid}
        data=process(data)
        if data==None:
            continue;
        data=data[0]["fileID"];
        content = urllib2.urlopen(urllib2.Request(url+'/download'+data)).read();
        out_filepath=out_path+os.path.basename(file)+'.ccl'
        print("out_path: "+out_path)
        print("file: "+file)
        print("os.path.basename(file): "+os.path.basename(file))
        print("Writing retult to: "+out_filepath)
        with open (out_filepath, "w") as outfile:
                outfile.write(content)
    print("GLOBAL %s seconds ---" % (time.time() - global_time))

main();
