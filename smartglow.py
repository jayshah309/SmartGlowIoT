if __name__ == '__main__' :
    
    import httplib
    import time
    import json
    from urlparse import urlparse
    import base64
    
    httpServer = 'http://smartobjectservice.com:8080'
    httpDomain = 'domain'
    resourcePathBase = '/' + httpDomain + '/endpoints'
    subscribeURI = '/3300/1/5700'
    actuateURI = '/11100/0/5900'
    baseURL = httpServer + resourcePathBase
    
    username = 'admin'
    password = 'secret'
    auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    ep_names = []
    def discoverEndpoints(basePath):
        uriObject = urlparse(basePath)
        print 'discoverEP : ' + basePath
        httpConnection = httplib.HTTPConnection(uriObject.netloc)
        httpConnection.request('GET', uriObject.path, headers= \
                           {"Accept" : "application/json", "Authorization": ("Basic %s" % auth) })
        response = httpConnection.getresponse()
        print response.status, response.reason
        if response.status == 200:
            endpoints = json.loads(response.read())
        httpConnection.close()
        
        for endpoint in endpoints:
            if endpoint['type'] == 'DEMO' and discoverResources(endpoint['name'], subscribeURI):
                ep_names.append(endpoint['name'])
                print 'endpoint: ' + endpoint['name']
        return ep_names

    def discoverResources(endpoint, uri_path):
        resources = []
        uriObject = urlparse(baseURL + '/' + endpoint)
        print 'discoverRES : ' + endpoint

        httpConnection = httplib.HTTPConnection(uriObject.netloc)
        httpConnection.request('GET', uriObject.path, headers= \
                           {"Accept" : "application/json", "Authorization": ("Basic %s" % auth) })
        response = httpConnection.getresponse()
        print response.status, response.reason
        if response.status == 200:
            resources = json.loads(response.read())
        httpConnection.close()
        
        
        for resource in resources:
            if resource['uri'] == uri_path:
                print 'resource: ' + resource['uri']
                return resource['uri']
            else:
                return 0
        
    def sound(eep, soundURI):
        resources = []
        print 'soundendpoint : ' +eep
        path = baseURL + '/' + eep + soundURI+'?sync=true'
        print 'path : ' +path
        uriObject = urlparse(path)
        httpConnection = httplib.HTTPConnection(uriObject.netloc)
        httpConnection.request('GET', path, headers= 
                           {"Content-Type" : "text/plain", "Accept" : "*/*", "Authorization": ("Basic %s" % auth) })
        response = httpConnection.getresponse()
        value = response.read()
        print 'sound value :'+value
        print value
        if value > 10:
            print 'I just heard some sound'
            actuateLEDbar('10000000')
        return response.read()

    def light(eep, lightURI):
        resources = []
        print 'lightendpoint : ' +eep
        path = baseURL + '/' + eep + lightURI+'?sync=true'
        print 'path : ' +path
        uriObject = urlparse(path)
        httpConnection = httplib.HTTPConnection(uriObject.netloc)
        httpConnection.request('GET', path, headers= 
                           {"Content-Type" : "text/plain", "Accept" : "*/*", "Authorization": ("Basic %s" % auth) })
        response = httpConnection.getresponse()
        value = response.read()
        print 'light value : '+value
        if int(value) == 0:
            presence('mbedDEMO-0A900009071E', '/3302/0/5500')
            sound('mbedDEMO-0A900009071E','/3300/0/5700')            
        else:
            actuateLEDbar('00000000')

    def presence(eep, presenceURI):
        resources = []
        print 'presenceendpoint : ' +eep
        path = baseURL + '/' + eep + presenceURI+'?sync=true'
        print 'path : ' +path
        uriObject = urlparse(path)
        httpConnection = httplib.HTTPConnection(uriObject.netloc)
        httpConnection.request('GET', path, headers= 
                           {"Content-Type" : "text/plain", "Accept" : "*/*", "Authorization": ("Basic %s" % auth) })
        response = httpConnection.getresponse()
        value = response.read()
        print 'presence value :'+value
        print value
        if value > 0:
            print 'I saw an object moving'
            actuateLEDbar('10000000')
        return response.read()

   

    def handleNotifications(events):
        if 'notifications' in events:
            for notification in events['notifications']:
                if (notification['ep'] in ep_names) and (notification['path'] == subscribeURI):
                    process_payload(notification)
                
    def process_payload(notification):
        value =  base64.b64decode(notification['payload']) #notification payloads are base64 encoded
        print "value: ", value
        if value > 1:
            actuateLEDbar('10000000')
        else:
            actuateLEDbar('00000000')


            
        
    def actuateLEDbar(ledString = '00000000'):
        print 'actuateLEDbar'
        path = baseURL + '/' + 'mbedDEMO-0A900009071E' + actuateURI
        print "actuating: " + path + ", value=" + ledString
        uriObject = urlparse(path)
        httpConnection = httplib.HTTPConnection(uriObject.netloc)
        httpConnection.request('PUT',   uriObject.path + '?' + uriObject.query, ledString, \
                               {"Content-Type" : "application/json", "Authorization": ("Basic %s" % auth)})
        response = httpConnection.getresponse()
        print response.status, response.reason
        httpConnection.close()

    def start():
        for x in range(5):
            time.sleep(10)
            light('mbedDEMO-0A900009071E','/3300/1/5700')
            
               
                
    """
    Start
    """
    print "Started"

    discoverEndpoints(baseURL)
    start()
    
