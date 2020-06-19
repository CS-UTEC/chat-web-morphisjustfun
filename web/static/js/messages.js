function getMessagesDevEx(){
    var url = "/messages";
    var url_users = "/users";
    $("#grid").dxDataGrid({
        dataSource: DevExpress.data.AspNet.createStore({
            key: "id",
            insertUrl: url,
            updateUrl: url,
            deleteUrl: url,
            loadUrl: url,
            onBeforeSend: function(method, ajaxOptions) {
                ajaxOptions.xhrFields = { withCredentials: true };
            }
        }),

        editing: {
            allowUpdating: true,    
            allowDeleting: true,
            allowAdding: true
        },
        
        paging: {
            pageSize: 12
        },

        pager: {
            showPageSizeSelector: true,
            allowedPageSizes: [8, 12, 20]
        },
        columns: [{
            dataField: "id",
            dataType: "number",
            allowEditing: false
        }, {
            dataField: "content"
        }, {
            dataField: "sent_on",
            dataType: "date",
            format: "MM/dd/yyy hh:mm"
        }, {
            dataField: "user_from_id",
            lookup:{
                    dataSource: DevExpress.data.AspNet.createStore({
                    key: "id",      
                    loadUrl: url_users,
                    onBeforeSend: function(method, ajaxOptions){
                        ajaxOptions.xhrFields = {withCredentials:true};
                    }
                }),
                valueExpr: "id",
                displayExpr: "username"
            }
        }, {
            dataField: "user_to_id",
            lookup:{
                    dataSource: DevExpress.data.AspNet.createStore({
                    key: "id",      
                    loadUrl: url_users,
                    onBeforeSend: function(method, ajaxOptions){
                        ajaxOptions.xhrFields = {withCredentials:true};
                    }
                }),
                valueExpr: "id",
                displayExpr: "username"
            }
        }],

    }).dxDataGrid("instance");
}