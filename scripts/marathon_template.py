#!/usr/bin/python

import argparse
import urllib2
import json
from jinja2 import Environment, Template

import Properties


class MarathonTaskInfo:
	def __init__(self, host, ports):
		self.host = host
		self.ports = ports

	def http_uri(self):
		return "http://"+self.host+":"+str(self.ports[0])


def to_set(param, sep=','):
	return set(param.split(sep))

def http(url):
	print "Fetching from %s " % url
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	return json.loads(response.read())

# Not used currently
def all_apps_on(marathon_uri):
	apps_json = http(marathon_uri+"/v2/apps")
	apps = apps_json["apps"]
	app_ids = map(lambda app: app["id"].strip("/"), apps)
	return app_ids

def fetch_tasks(marathon_uri, app_id):
	app = http(marathon_uri+"/v2/apps/"+app_id)
	app_tasks = app["app"]["tasks"]
	tasks = map(lambda task: MarathonTaskInfo(task["host"], task["ports"]), app_tasks)
	return map(lambda t: t.http_uri(), tasks)

def tasks_for(marathon_url, apps):
	response = {}
	for app in apps:
		response[app] = fetch_tasks(marathon_url, app)
	return response

def render(template, out_file, variables):
	env = Environment()
	app_name = template.split(".")[0]
	properties = Properties.load("../conf/"+app_name+".properties")

	template = env.get_template(template)
	rendered_template = template.stream(j2=variables, props=properties)
	rendered_template.dump(out_file)

if __name__ == '__main__':
	argumentParser = argparse.ArgumentParser(prog='marathon_template', description='Script that\'s used to generate ha_proxy config file from marathon')
	argumentParser.add_argument('-m', '--marathon', help='Marathon URI', required=True)
	argumentParser.add_argument('-a', '--app_name', type=to_set, help='App name for which haproxy config needs to be generated', required=True)
	argumentParser.add_argument('-t', '--template_file', help='Template file which on which rendering would be done', required=True)
	argumentParser.add_argument('-o', '--out_file', help='Output file', required=True)

	args = argumentParser.parse_args()

	response = tasks_for(args.marathon, args.app_name)
	render(template_file, out_file, response)