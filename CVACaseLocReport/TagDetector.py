from ftplib import FTP
import os,sys,string,datetime,time
import socket
import re
import cPickle
import logging
logging.basicConfig(level=logging.DEBUG)


def tag_cmp(tag1,tag2):
    l1 = tag1.split('.')
    while(len(l1) != 4):  
        l1.append('0') 
    l2 = tag2.split('.')
    while(len(l2) != 4):  
        l2.append('0')
    for i in range(4):
        l1[i] = int(l1[i])
        l2[i] = int(l2[i])
    return cmp(l1,l2)
    
class TagDetector:
    def __init__(self, hostaddr, username, password, remotedir, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir  = remotedir
        self.port     = port
        self.ftp      = FTP()
        self.file_list = []
    def __del__(self):
        self.ftp.close()


    def login(self):
        ftp = self.ftp
        try: 
            timeout = 300
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            logging.debug( u'start to connect to %s' %(self.hostaddr))
            ftp.connect(self.hostaddr, self.port)
            logging.debug( u'connect to %s succesfully' %(self.hostaddr))
            logging.debug( u'login to %s' %(self.hostaddr))
            ftp.login(self.username, self.password)
            logging.debug( u'login to %s succesfully' %(self.hostaddr))
        except Exception:
            logging.debug( u'connect to FTP server %s failed!'  %(self.hostaddr))
            
        try:
            ftp.cwd(self.remotedir)
        except(Exception):
            logging.debug(u'failed to enter dir %s'  %(self.remotedir))
            
    def logout(self):
        self.ftp.quit()

    #get directory list in current server dirctory
    #only number and dot are allowed in the name, other directories are excluded
    #may only work for windows FTP server
    def __get_dir_list(self, line):
        ret_arr = []
        file_name = self.__get_dir_name(line)
        if file_name[0] not in ['.', '..']:
            self.file_list.append(file_name)
              
    def __get_dir_name(self, line):
        pos = line.rfind('>')
        if pos == -1:
            return '.'
        while(line[pos] != ' '):
            pos += 1
        while(line[pos] == ' '):
            pos += 1
        file_name = line[pos:]
        #only number and dot are allowed in the name
        if re.match("^[\d|\.]+$", file_name):
            return file_name
        else:
            #print "remove"+file_name
            return '.'
            
    def get_lastest_tag_list(self):
        self.file_list = []  
        self.ftp.dir(self.__get_dir_list)
        self.__file_list_sort()
        return self.file_list
        
    def get_the_two_tag(self):
        self.get_lastest_tag_list()
        if self.file_list == []:
            print "shitt"
            return []
        hist_list = self.get_history_tag_list();
        index = self.__list_compare(self.file_list, hist_list)
        if index == len(self.file_list)-1:
            return []
        else:
            self.save_history_tag_list()
            return self.file_list[index:index+2]
        
    def get_history_tag_list(self):
        f = open("taglist.txt","rb")
        hist_list = cPickle.load(f)
        f.close()
        return hist_list
    
    def save_history_tag_list(self):
        f = open("taglist.txt","wb")
        cPickle.dump(self.file_list,f)
        f.close()
        pre=str(self.file_list)
        pre=pre.replace("[","")
        pre=pre.replace("]","")+"\n"
        ofile=open("tqglist.txt","wb")
        ofile.write(pre.encode('cp1252'))
        ofile.close()
        
    def __list_compare(self,List1,List2):
        for i in range(0,len(List1)):
            if List1[i]==List2[i]:
                pass
            else:
                break
        #print i
        return i
        
    def __file_list_sort(self):
        self.file_list.sort(cmp=tag_cmp,reverse=True)
        return
        
if __name__ == '__main__':
    hostaddr = '10.35.18.44'
    username = 'anonymous'
    password = ''
    port  =  21
    rootdir_remote = '/CVA/InternalDrop/Core/'

    f = TagDetector(hostaddr, username, password, rootdir_remote, port)
    f.login()
    taglist = f.get_lastest_tag_list()
    latest_two_tags = f.get_the_two_tag()
    print latest_two_tags
    
    
 
