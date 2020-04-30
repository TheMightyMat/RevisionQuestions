function markdown() {
	let markdownElements = document.querySelectorAll('.markdown');
	markdownElements.forEach(function (markdownElement) {
		markdownElement.innerHTML = _.unescape(marked(markdownElement.innerHTML.trim()))
	});
}