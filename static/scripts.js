// WORK IN PROGRESS

function togglePass() {
    // gets the element that needs to be toggeled and toggles it based on its current state
    x = document.getElementById("pass").innerHTML 
    if (x == "********"){
      document.getElementById("pass").innerHTML = "Paragraph changed.";
    }
    else{
      document.getElementById("pass").innerHTML = "********";
    }
}


var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("addBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

function deleteRow(r) {
  // deletes a row when the delete button is pressed
  var i = r.parentNode.parentNode.rowIndex;
  document.getElementById("pass_table").deleteRow(i);
}