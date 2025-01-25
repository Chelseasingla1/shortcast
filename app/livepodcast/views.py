# Create the podcast blueprint
from flask import Blueprint, render_template

# Create the Blueprint for live podcast
live_podcast = Blueprint(
    'live_podcast',
    __name__,
    template_folder='templates',
    static_folder='static/livepodcast/static'
)

# Register your live podcast route using the route decorator
@live_podcast.route('/live')
def live_podcast_route():
    return render_template('livepodcast/index.html')
