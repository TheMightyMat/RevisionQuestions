function deleteQuestion(id) {
	var api = window.location.origin + "/api/delete/" + id

	var xhttp = new XMLHttpRequest();
	xhttp.open("DELETE", api, true);
	xhttp.setRequestHeader("Content-type", "application/json");

	xhttp.send();

	xhttp.onreadystatechange = processRequest

	function processRequest(e) {
		if (xhttp.readyState == 4) {
			if (xhttp.status == 200) {
				alert("Question deleted sucessfully!")
				window.location.href = "/"
			} else {
				alert("Failed to delete question! Status code: " + xhttp.status + ", response: " + xhttp.response)
			}
		}
	}
}
