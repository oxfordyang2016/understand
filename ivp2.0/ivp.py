from ivpdb import *
app = Flask(__name__)
from tools import yangtest

#board group
allencodergroup=['7','8','9','10','11','17','19','25','34' ,'38','39' ]
alldecodergroup=['6','13','14','20','21','30']
tmp='7 8  9 10 11 17 19 25 34 38 39 6 13 14 20 21 30'
neededencodergroup=['10']
neededdecodergroup=['21']
apiversion='1.0'


@app.route('/')
def hello_world():
    #return 'hello world'
    return render_template("index.html")

@app.route('/streams')
def hello_world1():
    #return 'hello world'
    return render_template("index.html")



@app.route('/devices')
def hello_world2():
    #return 'hello world'
    return render_template("index.html")




@app.route('/api/v')
def version():
    versionofapi={'version':apiversion}
    return json.dumps(versionofapi)

@app.route('/api/errorcodes')
def errorcodes():
    errorcodelist=[{'0':'success'},{'11':'fail to query device status'},{'211':'errorcode api  internal error'}]
    try:
        return json.dumps({'errorcodelist':errorcodelist,'errorcode':0})
    except:
        return json.dumps({'errorcodelist':errorcodelist,'errorcode':211})


#register ivp
#r=requests.post('http://192.168.201.142:50/ivps',json={'ip':'192.168.50.182','user':'yangming','addressofdevice':'shanghai','phone':'110'})
@app.route('/ivps',methods = ['POST'])
def register():
    if request.method == 'POST':
        #user = request.form['user']
        getjson=request.get_json(force=True)
        registeruser=getjson['user']
        registerip=getjson['ip']
        registeraddress=getjson['addressofdevice']
        registerphone=getjson['phone']
        try:
            registerport=getjson['port']
        except:
            registerport = 80        
        registerivpid='ivp'+strftime('%Y%m%d%H%M')
        ivpinfo={'user':registeruser,'ip':registerip,'ivpid':registerivpid,\
                 'addressofdevice':registeraddress,'phone':registerphone,'errorcode':1,'port':registerport}
        cursor.execute("INSERT INTO infoofivp  (ivpid,ip,port,user,phone,addressofdevice) VALUES"\
                   +"("+"'"+str(registerivpid)+"'"+","+"'"+str(registerip)+"'"+","+"'"+str(registerport)+"'"+","+"'"+\
                   str(registeruser)+"'"+","+"'"+str(registerphone)+"'"+","+"'"+\
                   str(registeraddress)+"'" +')')
        db.commit()
        return json.dumps(ivpinfo)

      

#lookup registered ivp device
@app.route('/ivps/registered')
def registered(*args):
    ivpid = request.args.get('ivpid')
    print str(ivpid)+'ivp id is here'
    if ivpid!=None:
        cursor.execute("select * from infoofivp where ivpid= "+"'"+str(ivpid)+"'")
        print 'the line is  a bug---------------'
        registeredinfo=getrow()
    else:
        print 'i have enter except part--------------->'
        cursor.execute("select ivpid,devicestatus from infoofivp")
        print "select ivpid,devicestatus from infoofivp"
        registeredinfo=getrow()
        print registeredinfo
    
    return json.dumps(registeredinfo)









@app.route('/ivps/delete')
def delete():
    import ivpdb
    try:
        ivpid=request.args.get('ivpid')
        ivpdb.deleteivp(ivpid)
        return json.dumps({'errorcode':222,'status':'delete successfully'})
    except:
        yangtest.exceptinfo()  
        return json.dumps({'errorcode':11,'status':'failed'})
        pass
    



def getivpversion(ivpid):
    ip=parserip(ivpid)
    #get ivp main board info
    content=requests.get('http://'+str(ip)+'/cgi-bin/system.cgi?action=get&object=dev&key=all').text
    result=ast.literal_eval(content)
    ivpinfo=result['Body'] 
    t=ivpinfo
    ivpresult={'sn':t["sn"],'hdver':t["hdver"],'swver':t['swver'],"model":t['mode'],'devicename':t["Device_Name"]}   
    



