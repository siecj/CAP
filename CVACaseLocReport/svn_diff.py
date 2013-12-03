import logging
logging.basicConfig(level=logging.DEBUG)
import os
import sys

def svn_diff(old_tag, new_tag, outfile):
    
    logging.debug("Input Summary:\nOld:"+old_tag+"\nNew:"+new_tag+"\n\n")
    diffcmd = "svn diff --username s.buildrobot.rtcl --password k$.gdAqr}@ --old " + old_tag + " --new " + new_tag + " > " + outfile
    logging.debug("processing..." + diffcmd)
    os.system(diffcmd)
    
if __name__ == '__main__':
    #svn_diff("https://sami.cdt.int.thomsonreuters.com/svn/collections_elektron/CVA/Tags/1.9.0.15", "https://sami.cdt.int.thomsonreuters.com/svn/collections_elektron/CVA/Tags/1.9.0.16", "diffout.txt")
    svn_diff(sys.argv[1], sys.argv[2], sys.argv[3])