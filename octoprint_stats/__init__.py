# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint.events

import os.path
import datetime
import calendar
import sqlite3

class StatsDB:
    def __init__(self, plugin):
        self.DB_NAME = plugin._settings.global_get_basefolder("logs") + "/octoprint_stats.db"

        # DB
        conn = sqlite3.connect(self.DB_NAME)
        db = conn.cursor()

        db.execute('CREATE TABLE IF NOT EXISTS connected(event_time DateTime PRIMARY KEY, port Text, baudrate Text)')
        db.execute('CREATE TABLE IF NOT EXISTS disconnected(event_time DateTime PRIMARY KEY)')
        db.execute('CREATE TABLE IF NOT EXISTS upload(event_time DateTime PRIMARY KEY, file Text, target Text)')
        db.execute('CREATE TABLE IF NOT EXISTS print_started(event_time DateTime PRIMARY KEY, file Text, origin Text)')
        db.execute('CREATE TABLE IF NOT EXISTS print_done(event_time DateTime PRIMARY KEY, file Text, ptime Integer, origin Text)')
        db.execute('CREATE TABLE IF NOT EXISTS print_failed(event_time DateTime PRIMARY KEY, file Text, origin Text)')
        db.execute('CREATE TABLE IF NOT EXISTS print_cancelled(event_time DateTime PRIMARY KEY, file Text, origin Text)')
        db.execute('CREATE TABLE IF NOT EXISTS print_paused(event_time DateTime PRIMARY KEY, file Text, origin Text)')
        db.execute('CREATE TABLE IF NOT EXISTS print_resumed(event_time DateTime PRIMARY KEY, file Text, origin Text)')
        db.execute('CREATE TABLE IF NOT EXISTS error(event_time DateTime PRIMARY KEY, perror Text)')
        db.execute('''CREATE VIEW IF NOT EXISTS fullstat AS
                      SELECT month,
                        SUM(connected) connected, SUM(disconnected) disconnected, SUM(upload) upload, SUM(print_started) print_started,
                        SUM(print_cancelled) print_cancelled, SUM(print_done) print_done, SUM(print_failed) print_failed, SUM(print_paused) print_paused, SUM(print_resumed) print_resumed, SUM(error) error
                      FROM (
                        SELECT
                          strftime('%Y%m', event_time) month,
                          COUNT(event_time) connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          connected
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, COUNT(event_time) disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          disconnected
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, COUNT(event_time) upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          upload
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, COUNT(event_time) print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          print_started
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, COUNT(event_time) print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          print_cancelled
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, COUNT(event_time) print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          print_done
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, COUNT(event_time) print_failed, 0 print_paused, 0 print_resumed, 0 error
                        FROM
                          print_failed
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, COUNT(event_time) print_paused, 0 print_resumed, 0 error
                        FROM
                          print_paused
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, COUNT(event_time) print_resumed, 0 error
                        FROM
                          print_resumed
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, COUNT(event_time) error
                        FROM
                          error
                      ) AS tb
                      WHERE
                        NOT month IS NULL
                      GROUP BY
                        month
                      ORDER BY
                        month DESC''')
        conn.commit()
        conn.close()

    def execute(self, sql):
        conn = sqlite3.connect(self.DB_NAME)
        db = conn.cursor()

        db.execute(sql)
        conn.commit()
        conn.close()

    def query(self, sql):
        conn = sqlite3.connect(self.DB_NAME)
        db = conn.cursor()

        db.execute(sql)
        return db.fetchall()


