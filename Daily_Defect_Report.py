from suds.client import Client
from xml.etree import ElementTree as ET
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
	
		header=["Issue Number","Summary","Component","Submitter","Developer","Ower","State","Severity","Business Priority","Submit Date"]
	
		print "Start writing " + name
		writer.writerow(header)
	
		for x in list:
			row=[x['ISSUEID'], x['TITLE'],x['COMPONENT_SR'],x['SUBMITTER'],x['DEVELOPER'],x['OWNER'],x['STATE'],x['SEVERITY'],x['BUSINESS_PRIORITY'],x['SUBMITDATE']]
		
			writer.writerow(row)
		
		output.close()
		print "Finished\n"

	def Gen_Full_Defect_Lists(self,path):
		cva_file=path+"CVA_ALL.xml"
		cvg_file=path+"CVG_ALL.xml"
		va_che_file=path+"VA_CHE_ALL.xml"
		scw_file=path+"SCW.xml"
	
		#Lists of defects/enhancements for each products
		(cva_defects,cva_enhancements)=self.Split_Defects_Enhancement(cva_file)
	
		(cvg_defects,cvg_enhancements)=self.Split_Defects_Enhancement(cvg_file)
	
		va_che=self.Filter_All_Open(va_che_file)
	
		scw=self.Filter_All_Open(scw_file)
	
		#Generate .csv file for CVA defects by region
		CVA_AMER=[]
		CVA_EMEA=[]
		CVA_APAC=[]
		CVA_CORE=[]
		CVA_VENUE_COMMON=[]
	
		for d in cva_defects:
			if re.match("AMER",d['COMPONENT_SR']):
				CVA_AMER.append(d)
			elif re.match("EMEA",d['COMPONENT_SR']):
				CVA_EMEA.append(d)
			elif re.match("APAC",d['COMPONENT_SR']):
				CVA_APAC.append(d)
			elif re.match("CVA-Core",d['COMPONENT_SR']):
				CVA_CORE.append(d)
			elif re.match("Venue_Common",d['COMPONENT_SR']):
				CVA_VENUE_COMMON.append(d)
	
		cva_AMER_output="01 CVA Venue Open Defects Region AMER (Total "+str(len(CVA_AMER))+").csv"
	
		self.Write_CSV_File(cva_AMER_output,path,CVA_AMER)
	
		cva_EMEA_output="02 CVA Venue Open Defects Region EMEA (Total "+str(len(CVA_EMEA))+").csv"
	
		self.Write_CSV_File(cva_EMEA_output,path,CVA_EMEA)
	
		cva_APAC_output="03 CVA Venue Open Defects Region APAC (Total "+str(len(CVA_APAC))+").csv"
	
		self.Write_CSV_File(cva_APAC_output,path,CVA_APAC)
	
		cva_CORE_output="04 CVA Venue Open Defects CVA CORE (Total "+str(len(CVA_CORE))+").csv"
	
		self.Write_CSV_File(cva_CORE_output,path,CVA_CORE)
	
		cva_VENUE_COMMON_output="05 CVA Venue Open Defects VENUE COMMON (Total "+str(len(CVA_VENUE_COMMON))+").csv"
	
		self.Write_CSV_File(cva_VENUE_COMMON_output,path,CVA_VENUE_COMMON)
	
		#Generate .csv file for CVA enhancements by core or venue
		CVA_CORE_ENHAN=[]
		CVA_VENUE_ENHAN=[]
	
		for e in cva_enhancements:
			if re.match("CVA-Core",e['COMPONENT_SR']):
				CVA_CORE_ENHAN.append(e)
			else:
				CVA_VENUE_ENHAN.append(e)
	
		va_CORE_ENHAN_output="06 CVA Core Open Enhancements (Total "+str(len(CVA_CORE_ENHAN))+").csv"
	
		self.Write_CSV_File(va_CORE_ENHAN_output,path,CVA_CORE_ENHAN)
	
		cva_VENUE_ENHAN_output="07 CVA Venue Open Enhancements (Total "+str(len(CVA_VENUE_ENHAN))+").csv"
	
		self.Write_CSV_File(cva_VENUE_ENHAN_output,path,CVA_VENUE_ENHAN)
	
		#Generate .csv file for CVG
		cvg_DEFECTS_output="08 CVG Open Defects (Total " + str(len(cvg_defects))+").csv"
		self.Write_CSV_File(cvg_DEFECTS_output,path,cvg_defects)
	
		cvg_ENHAN_output="09 CVG Open Enhancements (Total " + str(len(cvg_enhancements))+").csv"
		self.Write_CSV_File(cvg_ENHAN_output,path,cvg_enhancements)
	
		#Generate .csv file for VA-CHE
		va_che_output="10 VA-CHE NTSR CHE-CD Open Defects Enhancements (Total " + str(len(va_che))+").csv"
		self.Write_CSV_File(va_che_output,path,va_che)
	
		#Generate .csv file for SCW
		scw_output="11 SCW Open Defects Enhancements (Total " + str(len(scw))+").csv"
		self.Write_CSV_File(scw_output,path,scw)
	
	def Gen_Delta_Defect_Lists(self,path):
		cva_file=path+"CVA_ALL.xml"
		cvg_file=path+"CVG_ALL.xml"
		va_che_file=path+"VA_CHE_ALL.xml"
		scw_file=path+"SCW.xml"
	
		#Lists of defects/enhancements for each products
		(cva_defects,cva_enhancements)=self.Split_Defects_Enhancement(cva_file)
	
		(cvg_defects,cvg_enhancements)=self.Split_Defects_Enhancement(cvg_file)
	
		va_che=self.Filter_All_Open(va_che_file)
	
		scw=self.Filter_All_Open(scw_file)
	
		if len(cva_defects)>0:
			cva_DEFECTS_output="01 New Open CVA Defects.csv"
			self.Write_CSV_File(cva_DEFECTS_output,path,cva_defects)

		if len(cva_enhancements)>0:
			cva_ENHAN_output="02 New Open CVA Enhancements.csv"
			self.Write_CSV_File(cva_ENHAN_output,path,cva_enhancements)
		
		if len(cvg_defects)>0:
			cvg_DEFECTS_output="03 New Open CVG Defects.csv"
			self.Write_CSV_File(cvg_DEFECTS_output,path,cvg_defects)
		
		if len(cvg_enhancements)>0:
			cvg_ENHAN_output="04 New Open CVG Enhancements.csv"
			self.Write_CSV_File(cvg_ENHAN_output,path,cvg_enhancements)
		
		if len(va_che)>0:
			va_che_output="05 New Open VA-CHE Defects Enhancements.csv"
			self.Write_CSV_File(va_che_output,path,va_che)  
	
		if len(scw)>0:
			scw_output="06 New Open SCW Defects Enhancements.csv"
			self.Write_CSV_File(scw_output,path,scw)
		
	
	def removeFileInDir(self,targetDir):
		for file in os.listdir(targetDir): 
			targetFile = os.path.join(targetDir,  file)
			if os.path.isfile(targetFile):
				os.remove(targetFile)

	def report(self):

		#Variables Initialization
		cur_path=os.getcwd()
	
		Files=('CVA_ALL','CVG_ALL','VA_CHE_ALL','SCW')
		Components={'CVA_ALL':'Elektron_CVA','CVG_ALL':'IDN_CVG','VA_CHE_ALL':'CHE-DJT,CHE-NFI,CHE-NTT,CHE-VAP,CHE-NTS,CHE-PHO,CHE-COX,CHE-CD,VA-CHE-CVG,VA-CHE-Elektron,CHE-GW1','SCW':'STATE CONTROL WATCHDOG'}
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

