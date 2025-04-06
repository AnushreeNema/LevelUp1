/*javascript function for dynamic functionalties*/
function user_question() {
  const question = document.getElementById("userInput").value;
  const chatBox = document.getElementById("response");
  fetch("/question", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })
    .then((res) => res.json())
    .then((data) => {
      chatBox.innerHTML += `<p><strong>You:</strong> ${question}</p>`;
      chatBox.innerHTML += `<p><strong>Smart_Teacher:</strong> ${data.answer}</p>`;
      if (data.C) {
        document.getElementById("C").innerText = data.C;
      }
      document.getElementById("userInput").value = "";
    });
}
