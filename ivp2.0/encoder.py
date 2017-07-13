from ivpdb import *
app = Flask(__name__)
#what happen?2333
#i will test if it work
neededencodergroup=['10']
neededdecodergroup=['21']

#Being ready group ofsingle device     
#look all encoder info in single device//--------these requirements are implemented by mrs yao
@app.route('/ivps/encoders')
def singledeviceencoderinfo(ivpid='test'):
    if ivpid=='test':
        ivpid = request.args.get('ivpid')    
    ip=parserip(str(ivpid))
    #print readyboards(str(ip)
    info=readyboards(str(ip),neededencodergroup,neededdecodergroup)
    encoder=info[1]
    encoderall={}
    allencoder=[]
    print('**********************************************************************************************')
    yangtest.yangshow(encoder)
    print('**********************************************************************************************')
    for i in encoder:
        print i
        encoder={}
        #http://192.168.0.181/cgi-bin/boardcontroller.cgi?action=get&object=slot3&key=status
        #print 'http://192.168.0.181/cig-bin/boardcontroller.cgi?action=get&object='+str(i)+'&key=status'
        info1=requests.get('http://'+str(ip)+'/cgi-bin/boardcontroller.cgi?action=get&object='+str(i)+'&key=status').text
        info2=requests.get('http://'+str(ip)+'/cgi-bin/boardcontroller.cgi?action=get&object='+str(i)+'&key=all').text
        selectedinfo1=ast.literal_eval(info1)
        selectedinfo2=ast.literal_eval(info2)
        print red(str(selectedinfo1))
        requirement1=selectedinfo1['Body']
        requirement2=selectedinfo2['Body']

        encoder_status={'encoding_status':requirement1['status_str'],\
        'video input':requirement1['videoinfo_str'],\
        'audio1to4input':{'audio1input':requirement1['audioinfo_str0'],\
        'audio2input':requirement1['audioinfo_str1'],'audio3input':requirement1['audioinfo_str2'],\
        'audio4input':requirement1['audioinfo_str3'], }}
        


        #print(yellow(str(requirement2)))
        bitratesettingmode=requirement2['bitMode']

        programparameters={'service':requirement2['videoSerName'],\
        'provider':[requirement2['videoPrivoder']],\
        'biterate': [x.strip() for x in requirement2['systemParam'].split(',')][0]}
        
        vp=[x.strip() for x in requirement2['videoParam'].split(',')]
        videoparameters={'source':vp[0],'format':vp[1],'horizontal size':vp[2],'biterate':vp[3],'loss input':vp[-1]}
        ap1=[x.strip() for  x  in requirement2['audioParam0']]
        ap2=[x.strip() for  x  in requirement2['audioParam1']]
        ap3=[x.strip() for  x  in requirement2['audioParam2']]
        ap4=[x.strip() for  x  in requirement2['audioParam3']]
        ap=[ap1,ap2,ap3,ap4]
        
        audioparameters={}
        i=0
        for k in ap:
            i=i+1
            audioparameters['channel'+str(i)]={'source':k[0],'audio enable':k[1],'format':k[2],'loss of input':k[-2]}
        #spree
        
        #bigbang={'position':i,'type':'encoder','status':encoder_status,'setting':{'settingtype':'encoder_setting','bitrate settingmode':bitratesettingmode,'videoParam':videoparameters,'programparameters':programparameters,'audioparameters':audioparameters}}
        bigbang={'type':'encoder','status':encoder_status,'setting':{'settingtype':'encoder_setting','bitrate settingmode':bitratesettingmode,'videoParam':videoparameters,'programparameters':programparameters,'audioparameters':audioparameters}}
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>') 
        print(bigbang) 
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<______________________________________________________________________________-------------------------------------------------------------------------------------')
        r.set(str(ivpid)+'slot'+str(i+1)+'info',bigbang)#this is designed for ivp device info ,but this is ready boards.
        print("==========================================yangming is here=======================================================")
        allencoder.append(bigbang)
        encoder['info1']=info1
        encoder['info2']=info2
        encoderall[str(i)]=encoder
    #print type(encoderall)
    #print encoderall
    print red('i will print big bang')
    print bigbang
    r.set(str(ivpid)+'encodergroup',str(bigbang))
    r.set(str(ivpid)+'encodersstatus',str(bigbang))
    #return json.dumps(encoderall)    
    return json.dumps(bigbang)
    '''
    info1=requests.get('http://192.168.0.181/cig-bin/boardcontroller.cgi?action=get&object='+str(encoder[0])+'&key=status').text
    #encoderall['info1']=info1
    return info1
    '''


