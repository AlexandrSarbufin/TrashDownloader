import os.path
from urllib.request import Request, urlopen
from urllib.error import  URLError, HTTPError
import json


TrashUrl = 'http://pomoyka.win/trash/ttv-list/'
TrashFile = 'ttv.json'
LastModifiedFile = 'last_modified.txt'
ChannelBase = 'Channel_base'


def GetLastModified():
    LastModified = 'Sun, 06 Nov 1994 00:00:00 GMT'
    if os.path.exists(LastModifiedFile):
        with open(LastModifiedFile, 'r') as f:
            LastModified = f.read()    
    return LastModified   

def GetTrashChannels(needUpdate,forceDowload=False):
    
    if not os.path.exists(TrashFile):
        with open(TrashFile,'w') as f: f.write('{"channels":["",""]}')
        print('TrashChannels not found. Downloading new')    
        return GetTrashChannels(True,True)
    else:     
        if needUpdate:
            req = Request(TrashUrl+TrashFile)
            
            if not forceDowload:
                req.add_header("If-Modified-Since", GetLastModified())
            else:
                print('Force download TrashChannels')
                
            try:
                connect = urlopen(req)
            except HTTPError as e:
                if e.code == 304:
                    print('Not Modified. Document has not changed since given time')
                else:
                    print('The server couldn\'t fulfill the request. Error code: '+str(e.code))
            except URLError as e:
                print('FAILED to reach a server. Reason: '+str(e.reason))
            else:
                with open(TrashFile,'wb') as f:
                    f.write(connect.read())
                    print('TrashChannels loaded')
                    
                with open(LastModifiedFile,'w') as f:
                    LastModified = connect.info().get('Last-Modified', False)
                    f.write(LastModified) 
                    print('New LastModified: '+LastModified+' saved')
                    
                connect.close()
                
        with open(TrashFile, encoding='utf-8') as f: TrashChannels = json.load(f)
                
                
        return TrashChannels['channels']

        

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



def GetChannelNameList(listCh):
    NameList = []
    for i in listCh['channels']:
        NameList.append(i['name'])
    return NameList

def SaveChannelBase(channels):
    with open(ChannelBase,'w') as f:
        json.dump(channels,f,ensure_ascii=False,indent=0)

def UpdateChannelBase():
    
    UpdateTrashChannels()
    c = 0
    
    with open(ChannelBase) as f:
        BaseChannelList = json.load(f)
        
    with open(TrashFile, encoding='utf-8') as f:
        TrashChannelList = json.load(f) 
              
    BaseChannelNameList = GetChannelNameList(BaseChannelList)
    dli = range(len(BaseChannelList['channels']))
    for TrashChannel in TrashChannelList['channels']:  
        if  TrashChannel['name'] not in BaseChannelList['channels'][dli]['name']:
            BaseChannelList['channels'].append({'name':TrashChannel['name'],
                                                'TrashName':TrashChannel['name'],
                                                'TvgName':TrashChannel['name'],
                                                'Logo':TrashChannel['name']+'.png',
                                                'url':TrashChannel['url'],
                                                'group':TrashChannel['cat'],
                                                'visible':True,
                                                'Last Update':'',
                                                'remark':''})
            c = c+1
            print('not in list '+TrashChannel['name'])
        
    SaveChannelBase(BaseChannelList)
    print('Add '+str(c)+' channels')   
    
    
#CreateChannelBase()

TrashChannels = GetTrashChannels(True)
for i in TrashChannels:
    print(i['name'])


