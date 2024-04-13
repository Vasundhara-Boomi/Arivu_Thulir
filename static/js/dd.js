const AP = [
    {
      APName: "Eat",
      imagePath: "/static/img/eat.png"
    },
    {
      APName: "Grow",
      imagePath: "/static/img/grow.png"
    },
    {
        APName: "Living thing",
        imagePath: "/static/img/living.png"
      },
      {
        APName: "Non-Living thing",
        imagePath: "/static/img/non_living.png"
      },
      {
        APName: "Young ones",
        imagePath: "/static/img/young_ones.png"
      }
];
  let correct = 0;
  let total = 0;
  const totalDraggableItems = 5;
  const totalMatchingPairs = 5; // Should be <= totalDraggableItems
  
  const scoreSection = document.querySelector(".score");
  const correctSpan = scoreSection.querySelector(".correct");
  const totalSpan = scoreSection.querySelector(".total");
  const playAgainBtn = scoreSection.querySelector("#play-again-btn");
  
  const draggableItems = document.querySelector(".draggable-items");
  const matchingPairs = document.querySelector(".matching-pairs");
  let draggableElements;
  let droppableElements;
  initiateGame()
  
  function initiateGame() {
    const randomDraggableBrands = generateRandomItemsArray(totalDraggableItems, AP);
    const randomDroppableBrands = totalMatchingPairs < totalDraggableItems ? generateRandomItemsArray(totalMatchingPairs, randomDraggableBrands) : randomDraggableBrands;
    const alphabeticallySortedRandomDroppableBrands = [...randomDroppableBrands].sort((a, b) => a.APName.toLowerCase().localeCompare(b.APName.toLowerCase()));
  
    // Create "draggable-items" and append to DOM
    for (let i = 0; i < randomDraggableBrands.length; i++) {
      document.querySelector(".draggable-items").insertAdjacentHTML("beforeend", `
          <img src="${randomDraggableBrands[i].imagePath}" class="draggable" draggable="true" id="${randomDraggableBrands[i].imagePath}">
      `);
  }
  
    // Create "matching-pairs" and append to DOM
    for (let i = 0; i < alphabeticallySortedRandomDroppableBrands.length; i++) {
      matchingPairs.insertAdjacentHTML("beforeend", `
        <div class="matching-pair">
          <span class="label">${alphabeticallySortedRandomDroppableBrands[i].APName}</span>
          <span class="droppable" data-brand="${alphabeticallySortedRandomDroppableBrands[i].imagePath}"></span>
        </div>
      `);
    }
  
    draggableElements = document.querySelectorAll(".draggable");
    droppableElements = document.querySelectorAll(".droppable");
  
    draggableElements.forEach(elem => {
      elem.addEventListener("dragstart", dragStart);
    });
  
    droppableElements.forEach(elem => {
      elem.addEventListener("dragenter", dragEnter);
      elem.addEventListener("dragover", dragOver);
      elem.addEventListener("dragleave", dragLeave);
      elem.addEventListener("drop", drop);
    });
  }
  // Drag and Drop Functions
  
  //Events fired on the drag target
  
  function dragStart(event) {
    event.dataTransfer.setData("text", event.target.id); // or "text/plain"
  }
  
  //Events fired on the drop target
  
  function dragEnter(event) {
    if(event.target.classList && event.target.classList.contains("droppable") && !event.target.classList.contains("dropped")) {
      event.target.classList.add("droppable-hover");
    }
  }
  
  function dragOver(event) {
    if(event.target.classList && event.target.classList.contains("droppable") && !event.target.classList.contains("dropped")) {
      event.preventDefault();
    }
  }
  
  function dragLeave(event) {
    if(event.target.classList && event.target.classList.contains("droppable") && !event.target.classList.contains("dropped")) {
      event.target.classList.remove("droppable-hover");
    }
  }
  
// ... (your existing code remains unchanged)

