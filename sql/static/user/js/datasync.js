$('#btnSync').click(function(){
	syncUser();
});

function syncUser() {
    $.ajax({
        type: "post",
        url: "/syncldapuser/",
        dataType: "json",
        data: {},
        complete: function () {
        },
        success: function (data) {
			$('#wrongpwd-modal-body').html(data.msg);
			$('#wrongpwd-modal').modal({
				keyboard: true
			});
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			alert(errorThrown);
        }
    });
};

function show_sync_data() {
    $('#data_sync_table').on('click','[data-role="sync_dict_btn"]',function(){
        $.post(
            "/syncoradict/",
            function (data) {
                var list = data.listCluster;
                var tableHTML = '';
                list.forEach(item => {
                    tableHTML += '<p><input type="checkbox" name="datasync" value="'+item+'" class="checkbox-input">'+item+'</p>';
                });
                $('#table_select').html(tableHTML);
            },
        );
    });
    $('#sync_dict_submit').on('click',function() {
        var syncArr = [];
        var checkboxs = $('#sync_dict_modal').find('input[name="datasync"]:checked');
        checkboxs.each(function(item) {
            var item = $(this);
            syncArr.push(item.val());
        })
        $.post('/syncoradict/',{cluster_list_sync :JSON.stringify(syncArr)},function(data) {
            // fail => has data.msg
            if(data.status == 'error') {
                alert(data.msg);
            } else {
                // success
                window.location.reload();
            }
        })
    })
}
function selectedOpt() {
    var $table_select = $('#table_select');
    $('#select_group').on('click','input[type="radio"]',function() {
        var _this = $(this);
        changeSelectStatus($table_select,_this.attr('data-select'));
    })
}
function changeSelectStatus(dom,status) {
    dom.find('input[type="checkbox"]').each(function() {
        var item = $(this);
        var check = status === 'opps' ? !item.prop('checked') : status;
        item.prop('checked',check);
    })
}
show_sync_data();
selectedOpt();
