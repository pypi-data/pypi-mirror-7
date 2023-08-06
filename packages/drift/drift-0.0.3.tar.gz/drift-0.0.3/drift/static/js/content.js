var content = (function() {
    var pub = {};
    var cancel_saved_data = null;
    var allowed_tags = ["code", "span", "div", "label", "a", "br", "p", "b", "i", "del", "strike", "u",
                        "img", "video", "audio", "iframe", "object", "embed", "param", "blockquote",
                        "mark", "cite", "small", "ul", "ol", "li", "hr", "dl", "dt", "dd", "sup", "sub",
                        "big", "pre", "code", "figure", "figcaption", "strong", "em", "table", "tr", "td",
                        "th", "tbody", "thead", "tfoot", "h1", "h2", "h3", "h4", "h5", "h6", "link",
                        "style", "form", "input"]

    pub.content = {};
    pub.content.id = '';
    pub.version = {};
    pub.version.id = '';
    pub.prepopulated_fields = [];
    pub.upload_photos_url = '';
    pub.recent_photos_url = '';
    pub.auto_save_url = '';

    pub.save_url = '';
    pub.edit = false;

    var control_toggle = function() {
        $('.control.edit').toggle();
        $('.control.save').toggle();
    }

    pub.initialize = function(initialize_editor) {
        $('.toggle_content_history').click(function() {
            $('#content_history').toggle();
            return false;
        })

        $('header').css('padding-top', '34px');
        $('html, body').scrollTop(34);

        $('.editable.textinput').each(function(i) {
            var $this = $(this);
            if ($this.text() == '') {
                $this.text($this.data('default'));
                $this.addClass('default');
            }
            $this.on('change keydown keypress input', function(event)
            {
                var $this = $(this);
                var content = $this.text().trim();

                $('#' + $this.data('target')).val(content);
                $('#' + $this.data('target')).trigger(event.type);
            })

            $this.on('focus active', function()
            {
                var $this = $(this);
                if ($this.hasClass('default')) {
                    $this.text('');
                    $this.removeClass('default');
                }
            })

            $this.on('blur', function()
            {
                var $this = $(this);
                if ($this.text() == '') {
                    $this.text($this.data('default'));
                    $this.addClass('default');
                }
            })
        })

        if (pub.edit == true) {
          // Warn user if they navigate away after a change.
          $(':input, textarea, *[contenteditable=true]').bind('change, input', function() { warn(true); });
          // Explicitly disable warning
          $('.nowarn').click(function() { warn(false); });
        }

        // Boostrap date picker
        //$('.content_datefield').datepicker();

        // Prepopulated fields
        $.each(pub.prepopulated_fields, function(i, prepopulated_field) {
            var prepopulatedField = $('#' + prepopulated_field.target_id);
            prepopulatedField.data('_changed', !prepopulatedField.val() == '');
            prepopulatedField.change(function() {
                prepopulatedField.data('_changed', true);
            });
            var sourceField = $('#' + prepopulated_field.source_id);
            var populate = function() {
                if (prepopulatedField.data('_changed')) {
                    return;
                }
                prepopulatedField.val(URLify(sourceField.val(), 80));
            }
            sourceField.on('change keydown keypress input', populate);
        })

        if (initialize_editor==undefined) {
          pub.default_initialize_editor();
        } else {
          initialize_editor();
        }

    }

    pub.default_initialize_editor = function() {
      if ($('.editable.wysiwyg').wysiwyg == undefined) {
        if (pub.edit) {
            var opts = {
                imageUpload: pub.upload_photos_url,
                imageGetJson: pub.recent_photos_url,
                convertDivs: false,
                allowedTags: content.allowed_tags
            };

            if (pub.auto_save_url != '') {
                opts.autosave = pub.auto_save_url;
                opts.autosaveInterval = 25;
            }

            $('.content').redactor(opts);
        }
      } else {
        $('.editable.wysiwyg').wysiwyg();
        $('.drift.editable.wysiwyg.textarea').on('keydown keypress keyup', function(event) {
          var $this = $(this);
          $('#' + $this.data('target')).val($this.cleanHtml());
        });
      }

    }

    /*pub.edit = function() {
        $.post(
            content.save_url,
            {
                'op': 'edit',
                'version_id': content.version.id,
            }
            function () {
                $('.content').redactor({
                    convertDivs: false,
                    allowedTags: content.allowed_tags
                });
                cancel_saved_data = $('.content').getCode();
                control_toggle();
            }
        )
    }*/

    pub.save = function() {
        var html = $('.content').getCode();
        $.post(
            content.save_url,
            {
                'op': 'update',
                'version_id': content.version.id,
                'html': html
            },
            function() {
                // destroy editor
                $('.content').destroyEditor();
                control_toggle();
            }
        )

    }

    pub.cancel = function() {
        $('.content').destroyEditor();
        if (cancel_saved_data != null) {
            $('.content').html(cancel_saved_data);
        }
        cancel_saved_data = null;
        control_toggle();
    }

    var warn_message = function() {
        return (
            'You have made changes which will not be saved. '
        );
    }

    var warn = function(on) {
        window.onbeforeunload = on ? warn_message : null;
    }

    return pub;
}());


