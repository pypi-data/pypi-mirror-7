(function($) {
    $(document).ready(function() {

        // If the info viewlet isn't here, 
        // stop right away.
        if( $('#js_info').length < 1 )
        {
            return 0;
        }

        var url = document.URL;

        // We really don't need to ever use this on the edit page.
        if (url.indexOf('/edit') > 0) {
            return 0;
        }

        var json = $('#buttonJson').text();
        var settings = jQuery.parseJSON( json );

        if( settings.length < 1 )
        {
            return 0;
        }
        var stateDescription = settings.stateDescription;
        var allowed_transitions = settings.allowedTransitions;
        var state = settings.wfState;
        var pageElement = settings.pageElement;
        var fixed = settings.floating;
        var preferencesUrl = settings.preferencesUrl;

        // This is needed since some URL's end in a slash,
        // and some don't
        function stripSlash(url) {
            if(url.substr(-1) == '/') {
                return url.substr(0, url.length - 1);
            }
            else
            {
                return url;
            }
        }

        var base = stripSlash($("base").attr("href"));

        // Since this is referring to links generated internally, and not by a theme,
        // this shouldn't change anytime soon.
        var modify_url_string = "/content_status_modify?workflow_action=";

        // This works by grabbing every <a> that has an href matching the 
        // URI corresponding to the given transitions
        var transitions = $("a[href^='" + base + modify_url_string + "']");

        var buttons = [];
        var allowed = [];
        var transitionClassNames = [];

        // Being very careful to grab the correct edit link
        var editUrl = $('#edit-bar').find('#contentview-edit').find('a');

        // Makes sure the pageElement property is set
        if($(pageElement).text() == "")
        {
            pageElement = "#portal-breadcrumbs";
        }

        $(allowed_transitions).each(function() {
            allowed.push(base + modify_url_string + this);
        });

        transitions.each(function() {

            // if statement checks that the links text is allowed
            if( $.inArray($(this).attr('href'), allowed) >= 0 )
            {
                buttons.push( this );
            }
        });

        if( $(editUrl).length > 0 )
        {
            buttons.push(editUrl);
        }

        if( buttons.length < 1 )
        {
            return 0;
        }

        var html ="<div id='transitionButtons'>";

        html = html + 
        '<span id="prefs_link" rel="#prefsDialog">x</span>' + 
        '<h4>Workflow state: <span class="stateTitle" >' + state +'</span></h4>' +
        '<p class="tbText">' + stateDescription + '</p>' + 
        '<div class="button-row"></div></div>';

        var message = "If you no longer want to see this widget,";
        message += " check the \"Disable transition buttons widget\" option in personal preferences."

        $(html).insertBefore(pageElement);

        $(buttons).each(function() {

            var thisButton =
            '<button class="button" ' +
            'onclick="window.location.href=\'' + $(this).attr('href') + '\'">' +
            $(this).text() +
            '</button>';

            $('.button-row').append($(thisButton));
        })

        var currentState = $('.state-' + state.toLowerCase() );
        stateColor = currentState.css('background-color');
        $('.stateTitle').css('background-color', stateColor);

        // add class to make the box "float"
        if( fixed )
        {
            $('#transitionButtons').addClass('floating');
        }

        $('#prefsDialog').prepend(message);



        $('#prefs_link').overlay({
                top: 250,
        });
    
    });
})(jQuery);