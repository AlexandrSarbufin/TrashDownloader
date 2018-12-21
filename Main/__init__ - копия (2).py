import os.path
import urllib.request
from urllib.error import  URLError, HTTPError
import json
from datetime import datetime



TrashUrl = 'http://pomoyka.win/trash/ttv-list/'
TrashFile = 'ttv.json'
LastModifiedFile = 'last_modified.txt'
ChannelBase = 'Channel_base'


def GetLastModified():
    
    if os.path.exists(LastModifiedFile):
        with open(LastModifiedFile, 'r') as f: LastModified = f.read()
    else:
        print(str(LastModifiedFile)+'not found.')
        LastModified = 'Sun, 06 Nov 1994 00:00:00 GMT'
        with open(LastModifiedFile,'w') as f:            
            f.write(LastModified)
            print(str(LastModifiedFile)+' saved.')
            
    return LastModified
  

def GetHeaders(forceUpdate):
    
    headers = {}
    
    headers['User-Agent'] = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
    headers['Accept'] = 'text/html, application/xml, application/xhtml+xml, */*'
    headers['Accept-Language'] = 'ru,en;q=0.9'
    
    if not forceUpdate:
        try:
            with open(LastModifiedFile, 'r') as f:
                headers['If-Modified-Since'] = f.read()
        except Exception as e:
            print(str(LastModified) + ' READ ERROR.')
            headers['If-Modified-Since'] = 'Sun, 06 Nov 1994 00:00:00 GMT'
    else:
        print('Force update')   
    
    return headers
    

def SaveTrashChannels(answer = '{"channels":""}',LastModified = 'Sun, 06 Nov 1994 00:00:00 GMT'):
    
    try:
        with open(TrashFile,'wb') as f:
            f.write(answer)
            print(str(TrashFile)+' saved.')
    except:
        print(str(TrashFile)+' SAVE ERROR.')
                
    try:
        with open(LastModifiedFile,'w') as f:
            f.write(LastModified)
            print(str(LastModifiedFile)+' saved.')
    except:
        print(str(LastModified)+' SAVE ERROR.')


def DownloadTrashChannels(forceUpdate=False):
    
    hdrs = GetHeaders(forceUpdate)
    req = urllib.request.Request(TrashUrl+TrashFile, headers = hdrs)
        
    try:
        connect = urllib.request.urlopen(req)
    except HTTPError as e:
        if e.code == 304:
            print('Not Modified. Document has not changed since given time.')
        else:
            print('The server couldn\'t fulfill the request. Error code: '+str(e.code))
    except URLError as e:
        print('FAILED to reach a server. Reason: '+str(e.reason))
    else:
        answer = connect.read()
        LastModified = connect.info().get('Last-Modified', False)
        connect.close()
        
        SaveTrashChannels(answer, LastModified)               
           
    

def GetTrashChannels():
    
    if not os.path.exists(TrashFile):
        print(str(TrashFile) + ' not found. Downloading new.')
        DownloadTrashChannels(forceUpdate=True)     
    
    try:
        with open(TrashFile, encoding='utf-8') as f:
            TrashChannels = json.load(f)
    except:
        print(str(TrashFile) + ' READ ERROR.')
        TrashChannels = json.loads('{"channels":""}')
                
                
    return TrashChannels

        

def CreateChannelBase():
    
    ChannelAttribute = []
    
    UpdateTrashChannels()
    with open(TrashFile, encoding='utf-8') as f:
        TrashChannelList = json.load(f)
    for TrashChannel in TrashChannelList['channels']:
        ChannelAttribute.append({'name':TrashChannel['name'],
                                 'TrashName':TrashChannel['name'],
                                 'TvgName':TrashChannel['name'],
                                 'Logo':TrashChannel['name']+'.png',
                                 'url':TrashChannel['url'],
                                 'group':TrashChannel['cat'],
                                 'visible':True,
                                 'Last Update':'',
                                 'remark':''})
    ChannelBaseArray = {'channels':ChannelAttribute}
    
    with open(ChannelBase,'w') as f:
        json.dump(ChannelBaseArray,f,ensure_ascii=False,indent=0)    



def GetChannelNameList(ChannelList):
    NameList = []
    for i in ChannelList:
        NameList.append(i['name'])
    return NameList

def SaveChannelBase(channels):
    with open(ChannelBase,'w') as f:
        json.dump(channels,f,ensure_ascii=False,indent=0)

def UpdateChannelBase(BaseChannels, TrashChannels):
    
    BaseChannelNameList = GetChannelNameList(BaseChannels)
    AddChannelCount = 0
    UpdatedChannels = 0
    
    for TrashChannel in TrashChannels:
        if TrashChannel['name'] not in BaseChannelNameList:
            BaseChannels.append({'name':TrashChannel['name'],
                                'TrashName':TrashChannel['name'],
                                'TvgName':TrashChannel['name'],
                                'Logo':TrashChannel['name']+'.png',
                                'url':'',
                                'group':TrashChannel['cat'],
                                'visible':True,
                                'Last Update':datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
                                'remark':''})    
            AddChannelCount+=1
            
    print('Trash: '+str(len(TrashChannels))+' Base: '+str(len(BaseChannels)))
    
    for BaseChannel in BaseChannels:
#        for TrashChannel in TrashChannels:
#            if BaseChannel['TrashName']==TrashChannel['name'] and BaseChannel['url']!=TrashChannel['url']:
#                BaseChannel['url'] = TrashChannel['url']
#                BaseChannel['Last Update'] = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
#                print(BaseChannel['TrashName'])
                UpdatedChannels+=1 

    
    print('Trash: '+str(len(TrashChannels))+' Base: '+str(len(BaseChannels)))
    print('Add: '+str(AddChannelCount))
    print('Updated: '+str(UpdatedChannels))
    
DownloadTrashChannels(forceUpdate=False)    
TrashChannels = GetTrashChannels()
for i in TrashChannels['channels']:
    print(i['name'])



