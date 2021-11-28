from requests import Session, HTTPError
from typing import Dict, Any

JSONObject = Dict[str, Any]

class GraphQLException(Exception):
    pass

session = Session()
session.headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"}

# VOD URL format: https://www.twitch.tv/videos/1214580885?t=00h00m04s

QUERY = '''
query VideoInfo($id: ID!) {
	video(id: $id) {
		title
		id
		owner {
			login
			displayName
		}
	}
}

query InitialClips($id: ID!) {
	video(id: $id) {
		clips {
			...ClipInfo
		}
	}
}

query PaginateClips($id: ID!, $after: Cursor) {
	video(id: $id) {
		clips(after: $after) {
			...ClipInfo
		}
	}
}

fragment ClipInfo on ClipConnection {
	edges {
		cursor
		node {
			title
			id
			url
			embedURL
			videoOffsetSeconds
			viewCount
		}
	}
	pageInfo {
		hasNextPage
	}
}
'''

def gql_request(operation: str, variables: JSONObject = {}) -> JSONObject:
	url = "https://gql.twitch.tv/gql"
	body = {
		"query": QUERY,
		"operationName": operation,
		"variables": variables,
	}

	res = session.post(
		url,
		json=body,
	)

	try:
		res.raise_for_status()
	except HTTPError as e:
		raise GraphQLException from e

	body: Dict[str, Any] = res.json()

	errors = body.get("errors")
	if errors:
		raise GraphQLException(f"GQL error: {errors}")

	return res.json()["data"]

def get_video_info(video_id: int) -> JSONObject:
	return gql_request("VideoInfo", {"id": video_id})["video"]

def get_last_cursor(connection: JSONObject) -> str:
	return connection["edges"][-1]["cursor"]

def get_has_next_page(connection: JSONObject) -> bool:
	return connection["pageInfo"]["hasNextPage"]

def get_clips_from_edges(connection: JSONObject):
	return map(lambda edge: edge["node"], connection["edges"])

def create_formatted_timestamp(video_offset_seconds: int) -> str:
	MINUTE = 60
	HOUR = MINUTE * 60
	hours = str(video_offset_seconds // HOUR)
	minutes = str((video_offset_seconds % HOUR) // MINUTE)
	seconds = str(video_offset_seconds % MINUTE)
	return f"{hours.zfill(2)}h{minutes.zfill(2)}m{seconds.zfill(2)}s"

def clips_generator(video_id: int):
	# Get initial connection
	connection = gql_request(
		"InitialClips", {"id": video_id}
	)["video"]["clips"]

	yield from get_clips_from_edges(connection)

	has_next_page = get_has_next_page(connection)

	while has_next_page:
		cursor = get_last_cursor(connection)
		connection = gql_request(
                	"PaginateClips", {"id": video_id, "after": cursor}
        	)["video"]["clips"]

		yield from get_clips_from_edges(connection)

		has_next_page = get_has_next_page(connection)

def get_clips(video_id: int, sort_type: str = "chrono", reversed: bool = False):
	if sort_type == "chrono":
		index = "videoOffsetSeconds"
	elif sort_type == "popular":
		index = "viewCount"
	else:
		raise TypeError(
			f"Argument `sort_type` can only be strings 'chrono' or 'popular'; got {sort_type}."
		)

	clips = sorted(clips_generator(video_id), key=lambda clip: clip[index], reverse=reversed)

	for clip in clips:
		clip["formatted_timestamp"] = create_formatted_timestamp(clip["videoOffsetSeconds"])

	return clips
