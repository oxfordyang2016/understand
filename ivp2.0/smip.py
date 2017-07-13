import ivpdb
from  ivpdb  import *
app = Flask(__name__)


#get smip phy and stream setting info
def getsmipge(ivpid,ge):
    """
    according to discuss wtih  college ,that is , wangyanjie ,wanglei,
    i get the info ,i need to check that when the checkbox is checked
    in the stream graph,i need to check the stream wheather is sending 

    """




    ip=parserip(str(ivpid))
    """
    the group try and except is for the goal.i need to detect if
    the communicate of corresponding ge or stream  is ok!!!! 
    """
    try:
        #the smipinfo0 is used to get stream info
        smipinfo0=requests.get('http://'+str(ip)+\
        '/cgi-bin/boardcontroller.cgi?action=get&object=slot6&key=channel_status&instanceID='+str(ge)).text
        
        smipinfo1=requests.get('http://'+str(ip)+\
        '/cgi-bin/boardcontroller.cgi?action=get&object=slot6&key=ip_profile&instanceID='+str(ge)).text
    except:
        return {'alarm':'communicte error','smip-stream'+str(ge):'','smipgessetting'+str(ge):''}


    """
    i donnot know what to say,fucking !!!!
    """




    try:
        smipinfo0,smipinfo1=ast.literal_eval(smipinfo0),ast.literal_eval(smipinfo1)
        print blue(str(smipinfo1))
        net0=key1=smipinfo1['Body']
        key0=smipinfo0['Body']['channel_status']

        """
        i design the mechnism,that is,when the stream corresponding box is checked
        i save the value in the redis ,that is,1.or i will save 0 in redis
        r.set(str(ivpid)+'stream'+str(ge+1)+'boxcheck',1)
        """
        r.set(str(ivpid)+'stream'+str(ge+1)+'boxcheck',1)
    except:
        yangtest.exceptinfo()
        #the fellowing line is used to express that when the smip ge is not set well,i need to think the smip link doesnot exsit
        r.set(str(ivpid)+'stream'+str(ge+1)+'modestatus','no')
        r.set(str(ivpid)+'stream'+str(ge+1)+'boxcheck',1)
        return {'ge':'ge'+str(ge+1),'alarm':'smip set error','smipstream':'','smipgessetting':''}
    try:
        st0=ast.literal_eval(key0)
        st1=ast.literal_eval(st0['i'])
        r.set(str(ivpid)+'stream'+str(ge+1)+'mode','receive')
        st2=st1['orr']
    except:
        """
        the except group is used to say the ge or stream is used to send/receive


        u must care about the group,that is ,the stream is send and detect the strem is  ok!
        """


        st0=(ast.literal_eval(key0))
        
        st1=ast.literal_eval(st0['o'])
        r.set(str(ivpid)+'stream'+str(ge+1)+'mode','send')
        st2=st1['orr']
        st3=st1['rrar']
        st4=st1['rt']
        if 'Sending' in st1['msg']:
            r.set(str(ivpid)+'stream'+str(ge+1)+'modestatus','ok')
            #i will add realtime biterate
            r.set(str(ivpid)+'stream'+str(ge+1)+'realtimebiterate',st4)            

        if int(st2)!=0 and int(st3)!=0:
            r.set(str(ivpid)+'stream'+str(ge+1)+'modestatus','ok')
        else:
            r.set(str(ivpid)+'stream'+str(ge+1)+'modestatus','no')
    '''
    stream={'stream buffertime':"st0['bf']",'stream-setting':{'orr':st0['orr'],'rrar':st0['rrar'],
               'ip':st0['ipaddress'],'port':st0['ipport'],'setting-status':st0['msg'],
               'disconnect':st0['off_t'],'source':st0['source'],

                      'ge':st3['ge'],'mode':st0['status']}}
    '''    
    yangtest.yangshow(str(ivpid)+'status mode===>'+str(st1['status'])) 
    r.set(str(ivpid)+'ge'+str(ge)+'streamstatus',st1['msg'])
    #the fellwoing comment line is ok!
    #stream={'stream'+str(ge+1)+'settingip':st1['ipaddress']}
    stream={'streamsettingip':st1['ipaddress']}
    r.set(str(ivpid)+'stream'+str(ge+1)+'settingip',st1['ipaddress'])
    net1=ast.literal_eval(net0['ip_profile'])
    geinfo={'Network setting':{'work mode':net1['ipmode'],'mask':net1['mask'],\
            'gateway':net1['ge'],'ip':net1['ad']},'phy configuration':{'an':net1["an"],\
            'phy speed':net1['spddup'],'status':net1['s']}}
    r.set(str(ivpid)+'smipge'+str(ge+1)+'ip',net1['ad'])
    #the fellowing comment line is working properly
    #infogroup={'smip-stream'+str(ge):stream,'smipgessetting'+str(ge):geinfo}
    infogroup={'ge':'ge'+str(ge+1),'alarm':'','smipstream':stream,'smipgessetting':geinfo}     
    return infogroup



