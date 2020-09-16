var app = new Vue({
  el: '#app',
  data: {
    notes : [
      "do",
      "ré",
      "mi",
      "fa",
      "sol",
      "la",
      "si"
    ]
  },
  methods : {
     alt(note) {
       //alert(note);
       console.log(note)
     }
  }
})