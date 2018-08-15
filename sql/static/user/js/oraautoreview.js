function validate() {
	var result = true;
	var sqlContent = $("#sql_content").val();
	var clusterName = $("#cluster_name").val();
	if (sqlContent === null || sqlContent.trim() === "" || sqlContent == $("#sql_content").attr("placeholder")) {
		alert("SQL内容不能为空！");
		return result = false;
	} else if (clusterName === null || clusterName.trim() === "" || clusterName == $("#cluster_name").attr("data-placeholder")) {
		alert("请选择要！");
		return result = false;
	}
	return result;
}


$("#btn-oraautoreview").click(function(){
	//先做表单验证，成功了提交ajax给后端
	// if (validate()) {
		oraautoreview();
	// }
});

function oraautoreview() {
	var sqlContent = $("#sql_content");
	var clusterName = $("#cluster_name");
	
	var $check = $('#cluster_name_checkbox').find('input[type="checkbox"]:checked');
	var checkedArr = [];
	$check.each(function() {
		var item = $(this);
		checkedArr.push(item.val());
	})
	clusterName.val(checkedArr.join());
	if(sqlContent.val()==='' || clusterName.val()==="") {
		alert("SQL内容/上线的集群不能为空！");
	}else {
		//将数据通过ajax提交给后端进行检查
		
		$("#btn-oraautoreview").prop('disabled',true);
	
		$.ajax({
			type: "post",
			url: "/orasimplecheck/",
			dataType: "json",
			data: {
				sql_content: sqlContent.val(),
				cluster_name: clusterName.val()
			},
			complete: function() {
				$("#btn-oraautoreview").prop('disabled',false);
			},
			success: function (data) {
				if (data.status == 0) {
					//console.log(data.data);
					var result = data.data;
					var finalHtml = "";
					for (var i=0; i<result.length; i++) {
						//索引5是SQL，4是审核建议
						var sql = result[i][5].replace(/\n/g,'<br>');
						var suggest = result[i][4].replace(/\n/g,'<br>');
						alertStyle = "alert-success";
						if (result[i][4] != "None") {
							alertStyle = "alert-danger";
						}
						finalHtml += "<div class='alert alert-dismissable " + alertStyle + "'> <button type='button' class='close' data-dismiss='alert' aria-hidden='true'>x</button> <table class='' width='100%' style='table-layout:fixed;'> <tr> <td width='80%' style='word-wrap:break-word;'>" + sql + "</td> <td><strong>自动审核结果：</strong>" + suggest + "</td> </tr> </table> </div>";
					}
					$("#inception-result-col").html(finalHtml);
					// 填充内容后展现出来
					$("#inception-result").show();
				} else {
					alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
				}
			},
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				alert(errorThrown);
			}
		});	
	}
	

}

function renderClusterResult() {
	$('#btn_search_cluster').on('click',function() {
		var selected = $('#cluster_name_select').next().find('.filter-option').html();
		// var content = window.cluster[selected];
		var _this = $(this);
		_this.prop('disabled',true)
		$.getJSON('/oradict/',{cluster_name:selected},function(data) {
			var content = data.listSchema;
			var contentHTML ='';
			content.forEach(item => {
				contentHTML += '<li class="cluster-group-item">'+item+'</li>'			
			});
			$('#cluster_result_content').html('<ul class="cluster-list-group" style="margin-top:20px;">'+ contentHTML +'</ul>')
		}).always(function() {
			_this.prop('disabled',false)
		})
		
	})
}

function execute(e,t){
	var _this = $(t);
    var result = confirm('当前状态是'+ $('#workflowDetail_status').html() +',确认继续吗?');  
    if(result){
        _this.parent('form').submit();
    }
    // //点击执行之后，刷新当前页面，以显示执行进度
    // setTimeout(function(){
    //     window.location.reload(true);
    // },2500)
}

function pagination() {
	var pageHTML = '';
	var pagesNum = parseInt(window.pages);
	var pageNoNum = parseInt(window.pageNo);
	var activeClass;
	for(var i = 0; i < pagesNum; i++) {
		activeClass = pageNoNum === i ? 'active' :'';
		pageHTML += '<li class="' + activeClass + '"><a href="?pageNo=' + i + '" data-href="'+i+'">' + (i + 1) + '</a></li>'
	}
	$('#last_page').after(pageHTML)
}
function fillSqlContent() {
	// replaceLineFeed('modal_sql_content','sql_content_container')
	// replaceLineFeed('modal_manual_submit','modal_manual_submit')
}