def getsmip(ivpid):
    allinfo={}
    slot6info=[]
    smipinfo={}
    for k in range(4):
        allinfo['info'+str(k+1)]=getsmipge(ivpid,k)
        slot6info.append(getsmipge(ivpid,k))
    r.set(str(ivpid)+'smipinfo',allinfo)
    smipinfo={'type':'smip','status':'ok','infogroup':slot6info}
    #r.set(str(ivpid)+'slot6info',slot6info)
    r.set(str(ivpid)+'slot6info',smipinfo)
#i mam testing the connection

#get every device smip stream source 
@app.route('/link')
def getlink(ivpid='test'):
    if ivpid=='test':
        ivpid=request.args.get('ivpid')
    ip=parserip(str(ivpid))
    try:    
        stream1=requests.get('http://'+str(ip)+\
        '/cgi-bin/boardcontroller.cgi?action=get&object=router&slotid=slot6&slotport=SMIP_Out0').text
        stream2=requests.get('http://'+str(ip)+\
        '/cgi-bin/boardcontroller.cgi?action=get&object=router&slotid=slot6&slotport=SMIP_Out1').text
        stream3=requests.get('http://'+str(ip)+\
        '/cgi-bin/boardcontroller.cgi?action=get&object=router&slotid=slot6&slotport=SMIP_Out2').text
        stream4=requests.get('http://'+str(ip)+\
        '/cgi-bin/boardcontroller.cgi?action=get&object=router&slotid=slot6&slotport=SMIP_Out3').text
        st1,st2,st3,st4=ast.literal_eval(stream1),ast.literal_eval(stream2),ast.literal_eval(stream3),ast.literal_eval(stream4)
    except:
        print 'stream error'
    try:
        if st1['Body']['Route_records']!=[]:
            r.set(str(ivpid)+'stream1source',\
                [st1['Body']['Route_records'][0]['src_id'],st1['Body']['Route_records'][0]['src_port']])
        r.set(str(ivpid)+'stream1',st1)
    except:
        r.set(str(ivpid)+'stream1','no')    
    try:
        if st2['Body']['Route_records']!=[]:
            r.set(str(ivpid)+'stream2source',\
                [st2['Body']['Route_records'][0]['src_id'],st2['Body']['Route_records'][0]['src_port']])        

        r.set(str(ivpid)+'stream2',st2)
    except:
        r.set(str(ivpid)+'stream2','no') 
    try:
        if st3['Body']['Route_records']!=[]:
            r.set(str(ivpid)+'stream3source',\
                [st3['Body']['Route_records'][0]['src_id'],st3['Body']['Route_records'][0]['src_port']])        
        r.set(str(ivpid)+'stream3',st3)
    except:
        r.set(str(ivpid)+'stream3','no') 
    try:
        r.set(str(ivpid)+'stream4',st4)
        if st4['Body']['Route_records']!=[]:
            r.set(st(ivpid)+'stream4source',[st4['Body']['Route_records'][0]['src_id'],st4['Body']['Route_records'][0]['src_port']])        
    except:
            r.set(str(ivpid)+'stream4','no') 
    return 'test'



#detect that a given ip in which ge of which ivp smip
def singleivpsmipipsettinggroup(ivpid):
    ipgroup=[]
    for ge in range(4):
        #print('ge is '+str(ge)+r.get(str(ivpid)+'smipge'+str(ge+1)+'ip')) 
        ipgroup.append(r.get(str(ivpid)+'smipge'+str(ge+1)+'ip'))
    print green(str(ipgroup))
    return ipgroup

