import xml.etree.ElementTree as ET
from git import Git
import tarfile
g = Git()
import os
import logging
import sys

def get_remote(root):
    ''' Adding this function so that finding remotes for a given project is a single lookup
        instead of a list(for) loop '''

    remotes = {}
    for data in  root.iter('remote'):
        name = data.attrib['name']
        fetch = data.attrib['fetch']
        remotes[name] = fetch
    return remotes    

def parse_metadata(xmlroot,tarfile,basedir):
    root = xmlroot
    gitremote = get_remote(root)
    for project in root.iter('project'):
        projectdata=project.attrib
        path = projectdata['path']
        remotename=projectdata['remote']
        projectname=projectdata['name']
        try:
           revision=projectdata['revision']
        except KeyError,e:
           revision = 'master'
        print remotename
        try:  
            remoteurl = gitremote[remotename]
        except KeyError:
            remoteurl = None
        if remoteurl is not None:
            giturl = remoteurl+projectname
            gitstr=revision+","+giturl+","+path
            print gitstr
            checkout(gitstr,basedir)
        else:
              logging.warning("git remote url not found for project %s",projectname)
    zipit(basedir,tarfile)

def checkout(git,basedir):
   os.chdir(basedir)
   githash,remoteurl,gitpath = git.split(',')
   print githash,remoteurl,gitpath
   try:
     g.clone(remoteurl,gitpath)
   except:
      logging.warning("Error cloning repo %s",remoteurl)
      return
   
   try:
      os.chdir(os.path.join(basedir,gitpath))
   except:
      logging.warning("Error cloning repository to remote path %s",gitpath)
      return
   try:
      g.checkout(githash)
   except:
      logging.warning("Error githash %s not found, checking out master branch instead",githash)
      g.checkout("master")

def zipit(basedir,tarfilename):
    os.chdir(basedir)
    print " ziping files now"
    print  "tarfile name is " , tarfile
    tar = tarfile.open(tarfilename, "w:gz")
    for name in os.listdir(basedir):
        tar.add(name)
    tar.close()

def main(argv):
   if len(argv) < 3 :
      sys.exit('Usage: python %s xml-file-name tar-file-name' % sys.argv[0] )
   basedir = "zipmyrepo"
   xmlfile = os.path.realpath(argv[1])
   if not os.path.isfile(xmlfile):
      logging.error("File %s does not exist, Please provide the correct file",xmlfile)
      sys.exit()
   tarfile = os.path.realpath(argv[2])
   tree = ET.parse(xmlfile)
   root = tree.getroot()
   tarfile = os.path.realpath(argv[2])
   basedir = os.path.realpath(basedir)
   if not os.path.isdir(basedir):
      os.makedirs(basedir)
   parse_metadata(root,tarfile,basedir)


if __name__  =="__main__":
   sys.exit(main(sys.argv))
