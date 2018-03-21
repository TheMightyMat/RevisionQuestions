function submitQuestion() {
  var api = "http://127.0.0.1:5000/api/"

  var question = document.getElementById("question").value;
  var answer = document.getElementById("answer").value;
  var category = document.getElementById("category").value;

  if ((question && answer && category) && !(question === "" || answer === "" || category === "")) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", api + encodeURIComponent(question) + "/" + encodeURIComponent(answer) + "/" + encodeURIComponent(category), true);
    xhttp.setRequestHeader("Content-type", "text");
    xhttp.send();

    xhttp.onreadystatechange = processRequest

    function processRequest(e) {
      if (xhttp.readyState == 4) {
          if(xhttp.status == 200) {
            alert("Question created sucessfully!")
          } else {
            alert("Failed to create question! Status code: " + xhttp.status + ", response: " + xhttp.response)
          }
      }
    }
  } else {
    alert("Must have a value for question, answer and category!");
  }
}