def allposfucks(ivpid='test'):
    try:
        ivpidgroup=allivpdevice()
        print ivpidgroup
    except:
        yangtest.exceptinfo()
        r.set('allivpboardsgroup','no ivp devices')
    #the fellowing control flow is to del with the situation that when you delete a database 
    # or the ivp table is empty 

    if str(ivpidgroup)=='[]':
        r.set('allivpboardsgroup','no devices')
    allivpboardsgroup=[]
    boardsgroup=['slot0','slot1','slot2','slot3','slot4','slot5','slot6']
    #i will replace the fellowing line
    #namedict={'11':'HDE','21':'HDO','13':'DDO','28':'SMIP','52':'SMIP-C5','51':'ASI','50':'TSP','42':'ALC','38':'MHDE1','39':'MHDE2','40','IPASIM','41':'MODULATOR','44':'MAPPINGPORT','43':'MAPPING'}
    namedict={'0': 'CAM',
 '1': 'ASI',
 '10': 'HDE',
 '11': 'HDE',
 '12': 'Tuner',
 '13': 'DDO',
 '14': 'ADO',
 '15': 'MDO',
 '16': 'TRM',
 '17': 'IPM_ENC',
 '18': 'MUX',
 '19': 'IP/ASI_ENC',
 '2': 'ASI',
 '20': 'IP/ASI_DEC',
 '21': 'HDO',
 '22': 'Tuner-T',
 '23': 'Tuner-C',
 '24': 'MV',
 '25': 'DSDE',
 '255': 'N/A',
 '26': 'Tuner',
 '27': 'ALC',
 '28': 'SMIP',
 '29': 'Tuner',
 '3': 'ASI',
 '30': 'AVSDEC',
 '31': 'AVSTrans',
 '32': 'AVS FP',
 '33': 'ZW FP',
 '34': 'MHDE3',
 '35': 'SMIP',
 '36': 'MTRA3',
 '37': 'MTRA4',
 '38': 'MHDE1',
 '39': 'MHDE2',
 '4': 'ASI',
 '40': 'IPASIM',
 '41': 'Modulator',
 '42': 'ALC',
 '43': 'Mapping',
 '44': 'MAPPINGPORT',
 '45': 'Tuner',
 '46': 'Tuner',
 '47': 'Tuner',
 '48': 'Tuner',
 '49': 'Tuner',
 '5': 'ASI',
 '50': 'TSP',
 '51': 'ASI',
 '52': 'SMIP-C5',
 '6': 'IP_DEC',
 '7': 'DSDE',
 '8': 'ASDE',
 '9': 'HDE'}


    for k in ivpidgroup:
        ip=parserip(str(k))
        url='http://'+str(ip)+'/cgi-bin/boardcontroller.cgi?action=get&object=boardmap'
        try:
            response=ast.literal_eval(requests.get(url).text)
            slotgroup=response['Body']
            print type(slotgroup)
        except:
            response='no group info'
            slotgroup=''
        slots=[]
        print yellow(str(slotgroup))
        for slot in boardsgroup:
            try:
                slots.append({str(slot):{'name':namedict[str(slotgroup[str(slot)])],'status':slotgroup[str(slot)+'_status']}})
            except:
                #pass
                slots.append({str(slot):{'name':'','status':''}})
       
        print red(str(slots))
        #in june 19 ,i add the device status!in the fellowing line
        #for some things,i set  the device status to be the device netowk satus
        allivpboardsgroup.append({'id':k,'ip':str(parserip(str(k))),'status':r.get(str(k)+'netstatus'),'slot_list':slots})
    print('+++++++++++++++++++++++++++++++++allivpboardsgroup++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++') 
    print(allivpboardsgroup)
    #sleep(10)
    r.set('allivpboardsgroup',allivpboardsgroup)






'''
for  k in range(5):
    yangtest.yangshow("tell me why")
    allposfucks()
    print('i will  sleep 100------------------------------------------------------------------------>')
    sleep(100)

'''




def pollingdevices(alldevice):
    if str(alldevice)=='[]':
        #sleep(10)
        return
    try:
        for ivp in alldevice:
            yangtest.dividingline()
            print "i was running encoder"
            singledeviceencoderinfo(ivp)
            #allposfucks()
            #allposfucks()
            #sleep(10) 
    except:
        sleep(1)

#pollingdevices(alldevices)




for k in range(1000000):
    alldevices=allivpdevice()
    yangtest.yangshow(alldevices)
    pollingdevices(alldevices)
    allposfucks()











'''



for k in range(10):
    singledeviceencoderinfo(ivpid='ivp201705170754')
    #singledevicedecoderinfo(ivpid='ivp201705170754')
    #getsmip1(ivpid='ivp201705170754')
    allposfucks()


'''

if __name__ == '__main__':
   app.run('0.0.0.0',90,debug='True')

