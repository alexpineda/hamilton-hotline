<html>
	<head>
	<meta charset="utf-8">
  <title>Hamilton Hotline</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Call in with your opinion">
  <meta name="author" content="@alexpineda77 @andrewCHML">

  <!-- Le styles -->
  <link href="/css/bootstrap.css" rel="stylesheet">
  <link href="/css/twitter.css" rel="stylesheet">

	<style type="text/css">
        body {
          padding-top: 20px;
          padding-bottom: 40px;
        }

        /* Custom container */
        .container-narrow {
          margin: 0 auto;
          max-width: 700px;
        }
        .container-narrow > hr {
          margin: 30px 0;
        }

        /* Main marketing message and sign up button */
        .jumbotron {
          margin: 60px 0;
          text-align: center;
        }
        .jumbotron h1 {
          font-size: 72px;
          line-height: 1;
        }
        .jumbotron .btn {
          font-size: 21px;
          padding: 14px 24px;
        }

        .recordings {
          margin: 60px 0;
        }
        .recordings p + h4 {
          margin-top: 28px;
        }
		
		.scrubber {
            width:70% !important;
        }
		
		.audiojs {
			width:100%;
			border-radius:10px 10px 0 0;
		}
		
		.zero-left-margin {
			margin-left:0;
		}
		
      </style>

	</head>
  <body>

  <!--img src="http://i.imgur.com/aFxwO.jpg" width="100%" /-->