class _UT(unittest.TestCase):
	"""docstring for _UT"""
	def testOne(self):
		r = Daily_Defect_Report()
		cur_path=os.getcwd()
	
		Files=('CVA_ALL','CVG_ALL','VA_CHE_ALL','SCW')
		Components={'CVA_ALL':'Elektron_CVA','CVG_ALL':'IDN_CVG','VA_CHE_ALL':'CHE-DJT,CHE-NFI,CHE-NTT,CHE-VAP,CHE-NTS,CHE-PHO,CHE-COX,CHE-CD,VA-CHE-CVG,VA-CHE-Elektron,CHE-GW1','SCW':'STATE CONTROL WATCHDOG'}
		Component_Types={'CVA_ALL':'Product','CVG_ALL':'Product','VA_CHE_ALL':'Component','SCW':'Component'}
	
		StartDate=''
		EndDate=''
		current=time.time()
		today=time.gmtime(current)

		StartDate='2010-01-01 1:00AM'
		EndDate=EndDate=str(today[0])+'-'+str(today[1])+'-'+str(today[2])+' 1:00AM'

		#create output path
		output_path=cur_path+"\\raw data\\"
	
		if not os.path.exists(output_path):
			os.mkdir(output_path)
		today_folder=output_path+str(today[0])+str(today[1])+str(today[2])+"\\"
	
		#delete the existing files under output_path
		r.removeFileInDir(output_path)
	
		#Store the TT query results to xml files
		r.Gen_XML_Files(Files,output_path,Components,Component_Types,StartDate,EndDate)

		r.Gen_Full_Defect_Lists(output_path)

if __name__ == "__main_":
	unittest.main()
