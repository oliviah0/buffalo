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

// let $stat = $(".profile-stat li");
let $stat = $(".stat");


$stat.on("click", function(e){
  // $stat.removeClass("active");
  $(e.target).addClass("active");
});