from  colors  import *
from monitor import *
from time import strftime,sleep
from flask import Flask,request,render_template
import tools.yangtest as yangtest
import MySQLdb,redis,ast,requests,json
r = redis.StrictRedis(host='localhost', port=6379, db=0)



db1=MySQLdb.connect(host='localhost', user='root', passwd='123456')
cursor1=db1.cursor()
cursor1.execute("SET sql_notes = 0; ")
cursor1.execute("create database IF NOT EXISTS ivp")

cursor1.execute("create table IF NOT EXISTS ivp.infoofivp(id INT NOT NULL AUTO_INCREMENT,ivpid varchar(60),ip varchar(60),port varchar(60),user varchar(60),phone varchar(60),addressofdevice varchar(60),devicestatus varchar(60),PRIMARY KEY(id));")
db1.commit()
db1.close()



db=MySQLdb.connect(host='localhost', user='root', passwd='123456',db="ivp")
cursor=db.cursor()
#define a function to get table row info and write it to dict
def getrow():
    # commit your changes
    db.commit()
    try:
        tabledict={}
        numrows = int(cursor.rowcount)
        num_fields = len(cursor.description)
        field_names = [i[0] for i in cursor.description]
        for x in range(0,numrows):
            row = cursor.fetchone()
            #print(row)
            tmpdict={}
            for k in range(0,len(row)):
                #print str(field_names[k])+"                 |---------------------------->"+str(row[k]) 
                tmpdict[str(field_names[k])]=str(row[k])
            tabledict[str(x)]=tmpdict
        return tabledict
    except:
        pass





def deleteivp(ivpid):
    print('delete ivp.infoofivp where ivpid='+"'"+str(ivpid)+"'")
    cursor.execute('delete from ivp.infoofivp where ivpid='+"'"+str(ivpid)+"'")
    db.commit()









#parser the ip of ivp device according to ivpid
def parserip(ivpid):
    cursor.execute("select * from infoofivp where ivpid= "+"'"+str(ivpid)+"'")
    registeredinfo=getrow()
    try:
        ip=registeredinfo['0']['ip']
    except:
        ip=''
    print(ip)
    return ip




def accoringiptogetsmiprx(ip):
    ivpgroup=allivpdevice()
    for ivpid in ivpgroup:
        try:
            for k in range(4):
                if r.get(str(ivpid)+'smipge'+str(k+1)+'ip')==ip:
                    if r.get(str(ivpid)+'stream'+str(k+1)+'mode')=='receive':
                        print 'it  will get receive ge,that is rx===============>'
                        return [ivpid,str(k+1)]
        except:
            yangtest.exceptinfo()
            pass









#parser all ivpid in table
def allivpdevice():
    try:
        cursor.execute("select ivpid from infoofivp")
        alldevice=getrow()
    except:
        alldevice=[]
    thenumberofdevices=len(alldevice)
    deviceslist=[]
    for k in  range(thenumberofdevices):
        deviceslist.append(alldevice[str(k)]['ivpid'])
    #in order to check the newest device ,i have reversed the list
    #return deviceslist
    return deviceslist[::-1]














def pinghost(ivpid):
    hostname=parserip(ivpid)
    response = os.system("ping -c 1 " + hostname)

    #anthen check the response...
    if response == 0:
        print hostname, 'is up!'
        result='ok'
    else:
        print hostname, 'is down!'
        result='no'
    return result





def readyboards(ip,encodergroup,decodergroup):
    '''
    request example
    requests.get('http://192.168.0.181/cgi-bin/boardcontroller.cgi?action=get&object=boardmap&id=0.8234045444577069')
    '''
    url='http://'+str(ip)+'/cgi-bin/boardcontroller.cgi?action=get&object=boardmap'
    elegantresponse=ast.literal_eval(requests.get(url).text)
    #according to encoder/decoder list to decide which type is every board
    print elegantresponse
    all=elegantresponse['Body']
    boardsgroup=[i for i in all.keys() if 'status' not in i]
    encoder=[d for d in boardsgroup if all[str(d)] in encodergroup]
    decoder=[d for d in boardsgroup if all[str(d)] in decodergroup]
    print encoder,str(decoder)
    return [elegantresponse,encoder,decoder]



#write all ivps borads to database;
def allivpsboards():
    cursor.execute('select ivpid from infoofivp')
    allivp=getrow()
    print(allivp)
    ivpidgroup=[allivp[i]['ivpid'] for i in allivp.keys()]
    print ivpidgroup
    #result0=readyboards(ip,allencodergroup,alldecodergroup)
    
    allivps=[]
    for k in ivpidgroup:
        ip=parserip(str(k))
        #result0=readyboards(str(ip),allencodergroup,alldecodergroup)
        try:
            print red('are you ok-------------')
            info=readyboards(str(ip),allencodergroup,alldecodergroup)
            tmp=info[0] 
            all=tmp['Body']
            boardsgroup=[i for i in all.keys() if 'status' not in i]
            encoder=[d for d in boardsgroup if all[str(d)] in allencodergroup]
            decoder=[d for d in boardsgroup if all[str(d)] in alldecodergroup]
            print encoder,decoder
            finalgroup={'encoder':encoder,'decoder':decoder}
            #encoder={k:'working' for k in encoder}
            #decoder={k:'working' for k in decoder}
            result1=['0',encoder,decoder]
           

        except:
            result1=['0','','']
        try:    
            allivp.append({'ivpid':k,'ip':ip,'slotlist':{'encodergroup':result1[1],'decodergroup':result[2]}})
        except:
            allivp.append({'ivpid':k,'ip':ip,'slotlist':'error'})

        print red('insert into deviceworkingboard (ivpid,encodergroup,decodergroup) values'+"("+"'"+str(k)+"'"+","+"'"+json.dumps(result1[1])+"'"+","+"'"+json.dumps(result1[2])+"'"+")")
        cursor.execute('insert into deviceworkingboard (ip,ivpid,encodergroup,decodergroup) values'+"("+"'"+str(ip)+"'"+","+"'"+k+"'"+","+"'"+json.dumps(result1[1])+"'"+","+"'"+json.dumps(result1[2])+"'"+")")        
        #cursor.execute("INSERT INTO infoofivp  (ivpid,ip,user,phone,addressofdevice) VALUES" +"("+"'"+str(registerivpid)+"'"+","+"'"+str(registerip)+"'"+","+"'"+str(registeruser)+"'"+","+"'"+str(registerphone)+"'"+","+"'"+str(registeraddress)+"'" +')')

    return allivps
