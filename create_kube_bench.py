"""
Creates, updates, and deletes a job object.
"""

from os import path
from flask import Flask
import yaml
import time
from kubernetes import client, config
from yaml import load

JOB_NAME = "kube-bench"

from kubernetes import client, config

def get_prev_job_if_running(v1):
    # gets the prev job id so that we can delete the earlier job
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    pod_name=""
    job_id=""	
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        pod_name=i.metadata.name
        if pod_name.startswith(JOB_NAME):
             job_id=pod_name

    return job_id
   

def create_yaml():
    stream = open("job.yaml", 'r')
    return  yaml.safe_load(stream)

def create_job(api_instance, job):
    time.sleep(5)
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default")
    print("Job created. status='%s'" % str(api_response.status))

def get_api_json(api_instance, id):
    return api_instance.read_namespaced_pod_log(name=id, namespace='default')

def delete_job(api_instance, id):
    api_response = api_instance.delete_namespaced_job(
        name=JOB_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Job deleted. status='%s'" % str(api_response.status))


def bench():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()
    #load from job.yaml in current dir
    job = create_yaml()
    print(job)
    id = get_prev_job_if_running(core_v1)
    print("Found the job " + id)
    if id!="":
         delete_job(batch_v1, id)
    create_job(batch_v1, job)
    time.sleep(10)
    return(get_api_json(core_v1, get_prev_job_if_running(core_v1)))

app = Flask(__name__)

@app.route('/')
def runBench():
   return bench()

if __name__ == '__main__':
     app.run(host= '0.0.0.0') 
