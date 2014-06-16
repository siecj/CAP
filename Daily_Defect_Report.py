from suds.client import Client
from xml.etree import ElementTree as ET
from jira.client import JIRA
import time
import re
import csv

import os
import unittest

class Daily_Defect_Report():

	def Get_TT_Defects(self,FieldList,IssueID,SiblingName,ComponentList,type,dtStartDate,dtEndDate,DateType,ID):
		url='http://tt.ime.reuters.com/TDM_Sibling/TDMSiblingToolkit.asmx?wsdl'
		query=Client(url)
	
		result=query.service.retrieveTDMDefects(FieldList,IssueID,SiblingName,ComponentList,type,dtStartDate,dtEndDate,DateType,ID)
		result=result.encode("utf-8")
		if re.match("CHE",ComponentList):
			result=result.replace("[&#x2;]","")
		temp=open('temp.xml','w')
		temp.write(result)
		temp.close()
	
		root=ET.parse('temp.xml')
	
		nodes=root.getiterator("MoreInfoTable")
	
		if len(nodes)>0:
			moreinfo=nodes[0].getchildren()[0]
		
			if moreinfo.text=="True":
				newid=nodes[0].getchildren()[1].text
			
				result=result+"\n"+self.Get_TT_Defects(FieldList,IssueID,SiblingName,ComponentList,type,dtStartDate,dtEndDate,DateType,newid)
		result=result.replace("<TT_Msg><Request_Info><Request_Type>XML</Request_Type><Result><NewDataSet>","")
		result=result.replace("</NewDataSet></Result><Msg></Msg></Request_Info></TT_Msg>","")
		return result

	def Get_JIRA_Defects(self,server,auth,jsl):
		jira=JIRA(server,auth)
		issues=jira.search_issues(jsl,maxResults=2000,fields='key,summary,assignee,reporter,status,created,components')
		return issues
		
	def Gen_XML_Files(self,Files,path,Components,Components_Types,StartDate,EndDate):
		FieldList="'ISSUEID','TITLE','COMPONENT_SR','SUBMITTER','DEVELOPER','OWNER','STATE','SEVERITY','SUBMITDATE','BUSINESS_PRIORITY','ISSUETYPE'"
		for file in Files:
			name=path+file+".xml"
			print "Generating "+name
			Defects=self.Get_TT_Defects(FieldList,"","",Components[file],Components_Types[file],StartDate,EndDate,"SUBMITDATE","")
			Defects="<TT_Msg><Request_Info><Request_Type>XML</Request_Type><Result><NewDataSet>\n"+Defects+"\n</NewDataSet></Result><Msg></Msg></Request_Info></TT_Msg>"
			output=open(name,'w')
			output.write(Defects)
			output.close()
			print "Finished\n"

	def Split_Defects_Enhancement(self,file):
		defects=[]
		enhancements=[]
	
		root=ET.parse(file)
		nodes=root.getiterator("RecordsTable")
		if len(nodes)>0:
				for node in nodes:
					items=node.getchildren()
					if items[6].text=="DEFECT":
						if items[4].text in ["Developer Assigned","Being Validated","Open","Questioned"]:
							hash={}
							for i in range(0,len(items)):
								hash[items[i].tag]=items[i].text.encode("utf-8")
							defects.append(hash)
					else:
						if items[4].text in ["Developer Assigned","Being Validated","Open","Questioned"]:
							hash={}
							for i in range(0,len(items)):
								hash[items[i].tag]=items[i].text.encode("utf-8")
							enhancements.append(hash)
		return defects,enhancements
	
	def Filter_All_Open(self,file):
		defects=[]
		root=ET.parse(file)
		nodes=root.getiterator("RecordsTable")
		if len(nodes)>0:
				for node in nodes:
					items=node.getchildren()
					if items[4].text in ["Developer Assigned","Being Validated","Open","Questioned"]:
						hash={}
						for i in range(0,len(items)):
							hash[items[i].tag]=items[i].text.encode("utf-8")
						defects.append(hash)
		return defects

	def Write_CSV_File(self,file,path,list):
		name=path+file
		output=open(name,'wb')
		writer=csv.writer(output)
	
		header=["Issue Number","Summary","Component","Submitter","Developer","Owner","State","Severity","Business Priority","Submit Date"]
	
		print "Start writing " + name
		writer.writerow(header)
	
		for x in list:
			row=[x['ISSUEID'], x['TITLE'],x['COMPONENT_SR'],x['SUBMITTER'],x['DEVELOPER'],x['OWNER'],x['STATE'],x['SEVERITY'],x['BUSINESS_PRIORITY'],x['SUBMITDATE']]
		
			writer.writerow(row)
		
		output.close()
		print "Finished\n"

	def Write_CSV_File_For_JIRA(self,file,path,list):
		name=path+file
		output=open(name,'wb')
		writer=csv.writer(output)
	
		header=["Key","Summary","Reporter","Assignee","Status","Created"]
	
		print "Start writing " + name
		writer.writerow(header)
	
		for x in list:
			if x.fields().assignee==None:
				row=[x.key, x.fields().summary.encode("utf-8"),x.fields().reporter.name,"Unassigned",x.fields().status.name,x.fields().created]	
			else:
				row=[x.key, x.fields().summary.encode("utf-8"),x.fields().reporter.name,x.fields().assignee.name,x.fields().status.name,x.fields().created]

			writer.writerow(row)
		
		output.close()
		print "Finished\n"
	
	def Gen_Full_Defect_Lists(self,path):
		cvg_file=path+"CVG_ALL.xml"
		server={ 'server': 'http://www.iajira.amers.ime.reuters.com'}
		auth=('zhe.wang','alreadyJIRA6!')
		cva_core_jsl="component = 'CVA CORE' AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review')"
		cva_venue_jsl="component = 'CVA' AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review')"
		che_jsl="project in ('ERT VA-CHE','ERT CHE-CD','ERT NTS-R','ERT UPA-CHE') AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review') ORDER BY created DESC"
		scw_jsl="component = 'ERTSCW' AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review')"
		
		#Lists of defects/enhancements for each products
		cvg_defects=self.Filter_All_Open(cvg_file)
	
		cva_core_jira=self.Get_JIRA_Defects(server,auth,cva_core_jsl)

		cva_venue_jira=self.Get_JIRA_Defects(server,auth,cva_venue_jsl)

		che_jira=self.Get_JIRA_Defects(server,auth,che_jsl)

		scw_jira=self.Get_JIRA_Defects(server,auth,scw_jsl)
		
		#Generate .csv files

		cva_core_jira_output="01 CVA CORE Open Defects or Enhancements in JIRA (Total "+str(len(cva_core_jira))+").csv"
		self.Write_CSV_File_For_JIRA(cva_core_jira_output,path,cva_core_jira)

		cva_venue_jira_output="02 CVA VENUE Open Defects or Enhancements in JIRA (Total "+str(len(cva_venue_jira))+").csv"
		self.Write_CSV_File_For_JIRA(cva_venue_jira_output,path,cva_venue_jira)

		che_jira_output="03 CHE Open Defects or Enhancements in JIRA (Total "+str(len(che_jira))+").csv"
		self.Write_CSV_File_For_JIRA(che_jira_output,path,che_jira)
	
		scw_jira_output="05 SCW Open Defects or Enhancements in JIRA (Total "+str(len(scw_jira))+").csv"
		self.Write_CSV_File_For_JIRA(scw_jira_output,path,scw_jira)
	
		cvg_defects.reverse()
		
		#Generate .csv file for CVG
		cvg_DEFECTS_output="04 CVG Open Defects (Total " + str(len(cvg_defects))+").csv"
		self.Write_CSV_File(cvg_DEFECTS_output,path,cvg_defects)
	
	
	def Gen_Delta_Defect_Lists(self,path):
		cvg_file=path+"CVG_ALL.xml"
		server={ 'server': 'http://www.iajira.amers.ime.reuters.com'}
		auth=('zhe.wang','alreadyJIRA6!')
		cva_core_jsl="component = 'CVA CORE' AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review') AND createdDate >= startOfDay(-1d) AND createdDate < startOfDay() ORDER BY Created DESC"
		cva_venue_jsl="component = 'CVA' AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review') AND createdDate >= startOfDay(-1d) AND createdDate < startOfDay() ORDER BY Created DESC"
		che_jsl="project in ('ERT VA-CHE','ERT CHE-CD','ERT NTS-R','ERT UPA-CHE') AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review') AND createdDate >= startOfDay(-1d) AND createdDate < startOfDay() ORDER BY Created DESC"
		scw_jsl="component = 'ERTSCW' AND issuetype in (Bug,Improvement) AND status in ('Open','In Progress','In Review') AND createdDate >= startOfDay(-1d) AND createdDate < startOfDay() ORDER BY Created DESC"
		
		#Lists of defects/enhancements for each products
	
		cvg_defects=self.Filter_All_Open(cvg_file)
	
		cva_core_jira=self.Get_JIRA_Defects(server,auth,cva_core_jsl)

		cva_venue_jira=self.Get_JIRA_Defects(server,auth,cva_venue_jsl)

		che_jira=self.Get_JIRA_Defects(server,auth,che_jsl)

		scw_jira=self.Get_JIRA_Defects(server,auth,scw_jsl)
	
		if len(cva_core_jira)>0:
			cva_core_jira_output="01 CVA CORE Open Defects or Enhancements in JIRA (Total "+str(len(cva_core_jira))+").csv"
			self.Write_CSV_File_For_JIRA(cva_core_jira_output,path,cva_core_jira)

		if len(cva_venue_jira)>0:
			cva_venue_jira_output="02 CVA VENUE Open Defects or Enhancements in JIRA (Total "+str(len(cva_venue_jira))+").csv"
			self.Write_CSV_File_For_JIRA(cva_venue_jira_output,path,cva_venue_jira)

		if len(che_jira)>0:
			che_jira_output="03 CHE Open Defects or Enhancements in JIRA (Total "+str(len(che_jira))+").csv"
			self.Write_CSV_File_For_JIRA(che_jira_output,path,che_jira)

		if len(scw_jira)>0:
			scw_jira_output="05 SCW Open Defects or Enhancements in JIRA (Total "+str(len(scw_jira))+").csv"
			self.Write_CSV_File_For_JIRA(scw_jira_output,path,scw_jira)

		if len(cvg_defects)>0:
			cvg_DEFECTS_output="04 CVG Open Defects (Total " + str(len(cvg_defects))+").csv"
			self.Write_CSV_File(cvg_DEFECTS_output,path,cvg_defects)	
		
	
	def removeFileInDir(self,targetDir):
		for file in os.listdir(targetDir): 
			targetFile = os.path.join(targetDir,  file)
			if os.path.isfile(targetFile):
				os.remove(targetFile)

	def report(self):

		#Variables Initialization
		cur_path=os.getcwd()
	
		Files=[]
		Files.append('CVG_ALL')
		Components={'CVA_ALL':'Elektron_CVA','CVG_ALL':'IDN_CVG','VA_CHE_ALL':'CHE-DJT,CHE-NFI,CHE-NTT,CHE-VAP,CHE-NTS,CHE-PHO,CHE-COX,CHE-CD,VA-CHE-CVG,VA-CHE-Elektron,CHE-GW1,CHE-RTA','SCW':'STATE CONTROL WATCHDOG'}
		Component_Types={'CVA_ALL':'Product','CVG_ALL':'Product','VA_CHE_ALL':'Component','SCW':'Component'}
	
		StartDate=''
		EndDate=''
		current=time.time()
		today=time.gmtime(current)
	
		#generate the TT query date range   
		if today[6]!=0:
			yesterday=time.gmtime(current-86400)
			StartDate=str(yesterday[0])+'-'+str(yesterday[1])+'-'+str(yesterday[2])+' 1:00AM'
			EndDate=str(today[0])+'-'+str(today[1])+'-'+str(today[2])+' 1:00AM'
		else:
			StartDate='2010-01-01 1:00AM'
			EndDate=EndDate=str(today[0])+'-'+str(today[1])+'-'+str(today[2])+' 1:00AM'
		
		#create output path
		output_path=cur_path+"\\raw data\\"
	
		if not os.path.exists(output_path):
			os.mkdir(output_path)
		today_folder=output_path+str(today[0])+str(today[1])+str(today[2])+"\\"
	
		#delete the existing files under output_path
		self.removeFileInDir(output_path)
	
		#Store the TT query results to xml files
		self.Gen_XML_Files(Files,output_path,Components,Component_Types,StartDate,EndDate)

		if today[6]==0:
			self.Gen_Full_Defect_Lists(output_path)
		else:
			self.Gen_Delta_Defect_Lists(output_path)
