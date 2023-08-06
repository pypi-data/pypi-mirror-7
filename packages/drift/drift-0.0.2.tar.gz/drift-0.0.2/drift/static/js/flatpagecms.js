var flatpagecms = (function() {
    var pub = {}; 
    var cancel_saved_data = null;
    var allowed_tags = ["code", "span", "div", "label", "a", "br", "p", "b", "i", "del", "strike", "u",
                        "img", "video", "audio", "iframe", "object", "embed", "param", "blockquote",
                        "mark", "cite", "small", "ul", "ol", "li", "hr", "dl", "dt", "dd", "sup", "sub",
                        "big", "pre", "code", "figure", "figcaption", "strong", "em", "table", "tr", "td",
                        "th", "tbody", "thead", "tfoot", "h1", "h2", "h3", "h4", "h5", "h6", "link",
                        "style", "form", "input"]
    
    pub.flatpage = {};
    pub.flatpage.id = "";
    pub.flatpage.url = "";
    pub.flatpage.title = "";
    pub.flatpage.template_name = "";
    pub.upload_photos_url = "";
    pub.recent_photos_url = ""
    
    var control_toggle = function() {
        $('.control.edit').toggle();
        $('.control.save').toggle();
    }
 
    pub.initialize = function() {
        $('.control.save').hide();
    }
 
    pub.edit = function() {
        $('.flatpage_content').redactor({
            imageUpload: pub.upload_photos_url,
            imageGetJson: pub.recent_photos_url,
            convertDivs: false,
            allowedTags: flatpagecms.allowed_tags
        });
        cancel_saved_data = $('.flatpage_content').getCode();
        control_toggle();
    }
    
    pub.save = function() {
        var html = $('.flatpage_content').getCode();	
        $.post("/admin/flatpages/flatpage/" + pub.flatpage.id + "/",
               {
                'url': pub.flatpage.url,
                'title': pub.flatpage.title,
                'content': html,
                'sites': 1, // BEWARE: This is evil, but I am not sure how to encode this data if there were multiple values.
                '_continue': "Save and continue editing",
                'template_name': pub.flatpage.template_name
                })
        // destroy editor
        $('.flatpage_content').destroyEditor();
        control_toggle();
    }
    
    pub.cancel = function() {
        $('.flatpage_content').destroyEditor();
        if (cancel_saved_data != null) {
            $('.flatpage_content').html(cancel_saved_data);
        }
        cancel_saved_data = null;
        control_toggle();
    }
 
    return pub;
}());


