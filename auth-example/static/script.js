window.addEventListener('load', (event) => {
  document.getElementById('sign-in').onclick = function () {
    window.location.href = '/auth';
  };
});