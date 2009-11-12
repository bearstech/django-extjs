// dynamic load of a server side form
         Ext.ux.DjangoForm = Ext.extend(Ext.FormPanel, {
                 url:null
                ,baseParamsLoad:null
                ,callback:null
                ,initComponent:function() {
                    this.gotFormCallback = function(response, options) {
                         var res = Ext.decode(response.responseText);
                         console.log(res);
                         //delete this.baseParams
                         Ext.apply(this, res);
                        console.log(this);
                         Ext.ux.DjangoForm.superclass.initComponent.apply(this, arguments);
                         this.callback(this);
                     }
                     var o = {output:'json'}
                     if (this.baseParamsLoad) Ext.apply(o, this.baseParamsLoad);
                     Ext.Ajax.request({
                        url:this.url
                        ,params:o
                        ,method:'GET'
                        ,scope:this
                        ,success:this.gotFormCallback
                        ,failure:this.gotFormCallback
                    });
                }             
             });
             
             
        Ext.ux.DjangoField = function(config) {
             var tgt = config.django_form.findBy(function(comp, form) {
                          return (comp.name && (comp.name == config.name));
                        });
             var bConfig = {};
             if (tgt.length > 0) {
                    bConfig = tgt[0].cloneConfig();
                    }
             Ext.apply(bConfig, config);

             return bConfig;
        }
        
        Ext.ux.DjangoHiddenFields = function(config) {
            var tgt = config.django_form.findBy(function(comp, form) {
                          return (comp.xtype == 'hidden');
                        });
            if (tgt.length==0) tgt = [{html:'empty'}];
            console.log(tgt);
            return new Ext.Panel({
                hidden:true
                ,items:tgt
                });
        }
        
 
        
        Ext.reg("DjangoField", Ext.ux.DjangoField);
        
        Ext.reg("DjangoHiddenFields", Ext.ux.DjangoHiddenFields);
        
 
        function ExtJsForm_incompleteForm() {
            console.log('formulaire invalide!')
             Ext.Msg.show({
                       title:'Erreur',
                       msg: 'Impossible de valider : formulaire invalide',
                       buttons: Ext.Msg.OK,               
                       icon: Ext.MessageBox.WARNING 
                    });
        }
        // this functions handles the generic form submission
        function ExtJsForm_validResponse(form, action) {
               if (action.result.success) {
                    Ext.Msg.show({
                       title:'Succes',
                       msg: 'Formulaire bien enregistre',
                       buttons: Ext.Msg.OK,               
                       icon: Ext.MessageBox.INFO 
                    });
               }
               else {
                    Ext.Msg.show({
                       title:'Erreur',
                       msg: 'Impossible de valider : <br>' + action.result.msg + '<br>',
                       buttons: Ext.Msg.OK,               
                       icon: Ext.MessageBox.WARNING 
                    });
               }
        }