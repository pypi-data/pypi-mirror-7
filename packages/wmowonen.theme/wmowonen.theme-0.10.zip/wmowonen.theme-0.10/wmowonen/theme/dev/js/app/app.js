
var updateLinks = function ()
{
  links = $(this).find("a");
  
  for (var l=0;  l < links.length; l++)
  {
    var newQuery = window.location.search.split("&");
    var searchableText = "";
    for (var q in newQuery)
    {
      if (newQuery[q].indexOf("SearchableText=") > -1)
      {
        searchableText = newQuery[q].substring(newQuery[q].indexOf("SearchableText=")+15);
        
      }
    }
    if ($(links[l]).attr("href"))
    {
        try
        {
          var currentLinkSplit = $(links[l]).attr("href").split("SearchableText=");
          var currentLink = "";
          if (currentLinkSplit[1].indexOf("&") > -1)
          {
            currentLink = currentLinkSplit[0] + "SearchableText=" + searchableText + currentLinkSplit[1].substring(currentLinkSplit[1].indexOf("&"));
          }
          else
          {
            currentLink = currentLinkSplit[0] + "SearchableText=" + searchableText;
          }
          $(links[l]).attr("href", currentLink);
        } catch (err) 
        {
          
        }
    }
  }
};

$(function() {
  $('.infoWrapper').matchHeight(true);

  $('.navbar-form .form-control').addClass('hidden-lg hidden-md');

  $('.navbar-form button').click(function( event ) {
    if( $('.navbar-form .form-control').is(':hidden') ) {
      event.preventDefault();
    }

    $('.navbar-form .form-control').removeClass('hidden-lg hidden-md');

  });
  
  if ($(".template-search").length > 0)
  {
    setInterval(function () {
        $(".harcodedResultTypes").each(updateLinks);
        $(".harcodedThemas").each(updateLinks);
        $(".harcodedRegions").each(updateLinks);
      }, 1000);
  }

});
