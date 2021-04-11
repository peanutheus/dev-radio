"""
Handles parsing of podcasts
"""
from collections import namedtuple

import click
import feedparser
from prettytable import PrettyTable, ALL
from src.player import player
import requests
from requests import ConnectionError


podcast_urls = {
    'stackoverflow': 'https://feeds.simplecast.com/XA_851k3',
    'real_python': 'https://realpython.com/podcasts/rpp/feed',
    'python_bytes': 'https://pythonbytes.fm/episodes/rss_full_history',
    'talk_python': 'https://talkpython.fm/episodes/rss_full_history',
    'data_engineering': 'https://www.dataengineeringpodcast.com/feed/mp3/',
    'test_n_code': 'https://feeds.fireside.fm/testandcode/rss',
    'profitable_python': 'https://anchor.fm/s/c8df638/podcast/rss',
    'teaching_python': 'https://feeds.fireside.fm/teachingpython/rss',
    'python_podcast': 'https://www.pythonpodcast.com/feed/mp3/'
}
# FIXME: something is wrong with profitable python, play the episodes for other podcasts as well.


def read_podcasts():
    # MAYBE: maybe make podcast in file?
    return podcast_urls


def print_via_pager(data, data_len):
    """
    A utility pager function, because click.echo_via_pager() is broken for pretty_tables.
    Prints until data_len is 0 and then quits.

    :param data_len: length of data.
    :param data: data to be printed.
    :return:
    """
    # Defines the starting step for each paging print
    paging_start_step = 0

    # Defines how many elements are printed at a time.
    paging_step = 50
    pager_quit_control = None
    while pager_quit_control != 'q' and data_len > 0:
        click.echo(data.get_string(start=paging_start_step, end=paging_start_step+paging_step))
        paging_start_step += paging_step
        data_len -= paging_step
        click.echo("Press ENTER for more, q to quit.")
        pager_quit_control = click.getchar().lower()


def podcast_extractor(podcast_name):
    """
    Returns a list of namedtuple(Episode) with id, episode title, episode number, and stream url.

    :param podcast_name: rss feed link for the podcast.
    :return: [Episode(['id', 'episode_title', 'episode_number', 'date', 'stream_url'])]
    """
    podcast_link = read_podcasts().get(podcast_name)
    if podcast_link:
        try:
            requests.get(podcast_link)
        except ConnectionError:
            print("Either you are offline or the site is ...")
        except requests.exceptions.RequestException as e:
            print(e)
            print("Something went wrong, when accessing podcast ...")
        else:
            all_episodes = []
            Episode = namedtuple('Episode', ['id', 'episode_title', 'episode_number', 'date', 'stream_url'])

            rss_feed = feedparser.parse(podcast_link)
            episode_entries = rss_feed.entries
            for index, episode_item in enumerate(episode_entries):
                all_episodes.append(
                    Episode(id=index,
                            episode_title=episode_item.get('title', 'NULL'),
                            episode_number=episode_item.get('itunes_episode', 'NULL'),
                            date=' '.join(episode_item.get('published', 'NULL').split()[:-2]),
                            stream_url=episode_item.links[-1].get('href', 'NULL')
                            )
                )

            return all_episodes
    else:
        print("Incorrect podcast name, try again.")


def cli_print_episodes(podcast_name):
    """
    CLI facing function to pretty print the episode data.

    :param podcast_name:  podcast name from podcast dict.
    :return:
    """
    # FIXME: check the column width and other formatting issues for other podcasts.
    click.echo("Wait a few seconds ...")
    episode_list = podcast_extractor(podcast_name)
    if episode_list:
        pretty_table = PrettyTable()
        pretty_table.field_names = ['id', 'Title', 'Episode', 'Date', 'Url']
        pretty_table.add_rows(episode_list)
        pretty_table.hrules = ALL

        pretty_table.fields = ['id', 'Title', 'Episode']
        episodes_len = len(episode_list)
        print_via_pager(pretty_table, episodes_len)


def cli_podcast_list():
    """
    CLI facing function to pretty print all available podcast name.

    :return:
    """
    pretty_table = PrettyTable()
    pretty_table.hrules = ALL
    pretty_table.field_names = ["id", "Podcast Name"]
    podcast_list = read_podcasts()
    podcast_list = [(index, podcast) for index, podcast in enumerate(podcast_list, start=0)]
    pretty_table.add_rows(podcast_list)
    click.echo(pretty_table)


def cli_podcast_play(podcast_name, episode_id):
    """
    CLI facing function to play the podcast episode, when passed podcast name and episode id, (NOT episode number).

    :param podcast_name: name of the podcast.
    :param episode_id: id(index) of episode.
    :return:
    """
    episode = None
    episode_list = podcast_extractor(podcast_name)
    if episode_list:
        try:
            episode = episode_list[episode_id]
        except IndexError:
            print("Episode id is incorrect")
        except Exception as e:
            print(e)
            print("Something went wrong, when getting podcast episode data to play.")
        else:
            print(f"Episode:: {episode.episode_number} ->> Title:: {episode.episode_title}\nDate:: {episode.date}")
            player(episode.stream_url)


if __name__ == '__main__':
    cli_podcast_list()