def getboardsversion(ivpid):
    ip=parserip(ivpid) 
    #get ivp boards info ,that is all kinds of boards
    content1=requests.get('http://'+str(ip)+'/cgi-bin/system.cgi?action=get&object=hdnum&slot=all').text
    result1=ast.literal_eval(content1)
    boardsinfo=result1['Body']
    

    #get software info 
    content2=requests.get('http://'+str(ip)+'/cgi-bin/boardcontroller.cgi?action=get&object=bdinfo&slot=all').text
    result2=ast.literal_eval(content2)
    boardsinfo1=result2['Body']
    
    return [boardsinfo,boardsinfo1]















@app.route('/ivps',methods=['GET'])
def workstatus(*args):
    ivpid = request.args.get('ivpid')
    if ivpid!=None:
        print('i am look for all status')
        return json.dumps(ast.literal_eval(r.get('ivp201705170754')))
    cursor.execute("select ivpid,devicestatus from infoofivp ")
    status=getrow()
    thenumberofivpid=len(status)
    statuslist=[]
    for k in range(thenumberofivpid):
        statuslist.append({str(status[str(k)]['ivpid']):status[str(k)]['devicestatus']})
    try:
        result={'statuslist':statuslist,'errorcode':0}
    except:
        #tmp error code =11
        result={'statuslist':'','errorcode':11}    
    return json.dumps(result)




#look encoder info
#analysis which boads is  ready in ivp device according to ip

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
        print red('insert into deviceworkingboard (ivpid,encodergroup,decodergroup) values'+"("+"'"+str(k)+"'"+","+"'"+json.dumps(result1[1])+"'"+","+"'"+json.dumps(result1[2])+"'"+")")
        cursor.execute('insert into deviceworkingboard (ip,ivpid,encodergroup,decodergroup) values'+"("+"'"+str(ip)+"'"+","+"'"+k+"'"+","+"'"+json.dumps(result1[1])+"'"+","+"'"+json.dumps(result1[2])+"'"+")")        
        #cursor.execute("INSERT INTO infoofivp  (ivpid,ip,user,phone,addressofdevice) VALUES" +"("+"'"+str(registerivpid)+"'"+","+"'"+str(registerip)+"'"+","+"'"+str(registeruser)+"'"+","+"'"+str(registerphone)+"'"+","+"'"+str(registeraddress)+"'" +')')





#allivpsboards()


#give positions info  to front

@app.route('/ivps/allpos1')
def getallpostions(*args):
    cursor.execute("select ip,ivpid,encodergroup,decodergroup from deviceworkingboard")
    allrow=getrow()
    item={}
    ivplist=[]
    for k in range(len(allrow)):
        try:
            ip=allrow[str(k)]['ip']
        except:
            ip=ast.literal_eval(allrow[str(k)]['ip'])
        try:
            ivpid=allrow[str(k)]['ivpid']
        except:
            ivpid=ast.literal_eval(allrow[str(k)]['ivpid'])
        try:
           print 'i m eval'
           encoder= ast.literal_eval(allrow[str(k)]['encodergroup']) 
           decoder= ast.literal_eval(allrow[str(k)]['decodergroup'])
        except:
           print red('i can not convert')
           encoder= allrow[str(k)]['encodergroup']
           decoder= allrow[str(k)]['decodergroup']
        item={'ivpid':ivpid,'encoder':encoder,'decoder':decoder,'ip':ip}
        ivplist.append(item)
    print ivplist
    result={'errorcode':'233','ivplist':ivplist}
    print red(str(result))
    
    #print allrow[str(i)]['encodergroup']
    
    #result={"ivplist":[{'ivpid':allrow[str(i)]['ivpid'],'encoder':allrow[str(i))]['encodergroup'],'decoder':allrow[str(i)]['decodergroup']}  for i in  range(len(allrow))],"errorcode":0}
    #print result
    '''
    result= json.dumps(result)
    test=result.replace('\\"',"\"")
    return test
    '''
    return json.dumps(result) 



