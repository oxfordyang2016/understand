import re,os
import tools.yangtest as yangtest
#get stoplog file content


def getfileeverylinetolist(fname):
    with open(fname) as f:
       content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

def extractstuff(source,index):
    targetgroup=[]
    for k in source:
        target=k.split()
        yangtest.yangshow(target)
        try:
            targetgroup.append(target[index])
        except:
            pass
    return targetgroup


#the fellowing filw is to extract pid
stoploglines=getfileeverylinetolist('./loggroup/stoplog')
print(stoploglines)
finalgroup=[x for x in stoploglines if 'grep' not in x]
yangtest.yangshow(finalgroup)
pids=extractstuff(finalgroup,1)


#kill these pid
for k in pids:
    os.system('kill -9 '+str(k))












 









