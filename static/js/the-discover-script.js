/** the-discover-script.js **/

var diceIntervalTime

function animateDice() {
  var dices = ["&#9856;","&#9857;","&#9858;","&#9859;","&#9860;","&#9861;"]
  document.getElementById("the-dice-object").innerHTML = dices[Math.floor(Math.random()*dices.length)]
}
function startDiceAnimation() { diceIntervalTime = setInterval(animateDice, 150) }
function stopDiceAnimation() { clearInterval(diceIntervalTime) }

function closeMenu() { document.getElementById("the-menu-container").style.display = "none" }
function openMenu() {
  var menuState = document.getElementById("the-menu-container").style.display
  if (menuState === "block") {
    closeMenu()
  } else {
    document.getElementById("the-menu-container").style.display = "block"
  }
}

function openLink(url) {
  closeMenu()
  window.location.href = url
}

function refreshUrl() {
  var url = "/discover"
  closeMenu()
  document.getElementById("the-loader-container").style.display = "block"
  var xhr = new XMLHttpRequest()
  xhr.open("GET", url)
  xhr.onload = function() {
    if (xhr.status === 200) {
      window.location.href = url
    }
    else {
      alert("Ooops request failed, status is " + xhr.status)
    }
  }
  xhr.send()
}

function historyPushState(title) {
  window.history.pushState({"discover":"discover"}, title, "/discover");
}

function removeUnwantedClasses() {
  document.getElementById("the-html-container").classList.value = ""
  document.getElementById("the-body-container").classList.value = ""
}
