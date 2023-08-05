;;(function($) {
    $(document).ready(function() {
        var popupHelperLabel = $($('#externalizelink-i18n').text()).attr('data-i18n-popup-message'),
            siteConfiguration = $.parseJSON($('#externalizelink-data').text()),
            i, patter = /(^|\s+)[a-zA-Z0-9-\_](\s+|$)/g;

        function externalizeLink(event) {
            event.preventDefault();
            window.open($link.attr('href'));
        }

        function manageTitle($link) {
            if ($link.attr('title')) {
                $link.attr('title', $link.attr('title') + ' - ' + popupHelperLabel);
            } else {
                $link.attr('title', popupHelperLabel);
            }
        }

        function manageAdditionalAttrs($link) {
            var attrName, attrValue, i, pattern = "(^|\\s+)$ATTR(\\s+|$)", re; 
            for (i=0;i<siteConfiguration.additional_attrs.length;i++) {
                attrName = siteConfiguration.additional_attrs[i].name;
                attrValue = siteConfiguration.additional_attrs[i].value;
                if ($link.attr(attrName)) {
                    re = new RegExp(pattern.replace('$ATTR', attrValue), 'g');
                    if (!re.test(attrValue)) {
                        $link.attr(attrName, $link.attr(attrName) + ' ' + attrValue);
                    }
                } else {
                    $link.attr(attrName, attrValue);
                }
            }
        }

        if (!siteConfiguration.enabled) {
            return;
        }
        for (i=0;i<siteConfiguration.links_selection.length;i++) {
            siteConfiguration.links_selection[i] = siteConfiguration.links_selection[i]
                    .replace('$PORTAL_URL', portal_url);
            $(siteConfiguration.links_selection[i]).each(function () {
                $link = $(this);
                manageTitle($link);
                manageAdditionalAttrs($link);
                $link.click(externalizeLink);
            });
        }
    });
})(jQuery);
