$('para').on('click', function() {
  $(this).html('wow lol');
});

$('h1.title1').on('mouseover', function() {
  $(this).animate({
    "letter-spacing": "10px",
    "font-size": "40px"
  }, 1000, function() {
    $(this).html("Manu Gandham"); 
  })
});


$('a#facebook').on('mouse over', function() {
    $(this).html("A social network site"); 
  });


$('h4').on('click', function() {
 $('html').toggleClass('extra_html');
  $('#paraID').toggleClass('para');
 $('#paraID').toggleClass('extra_img');
});
