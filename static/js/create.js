function submitQuestion(user) {
  var api = window.location.origin + "/api/post/"

  var question = document.getElementById("question").value;
  var answer = document.getElementById("answer").value;
  var category = document.getElementById("category").value;
  if ((question && answer && category) && !(question === "" || answer === "" || category === "")) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", api, true);
    xhttp.setRequestHeader("Content-type", "application/json");

    var data = JSON.stringify({"question": question, "answer": answer, "category": category, "user": user})

    xhttp.send(data);

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
    alert("Must have a value for question, answer and subject!");
  }
}
