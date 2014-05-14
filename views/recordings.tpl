{% for recording in recordings %}
      <div class="span12 recording">
          <div class="span12 zero-left-margin">
  				<h4 class='recording-title' data-timestamp='{{ recording.unix_time}}'>Caller "{{ recording.screenName|default:"Anonymous" }}" on {{ recording.date }}</h4>

            <div class="audiojs" classname="audiojs" id="audiojs_wrapper{{ forloop.counter }}" >
				{% if forloop.first and allow_auto_play %}
					<audio src="{{ recording.mp3 }}" autoplay></audio>
				{% else %}
					<audio src="{{ recording.mp3 }}" preload="none"></audio>
				{% endif %}
				<div class="play-pause">
					<p class="play"></p>
					<p class="pause"></p>
					<p class="loading"></p>
					<p class="error"></p>
				</div>
				<div class="scrubber">
					<div class="progress"></div>
					<div class="loaded"></div>
				</div>
				<div class="time">
					<em class="played">00:00</em>/<strong class="duration">00:00</strong>
				</div>
				<div class="error-message"></div>
			</div>
			<button class='btn respond-button' data-id='{{ forloop.counter }}' data-punchcode='{{ recording.punchcode }}' style='float:right'>Respond</button>
			<button class='btn favorites-button' data-id='{{ forloop.counter }}' style='float:right'>Favorites</button>
			<!--button class='btn share-button' data-id='{{ forloop.counter }}' style='float:right'>Share</button-->
		</div>

		  <!--div class="span12">
			<div class="tabbable tabs-left">
			<ul class='nav nav-tabs transcription-tabs'>
				{% if recording.twitter.id %}
				<li>
				{% else %}
				<li class='disabled'>
				{% endif %}
					<a href="#{{ forloop.counter }}-tweeted" class="tweeted-tab" data-toggle='tab'>Tweeted</a>
				</li>

				<li>
					<a href="#{{ forloop.counter }}-transcribed" class="transcribed-tab" data-toggle='tab'>Transcribed</a>
				</li>
			</ul>

			<div class='tab-content'>
				<div class='tab-pane' id='{{ forloop.counter }}-tweeted' >
					<p>{{ recording.twitter.text|default_if_none:"No twitter status is available." }}</p>
				</div>
				<div class='tab-pane' id='{{ forloop.counter }}-transcribed' >
					<p>{{ recording.transcription|default_if_none:"No transcription available." }}</p>
				</div>

			</div>
			</div>
		  </div-->
	  </div>
      {% endfor %}