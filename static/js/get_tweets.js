

function setTopicValue(value) {

    // Animate the Button to the value clicked on.
    $("#topic_slider").slider('value', value);

}

function setSentimentValue(value) {

    // Animate the Button to the value clicked on.
    $("#sentiment_slider").slider('value', value);

}

    function isScrolledIntoView(elem){
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();
    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();
    return ((elemBottom >= docViewTop) && (elemTop <= docViewBottom) && (elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}

$(document).ready(function(){


	$(document).keypress(function(e) {

    	if(e.which == 13){

            $("#loading_message").removeClass('hidden');

            //Gets all user text boxes
            var users = $(".user_names");

            //gets api_key if there is one
            // var api_key = $("#api_key_label").html();
            // if (api_key==''){
            //     api_key = "NONE";
            // } else {
            //     api_key = api_key.substr(api_key.indexOf('>')+1);
            //     api_key = api_key.substr(0,api_key.indexOf('<'));
            // }

            //handles case where two tweeters are being compared
            if($("#one_tweeter").hasClass("hidden")){
                for (var i = 1; i < users.length; i++){
                    id = users[i].id;
                    if($("#"+id).val()==''){
                        window.location.replace("/compatability/UNK/UNK");
                            //+api_key);
                        return;
                    }
                }
        		user_name_1 = $("#twitter_name_1B").val();
        		if (user_name_1.charAt(0) == '@') user_name_1 = user_name_1.substr(1,user_name_1.length);
        		user_name_2 = $("#twitter_name_2").val();
        		if (user_name_2.charAt(0) == '@') user_name_2 = user_name_2.substr(1,user_name_2.length);
        		window.location.replace("/compatability/" + user_name_1 + "/" + user_name_2);
                    //+ "/" + api_key);
            
            //handles case where one tweeter is being analyzed
            } else {
                id = users[0].id;
                if($("#"+id).val()==''){
                    window.location.replace("/get_sentiment/UNKNOWN");
                    // +api_key);
                    return;
                }
                user_name_1 = $("#twitter_name_1A").val();
                if (user_name_1.charAt(0) == '@') user_name_1 = user_name_1.substr(1,user_name_1.length);
                window.location.replace("/get_sentiment/" + user_name_1);
                    //+"/"+api_key);
            }
    	}
    });

    $('input[type=radio]').change( function() {
        var checked = $('input[name=num_tweeters]:checked');
        console.log(checked);
        console.log(checked.attr('id'));
        if (checked.attr('id') == "one_tweeter_option"){
            $("#one_tweeter").removeClass("hidden");
            $("#two_tweeters").addClass("hidden");
        } else {
            $("#two_tweeters").removeClass("hidden");
            $("#one_tweeter").addClass("hidden");
        }
    });

     $("#topic_slider").slider({
        // This 'value' is the starting value.
        value: 0,
        min: 0,
        max: 100,
        step: 1,
        animate: "slow",
        slide: function(event, ui) {
        }
    });


    $("#sentiment_slider").slider({
        // This 'value' is the starting value.
        value: 0,
        min: 0,
        max: 100,
        step: 1,
        animate: "slow",
        slide: function(event, ui) {
        }
    });

    $("#add_api_key").on("click",function(){
        var key = prompt("Please enter your Alchemy API Key. You can get a free key at alchemyapi.com/api/register");
        if(key){
            $("#api_key_label").html("<b>"+key+"</b>");
        }
    });

    $('[data-toggle="tooltip"]').tooltip({
    
    }); 
        // $('[data-toggle="tooltip"]').tooltip({
        //     tooltipClass: "tooltip"
        // }); 

});

var not_scrolled = true;

$(window).scroll(function() {    
    if(isScrolledIntoView($('#sentiment_slider')) && not_scrolled)
    {
        setTopicValue(parseInt($("#topic_score").html()));
        setSentimentValue(parseInt($("#sentiment_score").html()));
        not_scrolled = false;

    }    
});