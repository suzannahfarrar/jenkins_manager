from requests.auth import HTTPBasicAuth
import argparse
import requests
import jenkins 
import os, javaproperties
from collections import Counter
from bs4 import BeautifulSoup

# server = jenkins.Jenkins('http://localhost:8080',username = 'Suzannah', password = 'root')
server = jenkins.Jenkins('http://localhost:8080')

jobs = server.get_jobs()

def test_CI(jobname, p):
	print ("_________________________")
	print ('\n Job Name: %s' % (jobname))
	print ("_________________________")
	result_xml = server.get_job_config(jobname)
	soup = BeautifulSoup(result_xml, "xml")

	# Getting the job's XML file
	url = "http://localhost:8080/job/" + jobname + "/api/xml"
	# resp = requests.get(url, auth=HTTPBasicAuth('Suzannah', 'root'))
	resp = requests.get(url)
	soup = BeautifulSoup(resp.content, "xml")
	builds = soup.find_all('build')
	counter = 0
	
	# Checking if the job has been built atleast once before proceeding
	if len(builds) > 0:
		
		for build in builds:
			
			# Counter used to check the total number of builds
			counter = counter+1
			
			# Checking XML files of each build
			url = "http://localhost:8080/job/" + jobname +"/"+ build.find('number').string +"/api/xml"
			# resp = requests.get(url, auth=HTTPBasicAuth('Suzannah', 'root'))
			resp = requests.get(url)
			soup = BeautifulSoup(resp.content, "xml")
			building = soup.find('building')
			
			if building:
				
				print("\n Build number: " + soup.find('number').string)
				rep_url = soup.find('remoteUrl')
				
				if rep_url:
					print(" Repository URL: " + rep_url.string)
					if ("\""+rep_url.string+"\"") == p['repo_path']:
						print(" Repository check: SUCCESS")	
					else:
						print(" Repository check: FAILURE")				

				else:
					print (" No repository")

				# Checking to see if the build has completed
				if building.string == 'false':
					
					marked = soup.find('marked')
					if marked:
						branches = marked.find_all('branch')
						print (" Branches: " )
						for branch in branches:
							print(" "+branch.find('name').string+"\n")
						result = soup.find('result')
						print (" Result: " + result.string)

					else:
						result = soup.find('result')
						print(" Result: " + result.string)

					# Checking munit file
					print ("\n MUNIT Test - Errors and warnings: \n")
					check_munit_report()

				# If build is running, then this code will run
				else:
					print(" Build is still running")
	else:
		print(" No build performed on this job")
	print ("\n Total number of builds: ", counter)

def check_munit_report():
	
	f = open('filemunittest.txt', 'r')
	file = f.readlines()
	error_lines = 0
	warning_lines = 0
	printList = []
	for line in file:
		if ('ERROR' in line):
			error_lines = error_lines + 1
		if ('WARNING' in line):
			warning_lines = warning_lines + 1
		if ('ERROR' in line) or ('WARNING' in line):
			printList.append(line)
	for item in printList:
		print (item)

	print(" Total number of errors: ",error_lines)
	print(" Total number of warnings: ", warning_lines)

def get_input_properties():
	
	# Checking input.properties file
	with open('input.properties', 'rb') as f:
		p = javaproperties.load(f)
	return p

def check_job(job_name):
	for job_instance in jobs:
		if job_name == ("\""+job_instance['name']+"\""):
			return job_instance['name']

def main():
	p = get_input_properties()
	jobname = p['job_name']
	job = check_job(jobname)
	if job != '':
		test_CI(job, p)
	else:
		print(" No job name specified")

if __name__ == "__main__": main()