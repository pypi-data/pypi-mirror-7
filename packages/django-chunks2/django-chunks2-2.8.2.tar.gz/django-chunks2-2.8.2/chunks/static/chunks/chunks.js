(function($) {
    $(document).ready(function(){
        $('.edit_chunk').on(
            'click',
            'a',
            function() {
                var key = $(this).parent().data('key'),
                    url = '/chunks/edit/' + key + '/',
                    link = '<a href="' + url + '">редактировать</a>',
                    chunk = $(this).parent(),
                    original = chunk.html();
                chunk.empty();
                $.get(url,
                      {},
                      function(data) {
                          chunk.html(data)
                          $('form', chunk)
                              .ajaxForm({
                                  dataType: 'text',
                                  beforeSubmit: function() { $('button', chunk).prop('disabled', true); },
                                  success: function(d, s, x) {
                                      $('form', chunk).css({
                                          'border': '10px solid green',
                                      }).animate(
                                          {'opacity': 'hide',},
                                          1000, 'linear',
                                          function() {
                                              var txt = $('.edit_chunk form textarea').val();
                                              chunk.empty().html(txt + link)});
                                  },
                                  error: function(d, s, x) { console.log('ERROR: ' + x.status); }})
                              .find('textarea')
                              .keydown(function(e) {
                                  if (e.ctrlKey && e.keyCode == 13) {
                                      $(this).parent().submit();
                                  } else if (e.keyCode == 27) {
                                      chunk.empty().html(original);
                                  }
                              })
                              .select();
                      });
                return false;
            });
    });
})(jQuery);
