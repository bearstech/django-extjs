 
import utils

# width, dateFormat, renderer, hidden, align, type


class SimpleGrid(object):
    def to_grid(self, fields, rows, totalcount = None, json_add = "", sort_field = 'id', sort_direction = 'DESC'):
        if not totalcount: 
            totalcount = len(rows)
            #print 'totalcount', totalcount
        json =  """{
            "success":true
            %s
            ,"metaData":{
                "root":"rows",
                "totalProperty":"totalCount",
               "successProperty": "success",
                "sortInfo":{
                   "field": "%s",
                   "direction": "%s"
                },
                "fields":""" % (json_add, sort_field, sort_direction)
        json += utils.JSONserialise(fields)
        json += '}\n,"rows":\n'
        json += utils.JSONserialise(rows)
        json += '\n,"totalCount":%s' % totalcount
        json += "}\n"
        return json 


class VirtualField(object):
    def __init__(self, name):
        self.name = name
        
class ModelGrid(object):

    def __init__(self, model):
        self.model = model
        self.fields = []
        
        model_fields = self.model._meta._fields()
        
        excludes = getattr(self.Meta, 'exclude', [])
        # reorder cols if needed
        order = getattr(self.Meta, 'order', None)
        if order and len(order) > 0:
            base_fields  = []
            for field in order:
                added = False
                for f in model_fields:
                    if f.name == field:
                        added = True
                        base_fields.append(f)
                if not added:
                    base_fields.append(VirtualField(field))
        else:
            base_fields = model_fields
            
        
        for field in base_fields:
            if field.name in excludes:
                continue
            if field.__class__.__name__ == VirtualField:
                self.fields.append(self.Meta.fields_conf[field.name])
                continue
            #print field, dir(field)
            fdict = {'name':field.name, 'header': field.name}
            if field.name == 'id':
                fdict['id']='id'
            if  field.__class__.__name__ == 'DateTimeField':
                fdict['type'] = 'date'
                fdict['dateFormat'] = 'Y-m-d H:i:s'
            if  field.__class__.__name__ == 'DateField':
                fdict['type'] = 'date'
                fdict['dateFormat'] = 'Y-m-d'
            elif field.__class__.__name__ == 'IntegerField':
                fdict['type'] = 'int'
            elif field.__class__.__name__ == 'BooleanField':
                fdict['type'] = 'boolean'
            elif field.__class__.__name__ == 'DecimalField':
                fdict['type'] = 'float'
                fdict['renderer'] = 'function(v) {return (v.toFixed && v.toFixed(2) || 0);}'
            elif  field.__class__.__name__ == 'ForeignKey':
                pass
            if getattr(self.Meta, 'fields_conf', {}).has_key(field.name):
                fdict.update(self.Meta.fields_conf[field.name])
               # print fdict
            self.fields.append(fdict)
        #for field in self.model:
        #    print field
    
    def to_grid_extjs3(self, queryset, start = 0, limit = 0, totalcount = None, json_add = "", colModel = None):
        if not totalcount: 
            totalcount = queryset.count()      
        
        base_fields = self.fields
        if colModel and colModel.get('fields'):
            base_fields = []
            for f in colModel['fields']:    
               # print f, base_fields
                for cf in self.fields:
                   # print cf
                    if cf['name'] == f['name']:
                        #print 'found colModel for field %s' % f['name']
                        config_field = cf
                        if f.get('width'):
                            config_field['width'] = f.get('width')
                        if f.get('hidden'):                        
                            config_field['hidden'] = f.get('hidden')
                        base_fields.append(config_field)
        
        id_field = base_fields[0]['name']
        list_fields = ','.join(['"%s"' % f['name'] for f in base_fields])
        
        json =  """{
            "success":true
            %s
            ,"metaData":{
                "root":"rows",
                "totalProperty":"totalCount",
                "successProperty": "success",
                "idProperty":"%s",
                "fields":[%s],
               
             },\n""" % (json_add, id_field, list_fields)
        
        
        json += '"columns":%s,' % utils.JSONserialise(base_fields)
        
        #print 'queryset', queryset
        if queryset:
            if limit > 0:
                #print start, limit
                queryset = queryset[int(start):int(start) + int(limit)]
            json += """"rows":\n"""
            json += '['
            fields_items = []
            for item in queryset:
                #print 'item', item
                idx = 0
                field_items = []
                for field in base_fields:
                    val = getattr(item, field['name'], '')
                   # print field, val
                    if val:
                        if field.get('type', '') == 'date':
                            val = val.strftime(utils.DateFormatConverter(to_python = field['dateFormat'] ) )
                        #else:
                         #   val = utils.JsonCleanstr(val)
                    else:
                        if field.get('type', '') == 'float':
                            val = 0.0
                        elif field.get('type', '') == 'int':
                            val = 0
                        else:
                            val = ''
                    astr = utils.JSONserialise_dict_item(field['name'], val)
                    field_items.append(astr)
                    idx += 1
                fields_items.append('{%s}' % ','.join(field_items))
            json += ','.join(fields_items)
            json += ']\n'
        else:
            json += '"rows":[]'
        json += """\n,"totalCount":%s""" % totalcount
        json += "}\n"
        return json 
    def to_grid(self, queryset, start = 0, limit = 0, totalcount = None, json_add = "", colModel = None, sort_field = 'id', sort_direction = 'DESC'):
        return self.to_grid_extjs2(queryset, start = start, limit =limit, totalcount = totalcount, json_add =json_add, colModel = colModel, sort_field = sort_field, sort_direction = sort_direction)
    def to_grid_extjs2(self, queryset, start = 0, limit = 0, totalcount = None, json_add = "", colModel = None, sort_field = 'id', sort_direction = 'DESC'):
        if not totalcount: 
            totalcount = queryset.count()
            #print 'totalcount', totalcount
        json =  """{
            "success":true
            %s
            ,"metaData":{
                "root":"rows",
                "totalProperty":"totalCount",
               "successProperty": "success",
                "sortInfo":{
                   "field": "%s",
                   "direction": "%s"
                },
                "fields":""" % (json_add, sort_field, sort_direction)
        
        base_fields = self.fields
        if colModel and colModel.get('fields'):
            base_fields = []
            for f in colModel['fields']:    
               # print f
                for cf in self.fields:
                    if cf['name'] == f['name']:
                        config_field = cf
                        if f.get('width'):
                            config_field['width'] = f.get('width')
                        # force hidden=False if field present in given colModel
                        if f.get('hidden') == True:                        
                            config_field['hidden'] = True
                        else:
                            config_field['hidden'] = False
                        base_fields.append(config_field)
        json +=  utils.JSONserialise(base_fields)
        json += "},\n"
        #print 'queryset', queryset
        if queryset:
            if limit > 0:
                #print start, limit
                queryset = queryset[int(start):int(start) + int(limit)]
            json += """"rows":\n"""
            json += '['
            fields_items = []
            for item in queryset:
                #print 'item', item
                idx = 0
                field_items = []
                for field in base_fields:
                    val = getattr(item, field['name'], '')
                   # print field, val
                    if val:
                        if field.get('type', '') == 'date':
                            val = val.strftime(utils.DateFormatConverter(to_python = field['dateFormat'] ) )
                        else:
                            val = utils.JsonCleanstr(val)
                    else:
                        if field.get('type', '') == 'float':
                            val = 0.0
                        elif field.get('type', '') == 'int':
                            val = 0
                        else:
                            val = ''
                    astr = utils.JSONserialise_dict_item(field['name'], val)
                    field_items.append(astr)
                    idx += 1
                fields_items.append('{%s}' % ','.join(field_items))
            json += ','.join(fields_items)
            json += ']\n'
        else:
            json += '"rows":[]'
        json += """\n,"totalCount":%s""" % totalcount
        json += "}\n"
        return json 
    class Meta:
        pass