// function replaceLineFeed(id,templete) {
// 	$('#'+id).length && $('#'+id).html($('#'+templete).html().replace(/\n/g,'<br>'))
	
// }
function confirmManual() {
	$('#confirm_manual').on('click',function() {
		$.post('/manexec/',{workflowid:$('#workflowid').val()},
		function(data) {
			if(parseInt(data.status) === 2) {
				alert(data.msg);
				window.location.reload();
			}else {
				alert(data.msg);
			}
		})
	})
}

function submitManualConfirm(){
	$('#confirm_manual_submit').on('click',function() {
		$.post('/manfinish/',{
			status:$('#manual_status_select').val(),
			content: $('#sql_content').val(),
			workflowid: $('#workflowid').val(),
		},function(data) {
			if(parseInt(data.status) === 2) {
				alert(data.msg);
				window.location.reload();
			}else {
				alert('fail');
			}
		})
	})
}


var addRoleFunc = {
	addRole() {
		$('#role_table').on('click','[data-role="add_role_btn"]',function() {
			window.currentOper = 'add';
			window.username = $(this).attr('data-username');
			$('#roleModalLabel').html('add role');
			$('#add_role_submit').html('add role');
			addRoleFunc.initRoleOper();
		}).on('click','[data-role="delete_role_btn"]',function() {
			window.currentOper = 'delete';
			window.username = $(this).attr('data-username');
			$('#roleModalLabel').html('delete role');
			$('#add_role_submit').html('delete role');
			addRoleFunc.initRoleOper();
		}).on('click','[data-role="view_role_btn"]',function() {
			window.currentOper = 'delete';
			window.username = $(this).attr('data-username');
			addRoleFunc.initRoleOper();
		})
		$('#add_role_submit').on('click',function() {
			var table_list = [];
			var extra_inst_list = [];
			var $table_select = $('#table_select');
			var $extra_inst_list = $('#extra_inst_list');
			
			$table_select.find('input[type="checkbox"]:checked').each(function() {
				var item = $(this);
				table_list.push(item.val());
			})
			$extra_inst_list.find('input[type="checkbox"]:checked').each(function() {
				var item = $(this);
				extra_inst_list.push(item.val());
			})
			$.post('/privcommit/'+window.currentOper+'/',{
				username:$('#add_role_username').val(),
				table_list:JSON.stringify(table_list),
				extra_inst_list:JSON.stringify(extra_inst_list)
			},function(data){
				alert(data.msg);
				//if(data.status==="saved") {
				//	alert('save success');
				//}
			}).fail(function() {
				alert(data.msg);
			})
		})
		// var roleArr = [];
		// $('#add_role_totext').on('click',function() {
		// 	var cluster_select = $('#cluster_select').val();
		// 	var schema_select = $('#schema_select').val();
		// 	var table_select = $('#table_select').val();
		// 	var role_content = $('#role_content');
		// 	var oldText = role_content.html();
		// 	var connectRole = cluster_select +' -- '+ schema_select +' -- '+ table_select;
		// 	roleArr.push({
		// 		cluster_select,
		// 		schema_select,
		// 		table_select
		// 	})
		// 	console.log(roleArr)
		// 	role_content.html(oldText + '<br>' +connectRole);
		// })
		
	},
	
	initRoleOper() {
		// filled schema_select
		$('#add_role_username').val(window.username);
		var $cluster_select = $('#cluster_select');
		var $extra_inst_list = $('#extra_inst_list');
		var cluster_list =[];
		$.getJSON('/privmod/'+window.currentOper+'/?username='+window.username,function(data) {
			if(data.cluster_list) {
				cluster_list = data.cluster_list;
				var clusterHTML = addRoleFunc.getOptionHTML(data.cluster_list);
				var extraInitListHtml = addRoleFunc.getExtraInitLIst(data.cluster_list,data.cluster_list[0]);
				$cluster_select.html(clusterHTML);
				$extra_inst_list.html(extraInitListHtml);
				// init schema list
				addRoleFunc.getSchemaList($cluster_select.val(),window.currentOper);
			}else {
				alert('missing data');
			}
		}).fail(function() {
			alert(data.msg);
		})
		$cluster_select.off('change.cluster_select').on('change.cluster_select',function() {
			addRoleFunc.getSchemaList($cluster_select.val(),window.currentOper);
			
			var extraInitListHtml = addRoleFunc.getExtraInitLIst(cluster_list,$(this).val());
			$extra_inst_list.html(extraInitListHtml);
		})
	},
	
	getSchemaList(cluster) {
		$.getJSON('/privmod/'+window.currentOper+'/?username='+window.username+'&cluster_name='+cluster,function(data) {
			if(data.schema_list) {
				var $schema_select = $('#schema_select');
				var schemaHTML = addRoleFunc.getOptionHTML(data.schema_list);
				$schema_select.html(schemaHTML);
				$('#schema_name_block').removeClass('hide');
				addRoleFunc.getTableList(cluster,$schema_select.val(),window.currentOper)
				$schema_select.off('change.schema_select').on('change.schema_select',function() {
					addRoleFunc.getTableList(cluster,$schema_select.val(),window.currentOper);
				})
			}else {
				alert('missing data');
			}
		}).fail(function() {
			alert(data.msg);
		})
	},
	
	getTableList(cluster,schema) {
		var _this = $(this)
		$.getJSON('/privmod/'+window.currentOper+'/?username='+window.username+'&cluster_name='+cluster+'&schema='+schema,function(data) {
			if(data.table_list) {
				var $table_select = $('#table_select');
				var tableHTML = '';
				var selectAll = $('#selectAll')
				Object.keys(data.table_list).forEach(function(item) {
					tableHTML += '<p><input type="checkbox" name="table" value="'+item+'" class="checkbox-input"">'+data.table_list[item]+'</p>';
				})
				$table_select.html(tableHTML);
				$('#table_name_block').removeClass('hide');
			}else {
				alert('missing data');
			}
		}).fail(function() {
			alert(data.msg);
		})
	},
	
	getOptionHTML(list) {
		var optionHTML = '';
		list.forEach(function(item) {
			optionHTML += '<option value='+item+'>'+item+'</option>';
		})
		return optionHTML;
	},
	getExtraInitLIst(list,val) {
		var _html = '';
		list.filter(function(item,index){return item!==val}).forEach(function(item){
			_html+= '<p><input type="checkbox" value="'+item+'">'+item+'</p>'
		})
		return _html;
	}
}

