(function (doc) {
    'use strict';

    var VOTE_CLASSES = 'positive neutral negative';

    $('.vote-form').submit(function (event) {
        event.preventDefault();
        var _form = $(this);
        $.post(_form.context.action, _form.serialize(), function (data) {
            _form.parent().removeClass(VOTE_CLASSES);
            _form.parent().addClass(data.status);
        });
    });

    $('.user-messages').delay(5000).slideUp();

}(document));
