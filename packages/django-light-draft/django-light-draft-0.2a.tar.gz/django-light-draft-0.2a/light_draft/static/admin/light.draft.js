(function ($) {
    $(function () {
        var href = location.href + 'preview/',
            button = $('<li><a href="'+href+'" class="previewlink" target="_blank">Draft preview</a></li>');

        $('.object-tools > li > a.viewsitelink')
            .closest('ul')
            .find('li:first')
            .before(button);

        button.click(function () {
            var form = $('form[method="post"][enctype="multipart/form-data"]'),
                m2m = form.find('select[multiple="multiple"][id$="_to"]'),
                link;

            if (window.CKEDITOR) {
                $('textarea').each(function () {
                    var $textarea = $(this),
                        instance = window.CKEDITOR.instances[$textarea.attr('id')];
                    if (instance) {
                        $textarea.val(instance.getData());
                    }
                });
            }

            $('ul.errorlist').remove();

            // Select m2m befor post data
            m2m.children().attr('selected', 'selected');

            $.ajax({
                type: "POST",
                url: href,
                data: form.serialize(),
                dataType: 'text',
                async: false,
                success: function (response) {
                    // Deselect m2m
                    m2m.children().attr('selected', null);

                    if (response.indexOf('?hash=') > 0) {
                        link = response;
                    } else {
                        $('ul.object-tools').after(response);
                    }
                }
            });

            if (link) {
                $(this).children('a').attr('href', link);
                return true;
            }

            return false;
        });
    });
}(jQuery || django.jQuery));
