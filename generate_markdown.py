import json
from collections import OrderedDict
import sys

def generate_markdown(input_filename):
    spec=json.loads(open(input_filename,'r').read(),object_pairs_hook=OrderedDict)
    print '# Kasisto Enterprise API Overview'
    print 'Version 1.2'
    print ''
    print '- [Authentication](#authentication)'
    print '- [Authorization](#authorization)'
    print '- [Schema](#schema)'
    for tag in spec['tags']:
        tagname=tag['name']
        print '- ['+tagname +' Methods](#'+tagname.lower().replace(' ','-')+'-methods)'
        for path,path_obj in spec['paths'].iteritems():
            for method,method_obj in path_obj.iteritems():
                if tagname in method_obj['tags']:
                    print '  * ['+path+'](#'+method_obj['x-name'].lower().replace(' ','-')+')'

    print ''
    print ''
    print '## Authentication'
    print 'The Kasisto API requires all requests to include a secret key header value used for request authentication.  Kasisto will include the secret key header in each request from our servers. API implementations must validate the secret is correct.'
    print 'Server implementations should return a 401 HTTP status code response if authentication fails.'
    print ''
    print '## Authorization'
    print 'The Kasisto API allows requests to include a user authorization token header value.  This token should be validated on the server implementation to match the provided user_id value and that is has the neccessary privilages to access the requested information.'
    print 'Server implementations should return a 403 HTTP status code response if authorization fails.'
    print ''
    print '## Schema'
    print 'All API access must be over HTTPS.  All data is sent and received as JSON.'
    print 'Schema definitions are described [here](#schema-definitions).'
    print ''

    for tag in spec['tags']:
        tagname=tag['name']
        print '### '+tagname +' Methods'
        print ''
        for path,path_obj in spec['paths'].iteritems():
            for method,method_obj in path_obj.iteritems():
                if tagname in method_obj['tags']:
                    print '#### '+method_obj['x-name']
                    print ''
                    print '```'
                    print method.upper()+" "+path
                    print '```'
                    print ''
                    print method_obj['description']
                    print ''
                    print '##### Request Parameters'
                    print ''
                    #print '| Parameter | Location | Required | Description |'
                    #print '| ------ | ----------- | -------- | ----------- |'
                    print '| Parameter | Location |'
                    print '| --------- | -------- |'
                    for param in method_obj['parameters']:
                        if param['in']=='body':
                            print '| ['+param['name']+'](#'+param['name']+') | '+param['in'] +' |'# +str(param.get('required',False))+' | ' + param.get('description','')+' |'
                        else:
                            print '| '+param['name']+' | '+param['in']+' |' #+str(param.get('required',False))+' | ' + param.get('description','')+' |'
                    print ''
                    print '##### Responses'
                    print ''
                    print '| Status | Description | Schema |'
                    print '| ------ | ----------- | ------ |'
                    for status in sorted(method_obj['responses'].keys()):
                        status_obj=method_obj['responses'][status]
                        print '| '+status +" | "+ status_obj['description']+' | '+ generate_ref_link(status_obj.get('schema'))+' |'
                    print ''
                    print '##### Sample Request / Response'
                    print ''
                    print '```http'
                    print method.upper()+" "+path+" HTTP/1.1"
                    print 'Content-Type: application/json'
                    print 'Accept: application/json'
                    for param in method_obj['parameters']:
                        if param['in']=='header':
                            if param['name']=='Date':
                                print 'Date: "Tue, 01 Jan 2017 00:00:00 GMT"'
                            else:
                                print param['name']+': string'
                    print '```'
                    print '```json'
                    for param in method_obj['parameters']:
                        if param['in']=='body':
                            print de_ref(spec,param.get('schema'))
                    print '```'
                    print ''
                    print '```http'
                    print 'HTTP/1.1 200 OK'
                    print 'Content-Type: application/json'
                    print 'token: string (optional)'
                    print '```'
                    print '```json'
                    for status in sorted(method_obj['responses'].keys()):
                        if status=='200':
                            status_obj=method_obj['responses'][status]
                            print de_ref(spec,status_obj.get('schema'))
                     
                    print '```'
                    print ''
        print ''

    print '### Schema Definitions'
    print ''
    for name in sorted(spec['definitions'].keys()):
        def_obj=spec['definitions'][name]
        print '#### '+name
        print ''
        print '```json'
        print json.dumps(generate_schema(spec,def_obj),indent=4)
        print '```'
        print ''

def de_ref(spec,obj,dumps=True):
    if obj is not None:
        if '$ref' in obj:
            ref=obj['$ref'].replace('#/definitions/','')
            ref_obj=spec['definitions'].get(ref)
            if ref_obj is not None:
                if dumps:
                    return json.dumps(generate_schema(spec,ref_obj),indent=4)
                else:
                    return generate_schema(spec,ref_obj)
        
        if 'type' in obj:
            if obj.get('type')=='array':
                if dumps:
                    return '['+de_ref(spec,obj.get('items'),dumps)+']'
                else:
                    return [de_ref(spec,obj.get('items'),dumps)]
            if obj.get('type')=='object':
                if dumps:
                    return "{}"
                else:
                    return {}
            if obj.get('type')=='array':
                if dumps:
                    return "[]"
                else:
                    return []
    return ''

def generate_ref_link(obj):
    if obj is not None:
        if '$ref' in obj:
            ref=obj['$ref'].replace('#/definitions/','')
            return '['+ref+'](#'+ref.lower().replace(' ','-')+')'
        else:
            if obj.get('type')=='array':
                return 'Array of '+generate_ref_link(obj.get('items'))
    return ''

def generate_schema(spec,def_obj):
    obj=OrderedDict()
    if not 'properties' in def_obj:
        return obj
    for name,prop in def_obj['properties'].iteritems():
        required=prop.get('required',False)
        if name=='meta':
            obj['meta']=[{'name':'string','value':'string'}]
        else:
            if prop.get('type')=='number' or prop.get('type')=='integer':
                if prop.get('format')=='float':
                    obj[name]=0.0
                else:
                    obj[name]=0
            else:
                if prop.get('format')=='date':
                    obj[name]='2016-01-30'
                else:
                    if prop.get('format')=='date-time':
                        obj[name]='2016-01-30T00:00:00.000+0000'
                    else:
                        if prop.get('type')=='object':
                            obj[name]=de_ref(spec,prop,dumps=False) 
                        else:
                            if prop.get('type')=='array':
                                p=prop.get('items')
                                if 'type' in p and p['type']=='string':
                                    obj[name]=['string']
                                else:
                                    obj[name]=de_ref(spec,prop,dumps=False)
                            else:
                                if prop.get('type')=='boolean':
                                    obj[name]=True
                                else:
                                    if 'enum' in prop:
                                        obj[name]=prop['enum']
                                    else:
                                        obj[name]='string'
    return obj

if __name__=='__main__':
    if len(sys.argv)==2:
        generate_markdown(sys.argv[1])
    else:
        generate_markdown('kasisto-swagger.json')
