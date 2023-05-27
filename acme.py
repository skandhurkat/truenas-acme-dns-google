#!/usr/bin/env python

"""Set and unset ACME DNS records for Google Domains."""

import argparse
import logging
import logging.handlers
import os
import sys

import requests

import config

REST_URL = f"https://acmedns.googleapis.com/v1/acmeChallengeSets/{config.domain}:rotateChallenges"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("acme_google_domains")
if os.name == "posix":
    log_handler = logging.handlers.SysLogHandler(address="/dev/log")
    logger.addHandler(log_handler)


def set_acme(args):
    logger.debug(f"SET record with "
                 f"fqdn: {args.fqdn}, "
                 f"digest: {args.digest}, "
                 f"timeout: {args.timeout}")
    logger.info(f"SET requested for {{{args.fqdn}, {args.digest}}}")
    response = requests.post(REST_URL,
                             data={
                                 "accessToken": config.api_key,
                                 "recordsToAdd": [
                                     {
                                         "fqdn": args.fqdn,
                                         "digest": args.digest,
                                     },
                                 ],
                                 "keepExpiredRecords": False,
                             },
                             timeout=args.timeout
                             )
    print(response.text)
    if args.digest in response.text and response.status_code == 200:
        logger.info(f"SET successful with {{{args.fqdn}, {args.digest}}}")
    else:
        logger.error(f"SET unsuccessful with {{{args.fqdn}, {args.digest}}}")
        sys.exit(1)


def unset_acme(args):
    logger.debug(f"UNSET record with "
                 f"fqdn: {args.fqdn}, "
                 f"digest: {args.digest}")
    logger.info(f"UNSET requested for {{{args.fqdn}, {args.digest}}}")
    response = requests.post(REST_URL,
                             data={
                                 "accessToken": config.api_key,
                                 "recordsToRemove": [
                                     {
                                         "fqdn": args.fqdn,
                                         "digest": args.digest,
                                     },
                                 ],
                                 "keepExpiredRecords": False,
                             }
                             )
    print(response.text)
    if args.digest in response.text and response.status_code == 200:
        logger.info(f"UNSET successful with {{{args.fqdn}, {args.digest}}}")
    else:
        logger.error(f"UNSET unsuccessful with {{{args.fqdn}, {args.digest}}}")
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Set and unset ACME DNS records for Google Domains"
    )
    sp = ap.add_subparsers()

    set_ap = sp.add_parser("set")
    set_ap.add_argument("fqdn", type=str)
    set_ap.add_argument("digest", type=str)
    set_ap.add_argument("timeout", type=int, default=60, nargs="?")
    set_ap.set_defaults(func=set_acme)

    unset_ap = sp.add_parser("unset")
    unset_ap.add_argument("fqdn", type=str)
    unset_ap.add_argument("digest", type=str)
    unset_ap.set_defaults(func=unset_acme)

    args = ap.parse_args()
    args.func(args)
