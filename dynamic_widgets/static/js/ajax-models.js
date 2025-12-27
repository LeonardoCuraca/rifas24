function submitForm(form) {
	var url = $(form).attr('action');
	var method = $(form).attr("method");
	var field = $(form).attr("data-field");

	var data = new FormData(form);

	$.ajax({
		url: url,
		type: method,
		data: data,
		processData: false,
		contentType: false,
		success: function (data) {

			if (data.status === "ok") {
				var select = $("select[data-field=" + field + "]");
				
				select.append($("<option></option>").attr("value", data.id).text(data.str));
				select.val(select.attr("multiple") ? select.val().concat(data.id) : data.id);
				select.trigger("chosen:updated");
				
				$('#modal_' + field).modal('hide');
			} else {
				console.log(data.errors)
			}

		},
		error: function (data) {
			console.log(data);
		}
	});
}