function drop(event) {
  event.preventDefault();
  event.target.classList.remove("droppable-hover");
  const draggableElementBrand = event.dataTransfer.getData("text");
  const droppableElementBrand = event.target.getAttribute("data-brand");
  const isCorrectMatching = draggableElementBrand === droppableElementBrand;
  total++;
  if (isCorrectMatching) {
    const draggableElement = document.getElementById(draggableElementBrand);
    event.target.classList.add("dropped");
    draggableElement.classList.add("dragged");
    draggableElement.setAttribute("draggable", "false");
    const img = document.createElement("img");
    img.src = draggableElement.src;
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "cover";
    event.target.appendChild(img);
    correct++;
    console.log('Correct:', correct, 'Total:', total);
    // Display description for the matched pair
    
    displayDescription(droppableElementBrand);
    correctSpan.textContent = correct;
    totalSpan.textContent = total;
  }

  correctSpan.textContent = correct;
  totalSpan.textContent = total;
  scoreSection.style.opacity = 0;
  setTimeout(() => {
    scoreSection.style.opacity = 1;
  }, 200);

  if (correct === Math.min(totalMatchingPairs, totalDraggableItems)) {
    playAgainBtn.style.display = "block";
    setTimeout(() => {
      playAgainBtn.classList.add("play-again-btn-entrance");
    }, 200);
  }
}

// Function to display description based on the matched pair
function displayDescription(pair) {
  const descriptionContent = document.querySelector(".description-content");
  // Add your descriptions here based on the matched pair
  const descriptions = {
    "/static/img/eat.png": "Living things eat. You eat",
    "/static/img/grow.png": "Living things grow. You grow",
    "/static/img/living.png": "Living things breathe and feel. They also move.",
    "/static/img/non_living.png": "Non living things dont eat, grow, feel, breath and have young ones.",
    "/static/img/young_ones.png": "Living things have young ones."
  };
  // Update the description content based on the matched pair
  if (descriptions.hasOwnProperty(pair)) {
    descriptionContent.textContent = descriptions[pair];
  } else {
    descriptionContent.textContent = "Description not available.";
  }
}
// ... (rest of your code remains unchanged)

  
  // Other Event Listeners
  playAgainBtn.addEventListener("click", playAgainBtnClick);
  function playAgainBtnClick() {
    playAgainBtn.classList.remove("play-again-btn-entrance");
    correct = 0;
    total = 0;
    draggableItems.style.opacity = 0;
    matchingPairs.style.opacity = 0;
    setTimeout(() => {
      scoreSection.style.opacity = 0;
    }, 100);
    setTimeout(() => {
      playAgainBtn.style.display = "none";
      while (draggableItems.firstChild) draggableItems.removeChild(draggableItems.firstChild);
      while (matchingPairs.firstChild) matchingPairs.removeChild(matchingPairs.firstChild);
      initiateGame();
      correctSpan.textContent = correct;
      totalSpan.textContent = total;
      draggableItems.style.opacity = 1;
      matchingPairs.style.opacity = 1;
      scoreSection.style.opacity = 1;
    }, 500);
  }
  // Function to generate draggable items and append them to the DOM
  function generateDraggableItems() {
    const draggableItems = document.querySelector(".draggable-items");
  
    const randomDraggableBrands = generateRandomItemsArray(totalDraggableItems, AP);
  for (let i = 0; i < randomDraggableBrands.length; i++) {
    draggableItems.insertAdjacentHTML("beforeend", `
      <img src="${randomDraggableBrands[i].imagePath}" class="draggable" draggable="true" id="${randomDraggableBrands[i].imagePath}">
    `);
  }

  draggableElements = document.querySelectorAll(".draggable");
  draggableElements.forEach(elem => {
    elem.addEventListener("dragstart", dragStart);
  });
  }
  // Auxiliary functions
  function generateRandomItemsArray(n, originalArray) {
    let res = [];
    let clonedArray = [...originalArray];
    if(n>clonedArray.length) n=clonedArray.length;
    for(let i=1; i<=n; i++) {
      const randomIndex = Math.floor(Math.random()*clonedArray.length);
      res.push(clonedArray[randomIndex]);
      clonedArray.splice(randomIndex, 1);
    }
    return res;
  }


generateDraggableItems();