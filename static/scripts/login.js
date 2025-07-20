let signup_shown = true

const sf = document.getElementById('signup-form')
const lf = document.getElementById('login-form')

window.onload = function() {
  sf.style.display = 'block'
  lf.style.display = 'none'  
}

function toggle() {
  if(signup_shown) {
    sf.style.display = 'none'
    lf.style.display = 'block'  
    signup_shown=false
  } else {
    sf.style.display = 'block'
    lf.style.display = 'none'
    signup_shown=true  
  }
}