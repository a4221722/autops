function validateForm(element) {
	var result = true;
	element.find('[required]').each(
		function () {
			var fieldElement = $(this);
			//如果为null则设置为''
			var value = fieldElement.val() || '';
			if (value) {
				value = value.trim();
			}
			if (!value || value === fieldElement.attr('data-placeholder')) {
				alert((fieldElement.attr('data-name') || this.name) + "不能为空！");
				result = false;
				return result;
			}
		}
	);
	return result;
}

function getValue(idName) {
	return document.getElementById(idName).value;
}

$("#btn-submitsqlora").click(function (){
	//获取form对象，判断输入，通过则提交
	var formSubmit = $("#form-submitsqlora");
	var sqlContent = $("#sql_content");
	var clusterName = $("#cluster_name");
	var review_man = $('#review_man');
	var message = $('#message');
	var $check = $('#cluster_name_checkbox').find('input[type="checkbox"]:checked');
	var checkedArr = [];
	var message = $("#message");
	$check.each(function() {
		var item = $(this);
		checkedArr.push(item.val());
	})
	clusterName.val(checkedArr.join());

	var $check_review = $('#review_man_checkbox').find('input[type="checkbox"]:checked');
	var viewArr = [];
	$check_review.each(function() {
		var item = $(this);
		viewArr.push(item.val());
	})
	review_man.val(viewArr.join());
	
	var type = $('#data_change_type').val();

	if(validateForm(formSubmit)){
		if (clusterName.val() == '') {
			alert('实例名不能为空');
		}else if(review_man.val() == '') {
			alert('审核人不能为空');
		}else if((type === '数据修订'|| type === '数据初始化')&&sqlContent.val()===''){
			alert('sql文本不能为空');
		}else if((type === '数据迁移'|| type === '其他')&&message.val()==='') {
			alert('备注不能为空');
		}else {
			$('#btn-submitsqlora').prop('disabled',true);
			formSubmit.submit();
		}
	}
});

$("#review_man").change(function review_man(){
    var review_man = $(this).val();
    $("div#" + review_man).hide();
});

function deleteTitle() {
	var $cluster_name = $('#cluster_name');
	var $realSelect = $cluster_name.next().find('button');
	// clean title
	$realSelect.attr('title','');
	// add new block
	$realSelect.on('mouseover',function(){
		let $realSelect = $cluster_name.next();
		let content = $realSelect.find('.filter-option').html();
		if(!$('#groupContent').length){
			$(this).parent().append('<div id="groupContent" class="group-content"><span class="close-group-icon" id="closeGroupIcon">x</span>'+content+'</div>')
			// after append can remove block
			$('#closeGroupIcon').on('click',function() {
				$('#groupContent').remove();
			});
		}
	}).on('click',function() {
		$('#groupContent').remove();
	})
}

function readFile() {
	$('#btn-addAttachment').on('change',function() {
		var file = document.getElementById("btn-addAttachment").files[0];
		if(file) {
			var reader = new FileReader();
			reader.readAsText(file,'UTF-8');
			reader.onload = function (e) {
				var fileText = e.target.result;
				$('#sql_content').val(fileText);
			}
		} else {
			alert('please add attachment');
		}
	})
}

$(document).ready(function () {
	// var pathname = window.location.pathname;
	// if (pathname == "/editsql/") {
	// 	document.getElementById('workflowid').value = sessionStorage.getItem('editWorkflowDetailId');
	// 	document.getElementById('workflow_name').value = sessionStorage.getItem('editWorkflowNname');
	// 	document.getElementById('sql_content').value = sessionStorage.getItem('editSqlContent');
	// 	document.getElementById('cluster_name').value = sessionStorage.getItem('editClustername');
	// 	document.getElementById('is_backup').value = sessionStorage.getItem('editIsbackup');
	// 	document.getElementById('review_man').value = sessionStorage.getItem('editReviewman');
	// 	var sub_review_name = sessionStorage.getItem('editSubReviewman');
	// 	$("input[name='sub_review_man'][value=\'"+sub_review_name+"\']").attr("checked", true);

	// 	// getValue('workflowid') = sessionStorage.getItem('editWorkflowDetailId');
	// 	// getValue('workflow_name') = sessionStorage.getItem('editWorkflowNname');
	// 	// getValue('sql_content') = sessionStorage.getItem('editSqlContent');
	// 	// getValue('cluster_name') = sessionStorage.getItem('editClustername');
	// 	// getValue('is_backup') = sessionStorage.getItem('editIsbackup');
	// 	// getValue('review_man') = sessionStorage.getItem('editReviewman');
	// 	// var sub_review_name = sessionStorage.getItem('editSubReviewman');
	// 	// $("input[name='sub_review_man'][value=\'"+sub_review_name+"\']").attr("checked", true);
	// }
	readFile();
	// delete title
	// var $cluster_name = $('#cluster_name');
	// $cluster_name.on('hidden.bs.select', function () {
	// 	deleteTitle()
	// })
	// // for exec after bs-select
	// setTimeout(function(){
	// 	$cluster_name.trigger('hidden.bs.select')
	// },2000)
});
