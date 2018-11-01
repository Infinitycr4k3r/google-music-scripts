import sys

import click
import google_music
from logzero import logger

from google_music_scripts.__about__ import __title__, __version__
from google_music_scripts.cli import split_filter_strings
from google_music_scripts.config import configure_logging
from google_music_scripts.core import filter_songs


@click.command()
@click.help_option('-h', '--help')
@click.version_option(__version__, '-V', '--version', prog_name=__title__, message="%(prog)s %(version)s")
@click.option('-l', '--log', is_flag=True, default=False, help="Log to file.")
@click.option('-v', '--verbose', count=True)
@click.option('-q', '--quiet', count=True)
@click.option(
	'-u', '--username', metavar='USERNAME', default='',
	help="Your Google username or e-mail address.\nUsed to separate saved credentials."
)
@click.option('--device-id', metavar='ID', help="A mobile device id.")
@click.option(
	'-f', '--include-filter', metavar='FILTER', multiple=True, callback=split_filter_strings,
	help="Metadata filters to match Google songs.\nSongs can match any filter criteria."
)
@click.option(
	'-fa', '--all-includes', is_flag=True, default=False,
	help="Songs must match all include filter criteria to be included."
)
@click.option(
	'-F', '--exclude-filter', metavar='FILTER', multiple=True, callback=split_filter_strings,
	help="Metadata filters to match Google songs.\nSongs can match any filter criteria."
)
@click.option(
	'-Fa', '--all-excludes', is_flag=True, default=False,
	help="Songs must match all exclude filter criteria to be included."
)
@click.option('-y', '--yes', is_flag=True, default=False, help="Display results without asking for confirmation.")
def search(
	log, verbose, quiet, username, device_id, include_filter, all_includes, exclude_filter, all_excludes, yes):
	"""Search a Google Music library for songs."""

	configure_logging(verbose - quiet, log_to_file=log)

	logger.info("Logging in to Google Music")
	mc = google_music.mobileclient(username, device_id=device_id)

	if not mc.is_authenticated:
		sys.exit("Failed to authenticate client.")

	search_results = filter_songs(
		mc.songs(),
		include_filters=include_filter, all_includes=all_includes,
		exclude_filters=exclude_filter, all_excludes=all_excludes
	)

	search_results.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('trackNumber')))

	if search_results:
		result_num = 0
		total = len(search_results)
		pad = len(str(total))

		confirm = yes or input(f"\nDisplay {len(search_results)} results? (y/n) ") in ("y", "Y")

		if confirm:
			for result in search_results:
				result_num += 1

				title = result.get('title', "<empty>")
				artist = result.get('artist', "<empty>")
				album = result.get('album', "<empty>")
				song_id = result['id']

				logger.info(f"{result_num:>{pad}}/{total} {title} -- {artist} -- {album} ({song_id})")
	else:
		logger.info("No songs found matching query")

	mc.logout()
	logger.info("All done!")