(function($){
  $(document).ready(function() {

    var field = $("#temporalCoverage");

    field.tokenInput([], {
      theme: "facebook",
      tokenValue: "name",
      hintText: "Type in a year or a range of years (e.g. 1999-2005).",
      searchingText: "",
      noResultsText: "",
      tokenDelimiter: "\n",
      prePopulate: function(){
        var value = field.val().split("\n");
        return $.map(value, function(val, idx){
          return {name: val, id: val};
        });
      }(),
      allowNewTokens: true
    });
  });
})(jQuery);