#get single device work status
@app.route('/ivps/readygroup')
def singledevicereadygroup():
    
    ivpid = request.args.get('ivpid')
    ip=parserip(str(ivpid))
    #print readyboards(str(ip)
    info=readyboards(str(ip),allencodergroup,alldecodergroup)
    k=info[0] 
    all=k['Body']
    boardsgroup=[i for i in all.keys() if 'status' not in i]   
    encoder=[d for d in boardsgroup if all[str(d)] in allencodergroup]
    decoder=[d for d in boardsgroup if all[str(d)] in alldecodergroup]
    print encoder,decoder
    finalgroup={'encoder':encoder,'decoder':decoder}
    print yellow(str(finalgroup)) 
    return json.dumps(finalgroup)
    


#lookup decoder info in single device   

@app.route('/ivps/encoders')
def singledeviceencoderinfo(ivpid='test'):
    if ivpid=='test':
        ivpid = request.args.get('ivpid')
    result=r.get(str(ivpid)+'encodersstatus') 
    finalresult=ast.literal_eval(result)     
    return json.dumps(finalresult)



#lookup decoder info in single device   

@app.route('/ivps/decoders')
def singledevicedecoderinfo(ivpid='test'):
    if ivpid=='test':
        ivpid = request.args.get('ivpid')
    result=r.get(str(ivpid)+'decodersstatus') 
    finalresult=ast.literal_eval(result)     
    return json.dumps(finalresult)










@app.route('/ivps/allpos')
#0531 i use the new fucntion
def allpofucks(ivpid='test'):
    allivpboardsgroup=r.get('allivpboardsgroup')
    try:
        allivpboardsgroup=ast.literal_eval(allivpboardsgroup)
    except:
        allivpboardsgroup='the current have no refistred device'
    print yellow(str(allivpboardsgroup))
    return json.dumps({'errorcode':0,"ivp_list":allivpboardsgroup})


testdata={"errorcode": "200", "linklist": [{"status": "running", "device_list": [{"ip": "192.168.0.211", "id": "ivpid20170601", "board_list": [{"status": "ready", "position": "slot3", "type": "encoder", "name": "HDE_In1"}, {"status": "ready", "ip": "192.168.1.211", "type": "smiptx", "name": "smip", "position": "ge1"}]}, {"ip": "192.168.1.23", "id": "ivpid2017088", "board_list": [{"status": "ready", "ip": "192.168.0.160", "destinationivp": "ivp201705170754", "type": "smip", "position": "ge3"}, {"status": "ok", "position": "slot4", "type": "decoder", "name": "name"}]}]}, {"status": "running", "device_list": [{"ip": "ip", "id": "ivpid", "board_list": [{"status": "ready", "position": "mux", "type": "encoder", "name": "MUX1_Out"}, {"status": "ready", "ip": "192.168.1.211", "type": "smiptx", "name": "smip", "position": "ge2"}]}, {"ip": "ip", "id": "id", "board_list": [{"status": "ready", "ip": "192.168.1.211", "destinationivp": "ivp201705170754", "type": "smip", "position": "ge4"}, {"status": "ok", "position": "position", "type": "decoder", "name": "name", "decoder": "slot4"}]}]}, {"status": "running", "device_list": [{"ip": "ip", "id": "ivpid", "board_list": [{"status": "ready", "position": "mux", "type": "encoder", "name": "MUX1_Out"}, {"status": "ready", "ip": "192.168.1.211", "type": "smiptx", "name": "smip", "position": "ge3"}]}, {"ip": "ip", "id": "id", "board_list": [{"status": "ready", "ip": "192.168.0.160", "destinationivp": "ivp201705170754", "type": "smip", "position": "ge3"}, {"status": "ok", "position": "position", "type": "decoder", "name": "name"}]}]}]}




