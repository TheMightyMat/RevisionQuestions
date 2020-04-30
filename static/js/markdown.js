function markdown() {
	console.log("applying markdown")
	let markdownElements = document.querySelectorAll('.markdown');
	markdownElements.forEach(function (markdownElement) {
		console.log("marking " + markdownElement.innerHTML.trim())
		markdownElement.innerHTML = marked(markdownElement.innerHTML.trim())
	});
}