class StatsPlugin(octoprint.plugin.EventHandlerPlugin,
                  octoprint.plugin.StartupPlugin,
                  octoprint.plugin.AssetPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.SettingsPlugin):

    def on_after_startup(self):
        self._logger.info("Printer Stats")
        self.statDB = StatsDB(self)

        self.refreshFull()

    def get_settings_defaults(self):
        return dict(url="http://www.google.com.br")

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
        ]

    def get_assets(self):
        return dict(
            js=["js/stats.js", "js/Chart.js"]
        )

    def refreshFull(self):
        sql = "SELECT month, connected, disconnected, upload, print_started, print_done, print_failed, print_cancelled, print_paused, print_resumed, error FROM fullstat LIMIT 3"
        rows = self.statDB.query(sql)
        month = list()
        connected = list()
        disconnected = list()
        upload = list()
        print_started = list()
        print_done = list()
        print_failed = list()
        print_cancelled = list()
        print_paused = list()
        print_resumed = list()
        error = list()

        for row in rows:
            mon = row[0]
            monName = calendar.month_name[int(mon[4:6])]

            month.append(monName[0:3])
            connected.append(int(row[1]))
            disconnected.append(int(row[2]))
            upload.append(int(row[3]))
            print_started.append(int(row[4]))
            print_done.append(int(row[5]))
            print_failed.append(int(row[6]))
            print_cancelled.append(int(row[7]))
            print_paused.append(int(row[8]))
            print_resumed.append(int(row[9]))
            error.append(int(row[10]))

        self.fullDataset = {'month': month, 'connected': connected, 'disconnected': disconnected,
            'upload': upload, 'print_started': print_started, 'print_done': print_done, 'print_failed': print_failed,
            'print_cancelled': print_cancelled, 'print_paused': print_paused, 'print_resumed': print_resumed, 'error': error}
        self._plugin_manager.send_plugin_message(self._identifier, dict(fullDataset=self.fullDataset))


    def on_event(self, event, payload):
        """
        Callback for general OctoPrint events.
        """
        sql = ""
        if event == octoprint.events.Events.CONNECTED:
            port = payload["port"]
            baudrate = payload["baudrate"]
            sql = "INSERT INTO connected (event_time, port, baudrate) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), port, baudrate)

        if event == octoprint.events.Events.DISCONNECTED:
            sql = "INSERT INTO disconnected (event_time) VALUES ('%s')" % (datetime.datetime.today())

        if event == octoprint.events.Events.UPLOAD:
            file = os.path.basename(payload["file"])
            target = payload["target"]
            sql = "INSERT INTO upload (event_time, file, target) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), file, target)

        if event == octoprint.events.Events.PRINT_STARTED:
            file = os.path.basename(payload["file"])
            origin = payload["origin"]
            sql = "INSERT INTO print_started (event_time, file, origin) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), file, origin)

        if event == octoprint.events.Events.PRINT_DONE:
            file = os.path.basename(payload["file"])
            ptime = payload["time"]
            origin = payload["origin"]
            sql = "INSERT INTO print_done (event_time, file, ptime, origin) VALUES ('%s', '%s', '%s', '%s')" % (datetime.datetime.today(), file, ptime, origin)

        if event == octoprint.events.Events.PRINT_FAILED:
            file = os.path.basename(payload["file"])
            origin = payload["origin"]
            sql = "INSERT INTO print_failed (event_time, file, origin) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), file, origin)

        if event == octoprint.events.Events.PRINT_CANCELLED:
            file = os.path.basename(payload["file"])
            origin = payload["origin"]
            sql = "INSERT INTO print_cancelled (event_time, file, origin) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), file, origin)

        if event == octoprint.events.Events.PRINT_PAUSED:
            file = os.path.basename(payload["file"])
            origin = payload["origin"]
            sql = "INSERT INTO print_paused (event_time, file, origin) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), file, origin)

        if event == octoprint.events.Events.PRINT_RESUMED:
            file = os.path.basename(payload["file"])
            origin = payload["origin"]
            sql = "INSERT INTO print_resumed (event_time, file, origin) VALUES ('%s', '%s', '%s')" % (datetime.datetime.today(), file, origin)

        if event == octoprint.events.Events.ERROR:
            perror = payload["error"]
            sql = "INSERT INTO error (event_time, perror) VALUES ('%s', '%s')" % (datetime.datetime.today(), perror)

        if sql != '':
            self.statDB.execute(sql)
            self.refreshFull()


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Printer Stats"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = StatsPlugin()

    # global __plugin_hooks__
    # __plugin_hooks__ = {
    #    "some.octoprint.hook": __plugin_implementation__.some_hook_handler
    # }