<div class="container-narrow">

      <div class="masthead">
        <ul class="nav nav-pills pull-right">
        {% if not user  %}
          <li class="active"><a id='signin-nav' href="#signin-modal" data-toggle="modal" >Sign in</a></li>
          <li ><a id='#signup-nav' href="#signup-modal" data-toggle="modal" >Sign Up With Email</a></li>
        {% else %}
          <li><a class='not-yet-implemented' href="/logout">Logout</a></li>
        {% endif %}
        </ul>

      </div>

      <hr>


      <div class="jumbotron">
        <h1>Hamilton Hotline</h1>
		<h2>(905) 581-0686</h2>

		<div class="alert alert-block" style='margin-top:20px;'>
		  <button type="button" class="close" data-dismiss="alert">&times;</button>
		  <h4>Active Channels</h4>
			<div class="stream btn" >Create Your Own..</div>
			<div class="stream btn" id="stream_casino" data-toggle="buttons-checkbox"><h4>Casino</h4><p>PunchCode: 42235#</p></div>
			<div class="stream btn" id="stream_restaurants_in_the_city" data-toggle="buttons-checkbox"><h4>Restaurants In The City</h4><p>PunchCode: 55432#</p></div>
			<div class="stream btn" id="stream_complaints_for_city_hall" data-toggle="buttons-checkbox"><h4>Complaints for City Hall</h4><p>PunchCode: 11111#</p></div>
			<div class="stream btn" id="stream_ticats" data-toggle="buttons-checkbox"><h4>TiCats</h4><p>PunchCode: 81166#</p></div>
		</div>
		
      </div>

      <hr>

      <div class="row-fluid recordings" id='recordings'>
        {% include "recordings.tpl" %}
      </div>

      <div class="row-fluid profile" style='display:none'>
        <div class="span12">
        <form class='form' name="user-profile-form" action="/req-verify-phone" method="POST">
          <p>Screen Name: {{ user.screenName }}</p>
          <label>Phone Number (eg. 905 555-5555): <input name="phone" value="{{ user.phoneNumber|default_if_none:'905 555-5555' }}" /> </label>
          <input type='submit' value='Submit Phone Verification' >
        </form>

        </div>
      </div>
      <hr>

      <div id="signup-modal" class="modal hide fade">
      <form class="form" id='signup-form'>
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h3>Sign up with Email</h3>
        </div>
        <div class="modal-body">
            <label>Email: <input type="text" name='email'/></label>
			<label>Screen Name (optional): <input type="text" name='screenName'/></label>
            <p>Signing up is easy</p>
        </div>
        <div class="modal-footer">
          <a href="#" class="btn btn-primary" >Sign Me Up!</a>
        </div>
        </form>
      </div>

	<div id="signup-complete-modal" class="modal hide fade">
      <form class="form" id='signup-form'>
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h3>Hey You!</h3>
        </div>
        <div class="modal-body">
            <p>You'll recieve a confirmation email shortly!</p>
        </div>
        <div class="modal-footer">
			<a href="#" class="btn btn-primary">Thanks!</a>
        </div>
        </form>
      </div>

	  
      <div id="signin-modal" class="modal hide fade">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h3>Hey Welcome !</h3>
        </div>
        <div class="modal-body">
          <label>Email: <input type="text" name='email'/></label>
		  <label>Password: <input type="password" name='password'/></label>
        </div>
        <div class="modal-footer">
          <a href="#" class="btn">Close</a>
          <a href="#" class="btn btn-primary">Sign In</a>
        </div>
      </div>

      <div class="footer">
        <p>© Alex Pineda 2013</p>
          <ul><li><a href="http://twitter.com/alexpineda77" target="_blank">@alexpineda77</a></li>
              <li><a href="http://twitter.com/andrewCHML" target="_blank">@andrewCHML</a></li></ul>
      </div>

    </div>
      <!-- Le javascript
      ================================================== -->
      <!-- Placed at the end of the document so the pages load faster -->

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js" ></script>
    <script src="/js/bootstrap.js"></script>
    <script src="/js/audiojs/audiojs/audio.min.js"></script>
    <!--script src="/js/twitter_marquee.js"></script-->
    <!--script src="/js/ember-1.0.0-pre.4.js"></script-->
	<script src="/js/underscore.js" ></script>
	<script src="/js/backbone.js"></script>
    <script src="//platform.twitter.com/widgets.js"></script><!-- for twitter status display widget -->
    <script>

    $(document).ready(function() {
      {% if user and not user.beenSetup %}
        hamont.open_profile();
      {% else %}
		
		$('.transcription-tabs').each(function(){
			var twitterTab = $(this).find('li').first();
			if (twitterTab.hasClass('disabled')){
				twitterTab = twitterTab.next();
			}
			twitterTab.children().first().tab('show');
			
		});
		
		$('.not-yet-implemented').click(function(){
			$('.alert').show();
		});
		
		$('#signup-modal .btn-primary').click(function(){
			$('#signup-modal').submit();
		});
	{% endif %}
	
	window.TwitterMarquee.init();
    });
    hamont = {}
    hamont.open_profile = function(){
      $('.recordings').hide();
      $('.profile').show();
    };
    hamont.close_profile = function(){
      $('.profile').hide();
      $('.recordings').show();
    };



    hamont.get_latest = function(){
      if (!hamont.get_latest_is_ready || $('.playing').length > 0)
        return;
      hamont.get_latest_is_ready = false;
      $.get('/get-latest',
            {
              timestamp : $('#recordings').children().first().find('.recording-title').data('timestamp'),
			  autoplay : true
            },
            function (resp){
              if (resp){
                var recordings = $('<div></div>').html(resp).find('.recording').css('display','none');
				        $(recordings).prependTo($('#recordings'));

                $(recordings).slideDown(400, function(){
                  audiojs.createAll({},$(recordings).find('audio').get());
				  $(recordings).find('.transcription-tabs').each(function(){
						var twitterTab = $(this).find('li').first();
						if (twitterTab.hasClass('disabled')){
							twitterTab = twitterTab.next();
						}
						twitterTab.children().first().tab('show');
						
					});
                  hamont.get_latest_is_ready = true;

                })
              } else {
                hamont.get_latest_is_ready = true;
              }
            })
        .fail(function(){ hamont.get_latest_is_ready = true; });
    };
	
  $(window).scroll(function(){
	return;//disabled for now
	  if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
		console.log('scroll threshhold');
		  if (!hamont.get_more_is_ready)
			return;
			
		  hamont.get_more_is_ready = false;
		  $.get('/get-more',
				{
				  timestamp : "2013-01-20 01:05:11:801920"//$('#recordings').children().first().find('.recording-title').data('timestamp')
				},
				function (resp){
				  if (resp){
					var recordings = $('<div></div>').html(resp).find('.recording').css('display','none');
							$(recordings).appendTo($('#recordings'));

					$(recordings).slideDown(400, function(){
					  audiojs.createAll({},$(recordings).find('audio').get());
					  $(recordings).find('.transcription-tabs').each(function(){
							var twitterTab = $(this).find('li').first();
							if (twitterTab.hasClass('disabled')){
								twitterTab = twitterTab.next();
							}
							twitterTab.children().first().tab('show');
							
						});
					  hamont.get_more_is_ready = true;

					})
				  } else {
					hamont.get_more_is_ready = true;
				  }
				})
			.fail(function(){ hamont.get_more_is_ready = true; });

      }
    });

    $('#signup-nav').click(function(){
      $('#signup-model').modal();
    });

      audiojs.events.ready(function() {
        audiojs.createAll();
		hamont.get_more_is_ready = true;
		hamont.get_latest_is_ready = true;
      });

	
	$('.respond-button').each(function(){
		$(this).popover({
			placement:'bottom',
			trigger:'hover',
			title:'How to respond to this call',
			html:true,
			content:'<p>Call Hamilton Hotline (905) 581-0686 and punch in ' + $(this).data('punchcode') + ' to respond to this call.</p>'
		});
	});
	
	$('.favorites-button').each(function(){
		$(this).popover({
			placement:'bottom',
			trigger:'hover',
			title:'Add to favorites',
			html:true,
			content:'<p>You need to sign in to add to favorites.</p>'
		});
	});
	
		$('.share-button').each(function(){
		$(this).popover({
			placement:'bottom',
			trigger:'hover',
			title:'Share this call',
			html:true,
			content:'<p>Share to Twitter Friendz, Faceb00k friends, Reddit Friendz ... soon.</p>'
		});
	});

    window.setInterval(hamont.get_latest, 5000);
    </script>
	
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-37964185-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>

    </body>

</html>