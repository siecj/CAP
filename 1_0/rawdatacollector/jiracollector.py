from jira.client import JIRA


class JiraQuery():
	def get_jira_defects(self,server,auth,jsl,max_results=1000):
		jira=JIRA(server,auth)
		fields='issuetype,summary,assignee,reporter,status,priority,resolution,created,updated,components'
		issues=jira.search_issues(jsl,maxResults=max_results,fields=fields)

		list=[] 

		for item in issues:
			hash={}
			hash['key']=item.key
			fids=item.fields
			for fid_name in fields.split(','):
				if fid_name == 'components':
					hash[fid_name]=fids.components[0].name
				else:
					attr=getattr(fids, fid_name)
					if str(type(attr))=="<type 'unicode'>":
						hash[fid_name]=attr
					elif attr!=None:
						hash[fid_name]=getattr(attr,'name')
					else:
						hash[fid_name]='None'

			list.append(hash)						

		return list

