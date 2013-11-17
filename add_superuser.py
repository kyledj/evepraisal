"""Upgrade a current user to a superuser

This can only be run after the first run of the app
"""
import sys
import os
from evepraisal import models
import sqlite3 as sqlite

def main():
    dbpath, openid = sys.argv[1:]

    if not os.path.exists(dbpath):
        print "Database does not exist: " + dbpath
        raise SystemExit

    con = sqlite.connect(dbpath)

    cur = con.execute(
        "UPDATE users SET accesslevel = ? WHERE openid = ?",
        (models.SUPERUSER, openid)
    )

    if cur.rowcount != 1:
        print "No user found for OpenID: " + openid
        raise SystemExit

    con.commit()

    print "Done"


if __name__ == "__main__":
    main()