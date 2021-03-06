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
    
    LastModified = 'Sun, 06 Nov 1994 00:00:00 GMT'
    
    if os.path.exists(LastModifiedFile):
        try:
            with open(LastModifiedFile, 'r') as f:
                LastModified = f.read()
        except:
            print(str(LastModifiedFile) + ' READ ERROR.')
            
    return LastModified
    


def DownloadTrashChannels(forceUpdate=False):
    
###############################################################################

    print('Trying to download Trash channels list. Force update: '+str(forceUpdate))
    
    TrashChannels = '{"channels":""}'
    LastModified = GetLastModified()
    
############################################################################### 

    req = urllib.request.Request(TrashUrl+TrashFile)
    
    req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')    
    if not forceUpdate:
        req.add_header('If-Modified-Since', LastModified)        
        
    try:
        connect = urllib.request.urlopen(req)
    except HTTPError as e:
        if e.code == 304:
            print('Not Modified. Document has not changed since given time. \nLast-Modified: '+LastModified)
        else:
            print('The server couldn\'t fulfill the request. Error code: '+str(e.code))
    except URLError as e:
        print('FAILED to reach a server. Reason: '+str(e.reason))
    else:        
        TrashChannels = connect.read()
        LastModified = connect.info().get('Last-Modified', False)
        connect.close()
        print('Trash channels list loaded. Last-Modified: '+LastModified)   
             
###############################################################################
        
        try:
            with open(TrashFile,'wb') as f:
                f.write(TrashChannels)
                print(str(TrashFile)+' saved.')
        except:
            print(str(TrashFile)+' SAVE ERROR.')
                    
        try:
            with open(LastModifiedFile,'w') as f:
                f.write(LastModified)
                print(str(LastModifiedFile)+' saved.')
        except:
            print(str(LastModifiedFile)+' SAVE ERROR.')               
              


def GetTrashChannels():
    
###############################################################################    
    
    if not os.path.exists(TrashFile):
        print(str(TrashFile) + ' not found.')
        DownloadTrashChannels(forceUpdate=True)
    else:
        DownloadTrashChannels(forceUpdate=False)
        
###############################################################################        
    
    try:
        with open(TrashFile, encoding='utf-8') as f:
            TrashChannels = json.load(f)
    except:
        print(str(TrashFile) + ' READ ERROR.')
        TrashChannels = json.loads('{"channels":""}')      
                
    return TrashChannels



def GetChannelNameList(ChannelList):
    NameList = []
    for i in ChannelList:
        NameList.append(i['name'])
    return NameList



def SaveChannelBase(channels):
    with open(ChannelBase,mode='w') as f:   
        json.dump(channels,f,ensure_ascii=False,indent=0)



def UpdateChannelBase(BaseChannels, TrashChannels):
       
###############################################################################       
    
    BaseChannels['LastUpdate'] = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
 
###############################################################################
                                                                 
    NewChannelsCount = 0
    UpdatedChannelsCount = 0
    DeletedChannelsCount = 0    
    BaseChannelNameList = GetChannelNameList(BaseChannels['channels'])
    
############################################################################### 
    
    for TrashChannel in TrashChannels['channels']:
        if TrashChannel['name'] not in BaseChannelNameList:
            BaseChannels['channels'].append({'name':TrashChannel['name'],
                                             'TrashName':TrashChannel['name'],
                                             'TvgName':TrashChannel['name'],
                                             'Logo':TrashChannel['name']+'.png',
                                             'url':'',
                                             'group':TrashChannel['cat'],
                                             'visible':True,
                                             'Last Update':datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
                                             'remark': ''})    
            NewChannelsCount+=1
    print('Add ' + str(NewChannelsCount) + ' channels')
            
###############################################################################
            
    for BaseChannel in BaseChannels['channels']:
        DeleteChannel = True
        for TrashChannel in TrashChannels['channels']:
            if BaseChannel['TrashName']==TrashChannel['name']:
                DeleteChannel = False
                if BaseChannel['url']!=TrashChannel['url']:
                    BaseChannel['url'] = TrashChannel['url']
                    BaseChannel['Last Update'] = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")  
                    print(TrashChannel['name'])              
                    UpdatedChannelsCount+=1
        if DeleteChannel:
            BaseChannel['visible'] = False
            DeletedChannelsCount+=1

    print('Update '+str(UpdatedChannelsCount) + ' channels')
    print(str(DeletedChannelsCount) + ' channels not in Trash channels list')
    SaveChannelBase(BaseChannels)
    
###############################################################################  
  
  
  
TrashChannels = GetTrashChannels()
ChannelsBase = {'LastUpdate' : [],'channels' : []}

with open(ChannelBase) as f:
    ChannelsBase = json.load(f)

UpdateChannelBase(ChannelsBase, TrashChannels)