def accrodingtoiptogetivp(ip):
    #ivpgroup=['ivp201705170754']
    ivpgroup=allivpdevice()
    ivpsmipsettingipgroup={}
    for ivpid in ivpgroup:
        ivpsmipsettingipgroup[str(ivpid)]=singleivpsmipipsettinggroup(ivpid)
    #print yellow(str(ivpsmipsettingipgroup))
    for key in ivpsmipsettingipgroup:
        if str(ip) in ivpsmipsettingipgroup[str(key)]:
            #print red(str(ivpsmipsettingipgroup[str(key)]))
            #print 'the device is '+str(key)
            #get device id and ge position
            print('this device is '+str(key)+' ge is ge'+str(ivpsmipsettingipgroup[str(key)].index(str(ip))+1))
            #break
            return [key,str(str(ivpsmipsettingipgroup[str(key)].index(str(ip))+1))]


'''
def accoringiptogetsmiprx(ip):
    ivpgroup=allivpdevice()
    for ivpid in ivpgroup:
        try:
            for k in range(4):
                if r.get(str(ivpid)+'smipge'+str(k+1)+'ip')==ip:
                    if r.get(str(ivpid)+'stream'+str(k+1)+'mode')=='receive':
                        return [ivpid,'ge'+str(k+1)]
        except:
            yangtest.exceptinfo()
            pass

'''









