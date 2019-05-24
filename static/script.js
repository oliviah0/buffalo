$(function () {
  $.ajax({
    url: '/autocomplete'
  }).done(function (data) {
    $('#search').autocomplete({
      source: data,
      minLength: 1
    });
  });
});

let $stat = $(".profile-stats li");


$stat.on("click", function(e){
  $stat.removeClass("active");
  // $(e.target).addClass("active");
});