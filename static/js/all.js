(function (doc) {
    'use strict';

    $('article.comment').each(function (index) {
        $(this).wrap('<div class="comment-family" id="' + this.id + '-family"></div>');
        $(this).after('<div class="comment-replies" id="' + this.id + '-replies"></div>');
        var parentId = $(this).data('parent');
        if (parentId) {
            $('#' + parentId + '-replies').append($(this).parent());
        }
        if ($(this).hasClass('erased') || $(this).hasClass('rejected')) {
            $(this).parent().addClass('folded');
        }
    });
    $('article.comment header').css('cursor', 'pointer').click(function (event) {
        $(this).parent().parent().toggleClass('folded');
    });
    $('article.comment .permalink').click(function (event) {
        event.stopPropagation();
    });
    $('.comment-family').click(function (event) {
        event.stopPropagation();
    });
    $('.comment-replies').click(function (event) {
        if ($(this).children('.comment-family:not(.folded)').length > 0) {
            $(this).children('.comment-family').addClass('folded');
        }
        else {
            $(this).children('.comment-family').removeClass('folded');
        }
    });

}(document));

