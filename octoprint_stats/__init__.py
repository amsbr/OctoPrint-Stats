# coding=utf-8
from __future__ import absolute_import

__author__ = "Anderson Silva <ams.bra@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2015 Anderson Silva - AGPLv3 License"

import octoprint.plugin
import octoprint.events
from octoprint.server import printer

from flask import jsonify, make_response
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
        db.execute('CREATE TABLE IF NOT EXISTS print_started(event_time DateTime PRIMARY KEY, file Text, origin Text, bed_target Numeric, tool0_target Numeric, tool1_target Numeric)')
        db.execute('CREATE TABLE IF NOT EXISTS print_done(event_time DateTime PRIMARY KEY, file Text, ptime Integer, origin Text, bed_actual Numeric, tool0_actual Numeric, tool1_actual Numeric, tool0_volume Numeric, tool1_volume Numeric, tool0_length Numeric, tool1_length Numeric)')
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
                            GROUP BY 
                                strftime('%Y%m', event_time)
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, COUNT(event_time) disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              disconnected
                            GROUP BY 
                                strftime('%Y%m', event_time)
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
                          GROUP BY 
                                strftime('%Y%m', event_time)
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, COUNT(event_time) print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_cancelled
                            GROUP BY 
                                strftime('%Y%m', event_time)  
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, COUNT(event_time) print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_done
                            GROUP BY 
                                strftime('%Y%m', event_time)
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, COUNT(event_time) print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_failed
                            GROUP BY 
                                strftime('%Y%m', event_time)
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, COUNT(event_time) print_paused, 0 print_resumed, 0 error
                            FROM
                              print_paused
                            GROUP BY 
                                strftime('%Y%m', event_time)
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, COUNT(event_time) print_resumed, 0 error
                            FROM
                              print_resumed
                            GROUP BY 
                                strftime('%Y%m', event_time)
                        UNION
                        SELECT
                          strftime('%Y%m', event_time) month,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, COUNT(event_time) error
                            FROM
                              error
                            GROUP BY 
                                strftime('%Y%m', event_time)
                      ) AS tb
                      WHERE
                        NOT month IS NULL
                      GROUP BY
                        month
                      ORDER BY
                        month DESC''')

        db.execute('''CREATE VIEW IF NOT EXISTS hourstat AS
                      SELECT hour,
                        SUM(connected) connected, SUM(disconnected) disconnected, SUM(upload) upload, SUM(print_started) print_started,
                        SUM(print_cancelled) print_cancelled, SUM(print_done) print_done, SUM(print_failed) print_failed, SUM(print_paused) print_paused, SUM(print_resumed) print_resumed, SUM(error) error
                      FROM (
                        SELECT
                          strftime('%H', event_time) hour,
                          COUNT(event_time) connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              connected
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, COUNT(event_time) disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              disconnected
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, COUNT(event_time) upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              upload
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, COUNT(event_time) print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_started
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, COUNT(event_time) print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_cancelled
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, COUNT(event_time) print_done, 0 print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_done
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, COUNT(event_time) print_failed, 0 print_paused, 0 print_resumed, 0 error
                            FROM
                              print_failed
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, COUNT(event_time) print_paused, 0 print_resumed, 0 error
                        FROM
                          print_paused
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, COUNT(event_time) print_resumed, 0 error
                            FROM
                              print_resumed
                            GROUP BY 
                                strftime('%H', event_time)
                        UNION
                        SELECT
                          strftime('%H', event_time) hour,
                          0 connected, 0 disconnected, 0 upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed, 0 print_paused, 0 print_resumed, COUNT(event_time) error
                            ROM
                              error
                            GROUP BY 
                                strftime('%H', event_time)
                      ) AS tb
                      WHERE
                        NOT hour IS NULL
                      GROUP BY
                        hour''')

        db.execute('''CREATE VIEW IF NOT EXISTS printstat AS
                      SELECT
                        SUM(upload) upload, SUM(print_started) print_started, SUM(print_cancelled) print_cancelled, SUM(print_done) print_done, SUM(print_failed) print_failed
                      FROM (
                        SELECT
                          COUNT(event_time) upload, 0 print_started, 0 print_cancelled, 0 print_done, 0 print_failed
                        FROM
                          upload
                        UNION
                        SELECT
                          0 upload, COUNT(event_time) print_started, 0 print_cancelled, 0 print_done, 0 print_failed
                        FROM
                          print_started
                        UNION
                        SELECT
                          0 upload, 0 print_started, COUNT(event_time) print_cancelled, 0 print_done, 0 print_failed
                        FROM
                          print_cancelled
                        UNION
                        SELECT
                          0 upload, 0 print_started, 0 print_cancelled, COUNT(event_time) print_done, 0 print_failed
                        FROM
                          print_done
                        UNION
                        SELECT
                          0 upload, 0 print_started, 0 print_cancelled, 0 print_done, COUNT(event_time) print_failed
                        FROM
                          print_failed
                      ) AS tb''')

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
                  octoprint.plugin.SimpleApiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.SettingsPlugin):

    def on_after_startup(self):
        self._logger.info("Printer Stats")
        self.statDB = StatsDB(self)

        self.refreshFull()
        self.refreshHour()
        self.refreshPrint()
        self.refreshWatts()

    def get_settings_defaults(self):
        return dict(
          pcbheatbed="98.5",
          hotend="32.5",
          steppermotors="0.6",
          eletronics="11.3"
          )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
        ]

    #def get_template_vars(self):
    #    return dict(month=self.month)

    ##~~ SimpleApiPlugin API

    def is_api_adminonly(self):
        return False

    def on_api_get(self, request):
        self.refreshFull()
        self.refreshHour()
        self.refreshPrint()
        self.refreshWatts()

        return jsonify(dict(
            fullDataset=self.fullDataset,
            hourDataset=self.hourDataset,
            printDataset=self.printDataset,
            dkwhDataset=self.dkwhDataset,
            mkwhDataset=self.mkwhDataset
        ))

    ##~~ AssetPlugin API

    def get_assets(self):
        return dict(
            css=["css/Chart.css"],
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

            month.append(monName)
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

    def refreshHour(self):
        sql = "SELECT hour, connected, disconnected, upload, print_started, print_done, print_failed, print_cancelled, print_paused, print_resumed, error FROM hourstat"
        rows = self.statDB.query(sql)
        hour = list()
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
            hour.append(row[0])
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

        self.hourDataset = {'hour': hour, 'connected': connected, 'disconnected': disconnected,
            'upload': upload, 'print_started': print_started, 'print_done': print_done, 'print_failed': print_failed,
            'print_cancelled': print_cancelled, 'print_paused': print_paused, 'print_resumed': print_resumed, 'error': error}
        self._plugin_manager.send_plugin_message(self._identifier, dict(hourDataset=self.hourDataset))

    def refreshPrint(self):
        sql = "SELECT upload, print_started, print_done, print_failed, print_cancelled FROM printstat"
        rows = self.statDB.query(sql)
        upload = list()
        print_started = list()
        print_done = list()
        print_failed = list()
        print_cancelled = list()

        for row in rows:
            upload.append(int(row[0]))
            print_started.append(int(row[1]))
            print_done.append(int(row[2]))
            print_failed.append(int(row[3]))
            print_cancelled.append(int(row[4]))

        self.printDataset = {'upload': upload, 'print_started': print_started, 'print_done': print_done,
            'print_failed': print_failed, 'print_cancelled': print_cancelled}
        self._plugin_manager.send_plugin_message(self._identifier, dict(printDataset=self.printDataset))

    def refreshWatts(self):
        pcbheatbed = float(self._settings.get(["pcbheatbed"]))
        hotend = float(self._settings.get(["hotend"]))
        steppermotors = float(self._settings.get(["steppermotors"]))
        eletronics = float(self._settings.get(["eletronics"]))

        total = pcbheatbed + hotend + steppermotors + eletronics

        sql = "SELECT strftime('%Y-%m-%d', event_time) day, (SUM(ptime) / 60 / 60) phour FROM print_done GROUP BY strftime('%Y-%m-%d', event_time) ORDER BY event_time DESC LIMIT 7"
        rows = self.statDB.query(sql)
        day = list()
        phour = list()
        kwh = list()

        for row in rows:
            day.append(row[0])
            phour.append(round(row[1], 3))
            kwh.append(round((float(row[1]) * float(total)) / 1000, 3))

        self.dkwhDataset = {'day': day, 'phour': phour, 'kwh': kwh}
        self._plugin_manager.send_plugin_message(self._identifier, dict(dkwhDataset=self.dkwhDataset))

        sql = "SELECT strftime('%Y%m', event_time) month, (SUM(ptime) / 60 / 60) phour FROM print_done GROUP BY strftime('%Y%m', event_time) ORDER BY event_time DESC LIMIT 7"
        rows = self.statDB.query(sql)
        month = list()
        phour = list()
        kwh = list()

        for row in rows:
            mon = row[0]
            monName = calendar.month_name[int(mon[4:6])]

            month.append(monName[0:3])
            phour.append(round(row[1], 3))
            kwh.append(round((float(row[1]) * float(total)) / 1000, 3))

        self.mkwhDataset = {'month': month, 'phour': phour, 'kwh': kwh}
        self._plugin_manager.send_plugin_message(self._identifier, dict(mkwhDataset=self.mkwhDataset))

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
            bed_target = 0
            tool0_target = 0
            tool1_target = 0

            from octoprint.server import printer
            if printer is not None:
                temps = printer.get_current_temperatures()
                if "bed" in temps:
                    bed_target = temps["bed"]["target"]
                if "tool0" in temps:
                    tool0_target = temps["tool0"]["target"]
                if "tool1" in temps:
                    tool1_target = temps["tool1"]["target"]

            sql = "INSERT INTO print_started (event_time, file, origin, bed_target, tool0_target, tool1_target) VALUES ('%s', '%s', '%s', %f, %f, %f)" % (datetime.datetime.today(), file, origin, bed_target, tool0_target, tool1_target)

        if event == octoprint.events.Events.PRINT_DONE:
            file = os.path.basename(payload["file"])
            ptime = payload["time"]
            origin = payload["origin"]
            bed_actual = 0
            tool0_actual = 0
            tool1_actual = 0
            tool0_volume = 0
            tool1_volume = 0
            tool0_length = 0
            tool1_length = 0

            from octoprint.server import printer
            if printer is not None:
                temps = printer.get_current_temperatures()
                if "bed" in temps:
                    bed_actual = temps["bed"]["actual"]
                if "tool0" in temps:
                    tool0_actual = temps["tool0"]["actual"]
                if "tool1" in temps:
                    tool1_actual = temps["tool1"]["actual"]

            try:
                printData = self._file_manager.get_metadata(origin, file)
            except:
                printData = None

            if printData is not None:
                if "analysis" in printData:
                    if "filament" in printData["analysis"] and "tool0" in printData["analysis"]["filament"]:
                        tool0_volume = printData["analysis"]["filament"]["tool0"]["volume"]
                        tool0_length = printData["analysis"]["filament"]["tool0"]['length']
                    if "filament" in printData["analysis"] and "tool1" in printData["analysis"]["filament"]:
                        tool1_volume = printData["analysis"]["filament"]["tool1"]["volume"]
                        tool1_length = printData["analysis"]["filament"]["tool1"]['length']

            sql = "INSERT INTO print_done (event_time, file, ptime, origin, bed_actual, tool0_actual, tool1_actual, tool0_volume, tool1_volume, tool0_length, tool1_length) VALUES ('%s', '%s', '%s', '%s', %f, %f, %f, %f, %f, %f, %f)" % (datetime.datetime.today(), file, ptime, origin, bed_actual, tool0_actual, tool1_actual, tool0_volume, tool1_volume, tool0_length, tool1_length)

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
            self.refreshHour()
            self.refreshPrint()
            self.refreshWatts()

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            stats=dict(
                displayName="Printer Stats",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="amsbr",
                repo="OctoPrint-Stats",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/amsbr/OctoPrint-Stats/archive/{target_version}.zip"
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Printer Stats"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Statistics of your 3D Printer"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = StatsPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