function fillQueryOraPage() {
	$('#query_ora_pagination').on('click','li',function() {
		var _this = $(this);
		var pageNo = _this.find('a').attr('data-href');
		$('#pageNo').val(pageNo);
		$('#query_ora_form').submit();
	})
}
function execSql() {
	$('#execSqlBtn').on('click',function() {
	var sql;
	if(window.getSelection().toString() && $(window.getSelection().focusNode).find('#sql_content').length>0){
		sql= window.getSelection().toString();
	}else {
sql= $('#sql_content').val();
	}

		if(sql.toString().trim() == '') {
			alert('sql不能为空');
		}else {
			$('#real_sql_content').val(sql);
			$(this).prop('disabled',true);
			$('#queryOraForm').submit();
		}
		// $.post('/queryora/',{
		// 	sql_content:sql,
		// 	cluster_name:$('#execSqlSelect').val()
		// },function() {
		// 	// window.location.reload();
		// })
	})
}


var allawr = {
	init() {
		this.searchAllawr();
	},
	searchAllawr() {
		window.currentPage = 1;
		
		$('#btn_search_awr').on('click',function() {
			allawr.getTableData();
		})

		$('#btn_generate_snap').on('click',function() {
			var _this = $(this);
			_this.prop('disabled',true)
			var cluster_name = $('#cluster_name_select').next().find('.filter-option').html();
			$.getJSON('/generatesnap/',{cluster_name},function(data) {
				alert(data.msg);
			}).always(function() {
				$('#btn_generate_snap').prop('disabled',false)
			})
		})
	},
	awrPagination() {
		$('#allawr_pages').on('click','a',function() {
			window.currentPage = parseInt($(this).attr('data-page'));
			allawr.getTableData(window.currentPage);
		})
		$('#awr_table').on('click','input',function() {
			var _this = $(this);
			var op = _this.attr('data-role');
			var snap_id = _this.attr('data-id');
			var cluster_name = _this.attr('data-cluster');
			$.getJSON('/allawr/',{cluster_name,snap_id,op},function(data){
				if(op === 'display') {
					window.location.href = data.awr_path;
				}else {
					alert(data.msg);
					$('#btn_search_awr').trigger('click');
				}
			})
		})
	},
	getTableData() {
		var cluster_name = $('#cluster_name_select').next().find('.filter-option').html();
			$.getJSON('/allawr/',{cluster_name,page:window.currentPage},function(data) {
				if(data.status == 'error'){
					alert(data.msg)
				}
				if(data.list_snapshot.length > 0) {
					var tbodyHTML = '';
					var buttonValue = '';
					var pagesHTML = '';
					data.list_snapshot.forEach(function(item) {
						buttonValue=item[2]+'' == 'init' ? 'generate' : (item[2]+'' == 'generated' ? 'display' : '    ');
						tbodyHTML += `<tr>
							<td>${item[0]}</td>
							<td>${item[1]}</td>
							<td><input type="button" class="btn btn-primary" value="${buttonValue}" data-role="${buttonValue}" data-cluster="${cluster_name}" data-id="${item[0]}"/></td>
							<td>${item[2]}</td>
						</tr>`
					})
					if(data.pages > 5) {
						pagesHTML = `
							${
								window.currentPage===1?
								'':`<li><a aria-label="Previous" data-page="${window.currentPage-1}"><span aria-hidden="true">&laquo;</span></a></li>`
							}
							<li class="active"><a data-page="${window.currentPage}">${window.currentPage}</a></li>
							<li><a data-page="${window.currentPage+1}">${window.currentPage+1}</a></li>
							<li><a data-page="${window.currentPage+2}">${window.currentPage+2}</a></li>
							<li><a data-page="${window.currentPage+3}">${window.currentPage+3}</a></li>
							<li><a data-page="${window.currentPage+4}">${window.currentPage+4}</a></li>
							<li>
								<a aria-label="Next" data-page="${window.currentPage+1}">
									<span aria-hidden="true">&raquo;</span>
								</a>
							</li>
						`

					} else {
						var lis = '';
						for(let i = 0; i < data.pages; i++) {
							lis+= `<li><a>${i+1}</a></li>`;
						}
						pagesHTML = lis;
					}
					$('#allawr_table').html(`
						<table class="table table-hover" id="awr_table">
							<thead>
								<tr>
									<th>snap_id</th>
									<th>快照时间</th>
									<th>操作</th>
									<th>状态</th>
								</tr>
							</thead>
							<tbody>
								${tbodyHTML}
							</tbody>
						</table>
						<nav aria-label="Page navigation" id="allawr_pages">
							<ul class="pagination">
								${pagesHTML}
							</ul>
						</nav>
					`)
					allawr.awrPagination();
					
				}
				
			})
	}
}
function downloadSql() {
	$('#download-btn').on('click',function() {
		var elHtml = $('#show_modal_sql_content').html().replace(/\n/g,'\r\n');
		var mimeType =  'text/plain';
		$('#createInvote').attr('href', 'data:' + mimeType  +  ';charset=utf-8,' + encodeURIComponent(elHtml));
		document.getElementById('createInvote').click();
	})
	$('#download-msg-btn').on('click',function() {
		var elHtml = $('#show_modal_msg_content').html().replace(/\n/g,'\r\n');
		var mimeType =  'text/plain';
		$('#createInvoteMsg').attr('href', 'data:' + mimeType  +  ';charset=utf-8,' + encodeURIComponent(elHtml));
		document.getElementById('createInvoteMsg').click();
	})
}

function allWorkflowPagination() {
	$('#allWorkflowPagination').on('click','li',function(e) {
		var currentPage = parseInt($(this).find('a').attr('data-href')) ;
		var url='/allworkflow/?pageNo='+currentPage+ '&search_status=' + $('#data_change_type').val()+'&hasAffirmed='+$('#hasAffirmed').val();
		window.location.href=url;
	})
}
downloadSql();
execSql();
renderClusterResult();
// renderAwrResult();
pagination();
// fillSqlContent();
confirmManual();
submitManualConfirm();
fillQueryOraPage();
addRoleFunc.addRole();
allawr.init();
// generateSnapshot();
allWorkflowPagination();
