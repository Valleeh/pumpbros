// Function to show the exercise form
var settings_flag = false;
function showForm(exerciseName) {
  document.getElementById('exerciseTitle').innerText = exerciseName;
  document.getElementById('exerciseInput').value = exerciseName;
  document.getElementById('exerciseForm').style.display = 'block';
  window.scrollTo(0, document.body.scrollHeight); // Scroll to the form
}
function prefillWorkoutForm(buddy) {
  var exercise = document.getElementById('exerciseInput').value;
  fetch(`/get_latest_workout?exercise=${exercise}&buddy=${buddy}`)
    .then(response => response.json())
    .then(data => {
      document.getElementById('weight').value = data.weight;
      document.getElementById('reps').value = data.reps;
      // Assuming you want to prefill the exercise and buddy as well
    })
    .catch(error => {
      console.error('Error fetching latest workout:', error);
    });
}
function submitWorkoutWithBuddy(buddyName) {
  const formData = new FormData(document.getElementById('workoutForm'));
  formData.append('pumpBuddy', buddyName); // Append the selected buddy to the form data

  fetch('/submit_workout', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();  // Assuming the response is text
    })
    .then(data => {
      // Update the page with a success message
      const messageDiv = document.getElementById('formMessage');
      messageDiv.textContent = 'Data saved';
      messageDiv.style.color = 'green'; // Optional: Style as needed

      // Clear the message after 3 seconds
      setTimeout(() => {
        messageDiv.textContent = '';
      }, 3000); // 3000 milliseconds = 3 seconds
    })
    .catch((error) => {
      console.error('Error:', error);
      const messageDiv = document.getElementById('formMessage');
      messageDiv.textContent = 'An error occurred';
      messageDiv.style.color = 'red'; // Change color for error message
    });

  // Prevent the form from submitting in the traditional way
  return false;
}

function selectBuddy(buddyName) {
  document.getElementById('selectedBuddy').value = buddyName;
  // Optionally: Highlight the selected buddy button
}
function settings() {
  settings_flag = true;
}
function updateWeightValue(value) {
  document.getElementById('weightValue').textContent = `Current: ${value}kg`;
  document.getElementById('weight') = value;
}

function increment(id) {
    var input = document.getElementById(id);
    var currentValue = parseInt(input.value, 10) || 0;
    input.value = currentValue + parseInt(input.step, 10);
}

function decrement(id) {
    var input = document.getElementById(id);
    var currentValue = parseInt(input.value, 10) || 0;
    input.value = currentValue - parseInt(input.step, 10);
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').then((registration) => {
      console.log('ServiceWorker registration successful with scope:', registration.scope);
    }, (err) => {
      console.log('ServiceWorker registration failed:', err);
    });
  });
}
