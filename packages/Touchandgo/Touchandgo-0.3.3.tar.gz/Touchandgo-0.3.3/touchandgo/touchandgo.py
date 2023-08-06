#! /usr/bin/env python
import argparse

from torrentmediasearcher import TorrentMediaSearcher

from subtitles import get_subtitle
from helpers import execute, daemonize


def watch(name, season=None, episode=None, sub_lang=None, serve=False,
         quality=None, port=None):


    def get_magnet(results):
        print("Processing magnet link")
        magnet = results['magnet']
        command = "peerflix \"%s\"" % magnet
        if sub_lang is not None:
            subtitle = get_subtitle(magnet, sub_lang)
            if subtitle is not None:
                command += " -t %s" % subtitle
        if port is not None:#
            command += " -p%s" % port
        if not serve:
            command += " --vlc"

        print("executing command %s" % command)
        execute(command)

    print("Searching torrent")
    search = TorrentMediaSearcher
    if season is None and episode is None:
        search.request_movie_magnet('torrentproject', name,
                                    callback=get_magnet, quality=quality)
    else:
        if quality is None:
            quality = 'normal'
        search.request_tv_magnet(provider='eztv', show=name,
                                 season=int(season), episode=int(episode),
                                 quality=quality, callback=get_magnet)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")

    parser.add_argument("sea_ep", nargs='*', default=[None, None])
    parser.add_argument("--sub", nargs='?', default=None)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--quality", nargs='?', default=None)
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--port", default="8888")
    parser.add_argument("--season", action="store_true")
    args = parser.parse_args()

    if args.daemon:
        daemonize(args, watch)
    else:
        episode = int(args.sea_ep[1]) if args.sea_ep[1] is not None else None
        play_next_episode = True
        while play_next_episode:
            watch(args.name, season=args.sea_ep[0], episode=episode,
                sub_lang=args.sub, serve=args.serve, quality=args.quality,
                port=args.port)
            episode += 1
            play_next_episode = args.season

if __name__ == '__main__':
    main()
