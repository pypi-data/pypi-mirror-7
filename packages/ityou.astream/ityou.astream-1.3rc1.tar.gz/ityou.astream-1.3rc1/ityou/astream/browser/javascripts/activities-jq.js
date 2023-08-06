/*
$(document).ready(
	function () {
		
		// === BEGIN ====================================
		NOTIFY_ACTIVITIES_REPEAT = 10000
        NOTIFY_COMMENTS_REPEAT   = 10000

        if ($("#ASTREAM_DELAY").length) {
    		var NOTIFY_ACTIVITIES_REPEAT =  parseInt($("#ASTREAM_DELAY").text())
    		var NOTIFY_COMMENTS_REPEAT = parseInt($("#ASTREAM_DELAY").text())
        }
        var uid = $('#uid').text()
		var ESI_ROOT = $("#ESI_ROOT").text()
		var ajax_activities = ESI_ROOT + '/@@ajax-activities'
		var ajax_comments = ESI_ROOT + '/@@ajax-post-comment'

		function activity_comment (context) {
		
			context.find("textarea").autoResize({
			    onResize : function() {
			        $(this).css({opacity:0.8});
			    },
			    animateCallback : function() {
			        $(this).css({opacity:1});
			    },
			    animateDuration : 300,
			    extraSpace : 20
			});
			
			context.find(".activity-hide-button").click(function (e) {
				e.preventDefault();
				$(".activity-all-button").show();
				$(this).parent().parent().slideUp("fast");
			});
		
	    	context.find(".comment-input-field").hide();
	    	context.find(".comment-save-button").hide();
	
	    	context.find(".comment-hide-button").click(function (e) {
	    		e.preventDefault();
	        	$(this).parent().slideToggle("fast");
				$(this).parent().parent().next().find(".comment-all-button").show();
				
	          });
	
	    	context.find(".comment-all-button").click(function (e) {
	    		e.preventDefault();
	        	$(this).parent().prev().children().each(function() {
	        		$(this).slideDown();
	        	});
				$(this).hide();
	          });
	
	    	context.find(".comment-input-button").click(function (e) {
	    		e.preventDefault();
	        	$(this).toggle();
	        	$(this).next().slideDown("fast");        	
	        	$(this).next().next().toggle();
	          });
	        
	    	context.find(".comment-save-button").click(function (e) {
	    		e.preventDefault();
	    		
	        	var coin 	= $(this).prev();
	        	var comment = coin.find("textarea:last").val();
	        	var alist 	= $(this).parent().parent().parent();
	        	var hash 	= alist.attr('id');
	        	var last_comment = $(this).parent().prev().find("li:last")
	        	var last_comment_hash = last_comment.attr('id');
	        	
	        	var act_li  = alist.prev().parent().prev().parent();
	
	        	if (comment) {
		        	$.getJSON(ajax_comments, {'comment':comment, 'hash': hash},
		        		function(data) {
		        			if (data != '') {
		        				coin.find("textarea").val("");
		        				if (data.hash != last_comment_hash) {
		        					$( "#activity-comment-tmpl" )
									    .tmpl( data )
										.appendTo( ".activities > li[id=" + hash + "] > .activity-wrapper > ul.comments" )
										.css({'background-color': '#FFE'}).slideDown();
		        					
		        					$("#" + hash).find(".comment-hide-button").click(function () {
		        			        	$(this).parent().hide();
		        			        });
		        				} else {
		        					last_comment.find(".comment-wrapper").append('<div style="white-space:pre">' + data.comment + "</div>");
		        					last_comment.css({'background-color': '#FFE'}).slideDown("fast");
		        				};
		        			};
		        	});
	        	};
	          });
		}

		// -----------------------------------------------
		activity_comment($(".tal-render"));
		$(".activity-all-button").hide();
		
		$(this).find(".activity-all-button").click(function (e) {
			e.preventDefault();
			$("#activity-stream > ul.activities > li.activity").slideDown("slow");
			$(".activity-all-button").hide();
		});
		
		$("#astream-tabs").find("li").click(function(){
			$("#astream-tabs").find("li").toggleClass("selected");
			toggle_following_activities();
		})

        // --------------------------- contentViews ------        

        function prepContentViews(){
	        $(".show-preview #content-views").children().click( function() {
	        	var url = $(this).find("a").attr("href");
	        	if (url != undefined) {
	        		window.location = url;
	        	};
	        });
	        $(".show-preview #content-views").children().each(function(){
	        	
	        	var menu_context = $(this).find("a").html();
	        	
	        	$(this).prepend('<div class="content-view-box"></div>');
	        	$(this).find(".content-view-box").html(menu_context).hide();
	        	$(this).find("a").html("");
	        	
	        });
	        
	        $(".show-preview  #content-views").children().hover( function() {
	        	if ( $(this).find(".content-view-box").html().length > 1 ) {         		
	        		$(this).find(".content-view-box").show();
	        	};
	        }, function(){
	        	$(this).find(".content-view-box").hide();
	        });
		}        
        // --------------------------- /contentViews ------
		
		function more_activity_event_handler(){

			$('.linked-document').prepOverlay({
			    subtype: 'ajax',
			    width: "533px",
			    height: "50px",
	   			config: {
	    			onLoad: function(e){prepContentViews()}	
	    		}
			});
			$('.Image').find(".linked-document").prepOverlay({
			    subtype: 'ajax',
			    width: "800px",
			    height: "50px",
	    		config: {
	    			onLoad: function(e){prepContentViews()}	
	    		}
			});

			if ($("#activity-stream").find("li:visible").last().is(":in-viewport")){
				get_more_activities();
			}
			else {
				$("#activity-stream").find("li:visible").last().one('inview', function(event, visible){
					if(visible) {
						$("#spinner").show();
						get_more_activities();
					}
				});
			}
		}
		
		function toggle_following_activities(){
			if($(".astream-tab-all").hasClass("selected"))
			{
				$(".activity").show();
			}
			else if($(".astream-tab-following").hasClass("selected"))
			{
				$(".not-following").hide();
				$(".following").show();
				if($(".following").html() == null)
				{
					get_more_activities();
				}
			}
	
			more_activity_event_handler();
		}

		function get_more_activities() {
			var last_timestamp = $("#activity-stream").find(".activity-text > .timestamp:last").attr("id");
			$(".activities").find(".jq-render").addClass('jq-render-ex').removeClass('jq-render');
			
			$.getJSON(ajax_activities, {
				'action':'get_more_activities', 
				'timestamp': last_timestamp,
                'uid': uid
				},
				function(data) {
					if (data != '') {
						$.cookie('latest_activity_hash', data.hash, { path: '/' });
        				activities = new Array();
        				$.each(data, function(key, val) {
       						activities.push(val);
        				});        				
						$( "#activity-tmpl" ).tmpl( activities ).appendTo( ".activities" ).hide().slideDown(400);        					
						$(".activities").find(".jq-render").addClass('jq-render');
						$(".activities").find(".jq-render").addClass('jq-more-activities');
						$.i18n.setDictionary(eval("astream_language_" + i18n_language));
						$(".activities").children().find(".comment-input-button").text($.i18n._('comment'));
						$(".activities").children().find(".comment-save-button").text($.i18n._('save'));
						$(".activities").children().find(".comment-all-button").text($.i18n._('view_all'));

						if($(".astream-tab-all").hasClass("selected")){
							$(".jq-more-activities")
								.css({'background-color':'#FFFFEE'})
								.delay(2000)
								.fadeTo(2500, 1.0, function() {
										$(".jq-more-activities").css({'background-color':'#FFFFFF'});
										//more_activity_event_handler();
									});
						}
						else if($(".astream-tab-following").hasClass("selected"))
						{
							$(".jq-more-activities, .following")
								.css({'background-color':'#FFFFEE'})
								.delay(2000)
								.fadeTo(2500, 1.0, function() {
										$(".jq-more-activities").css({'background-color':'#FFFFFF'});
										//more_activity_event_handler();
									});
							$(".not-following").hide();							
						}
						activity_comment( $(".jq-more-activities" ) ); 

						};
					$("#spinner").hide();
					if($(".following").length == 0)
					{
						if(!($(".astream-tab-following").hasClass("inactive"))){
							$(".astream-tab-following").addClass("inactive");	
						}
					}
					else
					{
						$(".astream-tab-following").removeClass("inactive");
					}
					more_activity_event_handler();
		    });
		}
		$("#activity-stream").find("li:visible").last().one('inview', function(event, visible){
			if(visible) {
				$("#spinner").show();
				get_more_activities();
			}
		});
		$.cookie('latest-activity-timestamp', $("#activity-stream").find(".timestamp").attr("id") , { path: '/' });
		
        setInterval(function () {
        	var latest_timestamp = $("#activity-stream").find(".timestamp").attr("id");
        	
        	$.getJSON(ajax_activities, {
        					'action':'get_latest_activities', 
        					'timestamp': latest_timestamp,
                            'uid': uid
        					},
        		function(data) {
        			if (data != '') {
        				$(".activities").find(".jq-render").attr('class','jq-render-next');
        				activities = new Array();
        				$.each(data, function(key, val) {
       						activities.push(val);
        				});
       					$( "#activity-tmpl" ).tmpl( activities ).prependTo( ".activities" ).hide().slideDown(400);	
       					$.i18n.setDictionary(eval("astream_language_" + i18n_language));
        				$(".activities").children().find(".comment-input-button").text($.i18n._('comment'));
        				$(".activities").children().find(".comment-save-button").text($.i18n._('save'));
        				$(".activities").children().find(".comment-all-button").text($.i18n._('view_all'));
        				$(".activities").find(".jq-render").addClass('jq-latest-activities');

						$(".jq-latest-activities")
						.css({'background-color':'#FFFFCC'})
						.delay(2000)
						.fadeTo(2000, 1.0, function() {
								$(".jq-latest-activities").css({'background-color':'#FFFFFF'})
							});
        				
        				activity_comment( $(".jq-latest-activities" ) );
        				$.cookie('latest-activity-timestamp', latest_timestamp , { path: '/' });
						if($(".following").length == 0)
						{
							if(!($(".astream-tab-following").hasClass("inactive"))){
								$(".astream-tab-following").addClass("inactive");	
							}
						}
						else
						{
							$(".astream-tab-following").removeClass("inactive");
						}
        			};
	        });       
        	
        }, NOTIFY_ACTIVITIES_REPEAT);
   
		setInterval(function () {
			var ctimestamps = [];     
		    $(".c-timestamp").each(function() { ctimestamps.push($(this).attr('id')  ) });
		    latest_comment_timestamp = ctimestamps.sort().reverse()[0];

			$.getJSON(ajax_activities, {
							'action'	:'get_latest_comments', 
							'timestamp'	: latest_comment_timestamp
							},
				function(data) {
					if (data != '') {
						$.each(data, function(index,value) {
							var place_path = ".activities > li[id=" + value.activity_hash + "] > .activity-wrapper > ul.comments" ;
							var place = $(place_path);
							var latest_comment = place.find(".comment:last");
							var latest_comment_id = latest_comment.attr("id");
							
							if (latest_comment_id != value.hash) {
								$("#activity-comment-tmpl").tmpl(value).appendTo(place_path).css({
									'background-color': '#FFE'
								}).hide().slideDown("slow")
							} else {
								latest_comment.detach();
                                $("#activity-comment-tmpl").tmpl(value).appendTo(place_path).css({
                                    'background-color': '#FFE'
                                })
							};
						});
					};
			});       
			
		}, NOTIFY_COMMENTS_REPEAT);

		$('.linked-document').prepOverlay({
		    subtype: 'ajax',
		    width: "533px",
		    height: "50px",
   			config: {
    			onLoad: function(e){prepContentViews()}	
    		}
		});
		$('.Image').find(".linked-document").prepOverlay({
		    subtype: 'ajax',
		    width: "800px",
		    height: "50px",
    		config: {
    			onLoad: function(e){prepContentViews()}	
    		}
		});
		
		if($(".following").length == 0)
		{
			$(".astream-tab-following").addClass("inactive");
		}
		
		$(document).delegate("a.user-message", "mouseenter", function(){
			thumb = $(this).parent().parent().find(".thumbnail");
			thumb.addClass("hover");
			$(this).mouseleave(function(){
				setTimeout(function(){
				  if(thumb.is(":hover"))
				  {}
				  else
				  {
				  	thumb.removeClass("hover");
				  }
				}, 200);
			})
			thumb.mouseleave(function(){
				thumb.removeClass("hover");
		});
		});
		
        // === END ======================================
    }
); 
*/