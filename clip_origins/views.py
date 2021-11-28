from flask import abort, Blueprint, render_template, request
from .scraper import get_clips, get_video_info

views = Blueprint("views", __name__, url_prefix="/")

@views.route('/')
def index():
  return render_template("index.html")

@views.route('/clips')
def clips():
	args = request.args

	video_id = args.get("id")

	if not video_id:
		abort(400)

	# Can be "chrono" or "popular"
	# Default is "chrono"
	sort_type = args.get("sort-type", "chrono")

	# Default is false
	reversed = bool(args.get("reversed"))

	video_info = get_video_info(video_id)
	clips = get_clips(video_id, sort_type=sort_type, reversed=reversed)

	return render_template("clips.html", video=video_info, clips=clips)