#lookup smip info
@app.route('/smip')
def getsmip(ivpid='test'):
    if ivpid=='test':
        ivpid = request.args.get('ivpid')
    result=r.get(str(ivpid)+'smipinfo')
    finalresult=ast.literal_eval(result)     
    return json.dumps(finalresult)



@app.route('/stream')
def getalllink():
    linklist=[]
    ivpidlist=allivpdevice()
    """
    in order to fix the bug ,that is ,when a host cannot be arrived 
    the stream status can not be  updated!!!!i add 
    """    
    for k in ivpidlist:
        try:
            singleivplink=r.get(str(k)+'streamgroup')
            result=ast.literal_eval(singleivplink)
            #linklist.append({k:result})
            print yellow(str(result))
            for linknumber in range(len(result)):
                linklist.append(result[linknumber])  
        except:
            #linklist.append({k:''})
            #linklist.append('')
            pass
    finalresult={'errorcode':'200','linklist':linklist}
    
    return json.dumps(finalresult)
    #return json.dumps(testdata)



#lookup smip info
@app.route('/ivps/singledevice')
def singledevice(ivpid='test'):
    if ivpid=='test':
        ivpid = request.args.get('ivpid')
    #encoder info,decoder info,smip info
    #r.set(str(ivpid)+'encodergroup',str(bigbang))
    #r.set(str(ivpid)+'decodergroup',decoder) 
    #r.set(str(ivpid)+'smipinfo',allinfo)




    encoderinfo=r.get()
    decoderinfo=r.get()
    smipinfo=r.get()
    singledeviceallinfo=[coderinfo,decoderinfo,smipinfo]
    result={'errorcode':200,allinfo:singledeviceallinfo}     
    return json.dumps(singledeviceallinfo)





#lookup all requirement info instatus that is proveded by fuck yao!!!
@app.route('/ivps/allinfo2')
def allinfo(ivpid='test'):
    alldevice=allivpdevice()
    allinfo=[]
    for ivpid in alldevice:
        encoder=r.get(str(ivpid)+'encodergroup')
        decoder=r.get(str(ivpid)+'encodergroup')
        smip=r.get(str(ivpid)+'smipinfo')
        id=ivpid
        info={'id':ivpid,'encoder':encoder,'decoder':decoder,'smip':smip}
        allinfo.append(info)
    return json.dumps(allinfo)




#this is for look up alldevice info
@app.route('/ivps/allinfo1')
def allinfo1():
    alldevice=allivpdevice()
    allinfo=[]
    #for  position in range(7):
    for ivpid in  alldevice:
        info=[]
        for k in range(7):
            try:
                final_info=ast.literal_eval(r.get(str(ivpid)+'slot'+str(k)+'info'))
            except:
                final_info='no'
               
            info.append({'position':'slot'+str(k),'info':final_info})
        allinfo.append({'id':ivpid,'info':info}) 
    return json.dumps(allinfo) 






@app.route('/ivps/allinfo',methods=['GET'])
def allinfoget(*args):
    ivpid = request.args.get('ivpid')
    info=[]
    for k in range(7):
        try:
            final_info=ast.literal_eval(r.get(str(ivpid)+'slot'+str(k)+'info'))
        except:
            final_info='no'
        info.append({'position':'slot'+str(k),'info':final_info})
    #errorcode is ok!
    finalinfo={'id':ivpid,'errorcode':23,'info':info}
    return json.dumps(finalinfo)










@app.route('/ivps/simplestreams')
def simplestream():
    alldevice=allivpdevice()
    workingstream=[]
    badstream=[]
    for ivp in alldevice:
        for k in range(1,5):
            if r.get(str(ivpid)+'stream'+str(k)+'modestatus')=='ok':
                workingstream.append({'id':ivp,'status':'working','smipport':k})
            if r.get(str(ivpid)+'stream'+str(ge+1)+'modestatus')=='no':
                badstream.append({'id':ivp,'status':'bad','smipport':k})
    
    result={'errorcode':233,'workingstream':workingstream,'badstream':badstream}
















if __name__ == '__main__':
   app.run('0.0.0.0',50,debug='True')