#what is wrong
def completelink(ivpid='test'):
    if ivpid=='test':
        ivpid=request.args.get('ivpid')
    #singlesmipgroup=[{'stream'+str(k+1):r.get(str(ivpid)+'stream'+str(k+1)+'source')} for k in range(4) ]
    
    #singlesmipgroup=[{'stream'+str(k+1):r.get(str(ivpid)+'stream'+str(k+1)+'source')} for k in range(4) if r.get(str(ivpid)+'stream'+str(k+1)+'mode')=='send' ]
    singlesmipgroup=[{'stream'+str(k+1):r.get(str(ivpid)+'stream'+str(k+1)+'source')} for k in range(4) if r.get(str(ivpid)+'stream'+str(k+1)+'mode')=='send' and r.get(str(ivpid)+'stream'+str(k+1)+'modestatus')=='ok' ]
    #get single ivp device smip send (and the status is sending )
    singlesmipgroup1=[k+1 for k in range(4) if r.get(str(ivpid)+'stream'+str(k+1)+'mode')=='send'] 
    print yellow(str(singlesmipgroup1))
    #yangtest.position()
    deviceip=parserip(ivpid)
    '''
    if pinghost(deviceip)=='no':
        r.set(str(ivpid)+'streamgroup',[])
        return
    '''



    yangtest.dividingline()
    print yellow(str(singlesmipgroup))
    count=1
    singleivpdevicelink=[]
    if str(singlesmipgroup)=='[]':
        r.set(str(ivpid)+'streamgroup',[])
    try:    
        for k in singlesmipgroup:
            print yellow('the curent device is '+str(ivpid)+'****')
            try:
                info=ast.literal_eval(k['stream'+str(count)])
          
            except:
                print('thers is a bug')
                #r.set(str(ivpid)+'streamgroup',[])
                #return 
            try:
                streamstatus=r.get(str(ivpid)+'ge'+str(count-1)+'streamstatus')
            except:
                streamstatus='Not work'
            #print(yellow(streamstatus))
            if info!=None:
                print('this stream'+str(count)+' encoder is the fellowing')
                print(info[0])
                print('this stream encoder type is')
                print(info[1])
                print('the smip tx ip is the fellowing')
                print(r.get(str(ivpid)+'smipge'+str(count)+'ip'))
                smiptxip=r.get(str(ivpid)+'smipge'+str(count)+'ip')
                print('this stream distination rx smip ip is')
                print(r.get(str(ivpid)+'stream'+str(count)+'settingip'))
            
                rxip=r.get(str(ivpid)+'stream'+str(count)+'settingip')
                print rxip
                #yangshow(ip)
                des11=ivpdb.accoringiptogetsmiprx(rxip)
                yangtest.yangshow('the problem should be there'+str(des11)+' this si des11---------')
                yangtest.yangshow(des11)
                #ivpdb.yangshow(des11)
                #des=accoringiptogetsmiprx(ip)
                #yangtest.position()
                #yangtest.yangshow(str(des))
                print 'the destination ivp is the bellow '
                print des11[0]
                print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                yangtest.yangshow('i donot understand what happen---')
                print 'the ip of destination ivp'
                receivingdeviceip=parserip(str(des11[0]))
                print receivingdeviceip
                print 'the distinantion ge is '
                print str(des11[1])


                #print('this stream desitination rx in fellowing device')
                destination=accrodingtoiptogetivp(str(rxip))
                #yangtest.yangshow(destination)
                try:
                    #coivp,coge=destination[0],destination[1] 
                    coivp,coge=des11[0],des11[1]
                except:
                    coivp,coge='device problem','20000'
                try:
                    print 'i will print des 11'
                    print des11[0],des11[1]
                except:
                    print 'if i am here ,the des has bug!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

                #print('the destination ivp is '+str(coivp))
                #print('this device corresponding ge is ge'+str(coge))
                print coivp,coge
                
                print('the corresponding decoder position')
                print(r.get(str(coivp)+'SMIP_In'+str(int(coge)-1)))
                #decoderpostion=r.get(str(coivp)+'SMIP_In'+str(int(coge)-1))
                #print('')
                #yangtest.yangshow(r.get(str(coivp)+'SMIP_In'+str(int(coge)-1)))
                if r.get(str(coivp)+'SMIP_In'+str(int(coge)-1))==None:
                    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                    decoder="no"
                
                if r.get(str(coivp)+'stream'+str(count)+'settingip')==None:
                    print "i dislike==================================================>"                     
                    ip="no"
                
                #ip11='no'
                #yangtest.divingline()
                yangtest.yangshow('yangming is herer')
                streamrealtimebiterate=r.get(str(ivpid)+'stream'+str(count)+'realtimebiterate')
                detectedlink={'status':'running','streamrealtimebitrate':streamrealtimebiterate,'device_list':[{'ip':deviceip,'id':ivpid,"board_list":[{'name':info[1],
                                                                                                             'type':'encoder',
                                                                                                              'status':'ready',
                                                                                                              'position':info[0]},
                                                                                                             {'name':'smip',
                                                                                                              'ip':smiptxip,
                                                                                                              'type':'smiptx',
                                                                                                              'position':'ge'+str(count),
                                                                                                              'status':'ready'}
                                                                                                            ]}
                                                                       ,{'ip':receivingdeviceip,'id':des11[0],'board_list':[{'ip':r.get('stream'+str(count)+'settingip'),\
                                                                                                            'destinationivp':str(coivp),
                                                                                                             'position':'ge'+str(coge),
                                                                                                             'type':'smiprx',
                                                                                                            'status':'ready'},
                                                                                                           {'type':'decoder',
                                                                                                            'position':'decoderposition',
                                                                                                             'name':'',
                                                                                                             'status':'ok',
                                                                                                             'decoder':r.get(str(coivp)+'SMIP_In'+str(int(coge)-1))}
                                                                                                             ]
                                                                         }

]



}








            singleivpdevicelink.append(detectedlink)
            print("what is =========================================================>")
            count+=1
            print yellow(str(singleivpdevicelink))
            r.set(str(ivpid)+'streamgroup',singleivpdevicelink)
    except:
        yangtest.exceptinfo()
        r.set(str(ivpid)+'streamgroup',[])










def finalsmip(alldevice):
    if str(alldevice)=='[]':
        print('i was sleeping in smip')
        #sleep(10)
        return
    try:
        for ivpid in alldevice:
            print('i was sleeping')
            getsmip(ivpid)
            getlink(ivpid)
            completelink(ivpid)
            #sleep(10)
    except:
        print('i was sleeping')
        yangtest.exceptinfo()
        #sleep(10)




for k in range(100000):
    alldevice=allivpdevice()
    finalsmip(alldevice)





'''



for k in range(1):
    getsmip(ivpid='ivp201705170754')
    getlink(ivpid='ivp201705170754')
    getsmip(ivpid='ivp201705232247')
    getlink(ivpid='ivp201705232247')
    completelink(ivpid='ivp201705170754')
    completelink(ivpid='ivp201705232247')
'''

#des=ivpdb.accoringiptogetsmiprx('192.168.0.160')
#print des
#print alldevice

#ivp201705232247
if __name__ == '__main__':
   app.run('0.0.0.0',70,debug='True')

