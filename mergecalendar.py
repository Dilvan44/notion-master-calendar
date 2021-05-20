from decouple import config
import requests
import json

apitoken = config('NOTIONAPITOKEN')
baseCalId1=config('BASECALENDAR1')
baseCalId2=config('BASECALENDAR2')
MasterCalId=config('MASTERCALENDAR')
requestheader = {
    'Authorization':f'Bearer {apitoken}',
    'Notion-Version':'2021-05-13'
    } 
basecals = [baseCalId1,baseCalId2]
mastercal = MasterCalId

def getCalendardata(calendarid):
    #Request to API to retrieve DB, return a list with New Pages & Pages which are already in the synced Database/Calendar
    
    newpagesfilter = {
        'filter':
            {
            'property':'addedtosync',
            'checkbox':{
                'equals':False
                }
            }
        }
    oldpagesfilter = {
        'filter':
            {
            'property':'addedtosync',
            'checkbox':{
                'equals':True
                }
            }
        }
    newpages = requests.post(
        f'https://api.notion.com/v1/databases/{calendarid}/query',
        headers = requestheader,
        json=newpagesfilter
        ).json()
    oldpages = requests.post(
        f'https://api.notion.com/v1/databases/{calendarid}/query',
        headers = requestheader,
        json=oldpagesfilter
        ).json()

    calendardata = [newpages,oldpages]
    return calendardata

def pushData(calendardata,calendarid):
    #Create new pages in the master database with the following properties: original database title ,title, Date, link to orig. page, 
    #if the property "addedtosync" is false, change it to True
    errorlist = []
    
    for page in calendardata['results']:
        #prepare fetched data to create new page
        page_parent = calendarid
        pageid_FK = page['id']
        
        #if accidently there is an empty item continue with next item
        try:
            name = page['properties']['Name']['title'][0]['text']['content']
        except: 
            continue

        if page['properties']['Date']['date']['end'] == None: #if there is no end date
            datedata = page['properties']['Date']
            datedata = {'date':{'start':datedata['date']['start'],'end':None}}
        else:
            datedata = page['properties']['Date']
            datedata = {'date':{'start':datedata['date']['start'],'end':datedata['date']['end']}}

        linktopage = "https://notion.so/" + page['id'].replace("-","")

        #Try creating new page. If it fails, print the error
        try: 
            pushrequest = requests.post(
                f'https://api.notion.com/v1/pages', 
                headers= requestheader, 
                json={
                    'parent':{'database_id':page_parent},
                    'properties':{
                        'Name':{'title':[{'type': 'text','text':{'content':name}}]},
                        'Pageid_FK':{'rich_text':[{'text':{'content':pageid_FK},"plain_text": "pageid_FK"}]},
                        'Date':datedata,
                        'link_original':{'url':linktopage}

                    }

                }
            )
            
        except: 
            errorstring = str(pushrequest.status_code) + "" + str(pushrequest.json())
            print(errorstring)
        

        

        #set addedtosync on original Page 
        if pushrequest.status_code == 200:
            requests.patch(
                f'https://api.notion.com/v1/pages/{pageid_FK}',
                headers=requestheader,
                json={
                    'properties':{
                        'addedtosync':True
                    }
                }
            )
            print(f"Page {name} was added to the mastercalendar")
            
        else: 
            print(f"Page {name} was not added to the mastercalendar")
            errorlist.append(pageid_FK)
        
    #errorhandling
    if not errorlist:
        #if there are no errors
        return True
    else:
        #if there errors
        return False

def getrelatedMasterPage(originalpageid, mastercalendarid):
    #Search the related page id in the master calendar in order to sync it correctly
    pageidfilter = {
        'filter':
            {
            'property':'Pageid_FK',
            'text':{
                'equals':originalpageid
                }
            }
        }
    query = requests.post(
        f'https://api.notion.com/v1/databases/{mastercalendarid}/query',
        headers=requestheader,
        json=pageidfilter
    ).json()
    masterpageid = query['results'][0]['id']
    return masterpageid

def syncData(calendardata):
    # Patch the already added pages
    errorlist =[]
    for page in calendardata['results']:
        pageid_FK = page['id']
        name = page['properties']['Name']['title'][0]['text']['content']

        if page['properties']['Date']['date']['end'] == None: #if there is no end date
            datedata = page['properties']['Date']
            datedata = {'date':{'start':datedata['date']['start'],'end':None}}
        else:
            datedata = page['properties']['Date']
            datedata = {'date':{'start':datedata['date']['start'],'end':datedata['date']['end']}}

        relatedmasterpageid = getrelatedMasterPage(pageid_FK,mastercal)

        
        patchreq = requests.patch(
            f'https://api.notion.com/v1/pages/{relatedmasterpageid}',
            headers=requestheader,
            json={
                'properties':{
                    'Name':{'title':[{'type': 'text','text':{'content':name}}]},
                    'Pageid_FK':{'rich_text':[{'text':{'content':pageid_FK},"plain_text": "pageid_FK"}]},
                    'Date':datedata,
                }
            }
        )
        if patchreq.status_code == 200:
            print(f'Page {name} was synced')
        else:
            print(f'Page {name} was not synced')
            errorlist.append(relatedmasterpageid)

    if not errorlist:
        return True
    else:
        return False

def main():
    #Get all Pages in original dbs for Dates > 1 month earlier 
    #filter not pushed data and push it 
    #already pushed data gets updated
    
    for calendarid in basecals:
        Calendardata = getCalendardata(calendarid) #returns a list. First item: new pages; Second Item: Pages which should be synchronized
        pushData(Calendardata[0],mastercal) 
        syncData(Calendardata[1])
    return None

if __name__ == "__main__":
    main()

