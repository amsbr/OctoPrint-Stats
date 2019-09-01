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
from tinydb import TinyDB, Query, where
import pandas as pd

class StatsDB:
    def __init__(self, plugin):
        self.DB_NAME_V1 = plugin._settings.global_get_basefolder("logs") + "/octoprint_stats.db"
        self.DB_NAME = plugin._settings.global_get_basefolder("logs") + "/octoprint_stats.json"
        
        if os.path.exists(self.DB_NAME_V1) == True:
            self.migrate_v1()
        
    def migrate_v1(self):
        conn = sqlite3.connect(self.DB_NAME_V1)
        db = conn.cursor()

        dbnew = TinyDB(self.DB_NAME)
        events = dbnew.table('events')

        # Migrate connected
        sql = "SELECT event_time, port, baudrate FROM connected"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            port = row[1]
            baudrate = row[2]
            
            eventData = {'event_type': 'CONNECTED', 
                         'data': {'event_time': event_time.__str__(), 'port': port, 'baudrate': baudrate}}
                        
            events.insert(eventData)

        # Migrate disconnected
        sql = "SELECT event_time FROM disconnected"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            
            eventData = {'event_type': 'DISCONNECTED', 
                         'data': {'event_time': event_time.__str__()}}
                        
            events.insert(eventData)
            
        # Migrate upload
        sql = "SELECT event_time, file, target FROM upload"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            target = row[2]
            
            eventData = {'event_type': 'UPLOAD', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'target': target}}
                        
            events.insert(eventData)

        # Migrate print_started
        sql = "SELECT event_time, file, origin, bed_target, tool0_target, tool1_target FROM print_started"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]
            bed_target = row[3]
            tool0_target = row[4]
            tool1_target = row[5]
            
            eventData = {'event_type': 'PRINT_STARTED', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'target': target}}
                        
            events.insert(eventData)
        
        # Migrate print_done
        sql = "SELECT event_time, file, ptime, origin, bed_actual, tool0_actual, tool1_actual, tool0_volume, tool1_volume, tool0_length, tool1_length FROM print_done"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            ptime = row[2]
            origin = row[3]
            bed_actual = row[4]
            tool0_actual = row[5]
            tool1_actual = row[6]
            tool0_volume = row[7]
            tool1_volume = row[8]
            tool0_length = row[9]
            tool1_length = row[10]

            eventData = {'event_type': 'PRINT_DONE', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'ptime': ptime, 'origin': origin, 'bed_actual': bed_actual, 'tool0_actual': tool0_actual, 'tool1_actual': tool1_actual, 'tool0_volume': tool0_volume, 'tool1_volume': tool1_volume, 'tool0_length': tool0_length, 'tool1_length': tool1_length}}
                        
            events.insert(eventData)

        # Migrate print_failed
        sql = "SELECT event_time, file, origin FROM print_failed"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_FAILED', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'origin': origin}}
                        
            events.insert(eventData)

        # Migrate print_cancelled
        sql = "SELECT event_time, file, origin FROM print_cancelled"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_CANCELLED', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'origin': origin}}
                        
            events.insert(eventData)
      
        # Migrate print_paused
        sql = "SELECT event_time, file, origin FROM print_paused"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_PAUSED', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'origin': origin}}
                        
            events.insert(eventData)
      
        # Migrate print_resumed
        sql = "SELECT event_time, file, origin FROM print_resumed"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_RESUMED', 
                         'data': {'event_time': event_time.__str__(), 'file': file, 'origin': origin}}
                        
            events.insert(eventData)

        # Migrate error
        sql = "SELECT event_time, perror FROM error"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            perror = row[1]

            eventData = {'event_type': 'ERROR', 
                         'data': {'event_time': event_time.__str__(), 'error': perror}}
                        
            events.insert(eventData)
            
        os.rename(self.DB_NAME_V1, self.DB_NAME_V1 + ".bak")

    def execute(self, data, document):
        # DB
        db = TinyDB(self.DB_NAME)
        doc = db.table(document)
        doc.insert(data)
    
    def query(self, search_data, document):
        # DB
        db = TinyDB(self.DB_NAME)
        doc = db.table(document)
        return doc.search(search_data)

    def count(self, search_data, document):
        # DB
        db = TinyDB(self.DB_NAME)
        doc = db.table(document)
        return doc.count(search_data)
      
    def getData(self, data):
        resData = []
        
        for row in data:
            resData.append(row["data"])
            
        return resData


class StatsPlugin(octoprint.plugin.EventHandlerPlugin,
                  octoprint.plugin.StartupPlugin,
                  octoprint.plugin.AssetPlugin,
                  octoprint.plugin.SimpleApiPlugin,
                  octoprint.plugin.TemplatePlugin,
                  octoprint.plugin.SettingsPlugin):

    def on_after_startup(self):
        self._logger.info("Printer Stats")
        self.current_filter = 'current_year'
        self.statDB = StatsDB(self)

        self.fullDataset = []
        self.hourDataset = []
        self.dayDataset = []
        self.printDataset = []
        self.timeDataset = []
        self.dkwhDataset = []
        self.mkwhDataset = []
        self.todayPrintDataset = []
        self.todayStatDataset = []
        self.todaykWhDataset = []

        self.refreshFull(filter_param=self.current_filter)
        self.refreshHour(filter_param=self.current_filter)
        self.refreshDay(filter_param=self.current_filter)
        self.refreshPrint(filter_param=self.current_filter)
        self.refreshTime(filter_param=self.current_filter)
        self.refreshWatts(filter_param=self.current_filter)

        self.refreshSidePrint()
        self.refreshSideDay()
        self.refreshSidekWh()

    def get_settings_defaults(self):
        return dict(
          pcbheatbed="98.5",
          hotend="32.5",
          steppermotors="0.6",
          eletronics="11.3",
          daystats=False,
          daykwh=False,
          dayprint=False
          )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False),
            dict(type="sidebar", name="Stats", icon="line-chart")
        ]

    #def get_template_vars(self):
    #    return dict(month=self.month)

    ##~~ SimpleApiPlugin API

    def is_api_adminonly(self):
        return False

    def on_api_get(self, request):
        if (request.args.get('type') == "reset"):
            os.remove(self.statDB.DB_NAME)
        elif (request.args.get('type') == "side"):
            self.refreshSidePrint()
            self.refreshSideDay()
            self.refreshSidekWh()

            if hasattr(self, 'todayPrintDataset'):
                return jsonify(dict(
                    todayPrintDataset=self.todayPrintDataset,
                    todayStatDataset=self.todayStatDataset,
                    todaykWhDataset=self.todaykWhDataset
                ))
            else:
                return jsonify(dict())
        else:
            self.current_filter = request.args.get('filter')
            self.refreshFull(filter_param=self.current_filter)
            self.refreshHour(filter_param=self.current_filter)
            self.refreshDay(filter_param=self.current_filter)
            self.refreshPrint(filter_param=self.current_filter)
            self.refreshTime(filter_param=self.current_filter)
            self.refreshWatts(filter_param=self.current_filter)

            self.refreshSidePrint()
            self.refreshSideDay()
            self.refreshSidekWh()
            
            if hasattr(self, 'fullDataset'):
                return jsonify(dict(
                    fullDataset=self.fullDataset,
                    hourDataset=self.hourDataset,
                    dayDataset=self.dayDataset,
                    printDataset=self.printDataset,
                    timeDataset=self.timeDataset,
                    dkwhDataset=self.dkwhDataset,
                    mkwhDataset=self.mkwhDataset,
                    todayPrintDataset=self.todayPrintDataset,
                    todayStatDataset=self.todayStatDataset,
                    todaykWhDataset=self.todaykWhDataset
                ))
            else:
                return jsonify(dict())

    ##~~ AssetPlugin API

    def get_assets(self):
        return dict(
            css=["css/Chart.min.css"],
            js=["js/stats.js", "js/Chart.min.js"]
        )

    def parseYear(self, x):
        try:
            parse = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y")
        except Exception:
            parse = ""
        return parse

    def parseYearMonth(self, x):
        try:
            parse = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m")
        except Exception:
            parse = ""
        return parse

    def parseYearMonthDay(self, x):
        try:
            parse = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d")
        except Exception:
            parse = ""
        return parse

    def parseYearMonthDayHour(self, x):
        try:
            parse = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H")
        except Exception:
            parse = ""
        return parse

    def parseHour(self, x):
        try:
            parse = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime("%H")
        except Exception:
            parse = ""
        return parse

    def parseDay(self, x):
        try:
            parse = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").strftime("%A")
        except Exception:
            parse = ""
        return parse

    def calcKwh(self, x, total):
        try:
            calc = round(((float(x) / 60 / 60) * float(total)) / 1000, 3)
        except Exception:
            calc = 0
            
        return calc

    def filterEvent(self, event, group, filterp = 'current_year'):
        search = Query()

        search_data = (search.event_type == event)
        event_data = self.statDB.getData(self.statDB.query(search_data, 'events'))
        event_df = pd.DataFrame(event_data)
        if(event_data != []):
            event_df["event_y"] = event_df["event_time"].apply(self.parseYear)
            event_df["event_ym"] = event_df["event_time"].apply(self.parseYearMonth)
            event_df["event_ymd"] = event_df["event_time"].apply(self.parseYearMonthDay)
            #if (group == "y"):
                #event_df["event_y"] = event_df["event_time"].apply(self.parseYear)
            #elif (group == "ym"):
                #event_df["event_y"] = event_df["event_time"].apply(self.parseYear)
                #event_df["event_ym"] = event_df["event_time"].apply(self.parseYearMonth)
            #if (group == "ymd"):
                #event_df["event_ymd"] = event_df["event_time"].apply(self.parseYearMonthDay)
            if (group == "ymdh"):
                event_df["event_ymdh"] = event_df["event_time"].apply(self.parseYearMonthDayHour)
            elif (group == "h"):
                event_df["event_h"] = event_df["event_time"].apply(self.parseHour)
            elif (group == "d"):
                event_df["event_d"] = event_df["event_time"].apply(self.parseDay)

            event_df["event_type"] = event

            if filterp == 'current_year':
                event_df = event_df[event_df.event_y == datetime.datetime.today().strftime("%Y")]
            elif filterp == 'current_month':
                event_df = event_df[event_df.event_ym == datetime.datetime.today().strftime("%Y-%m")]
            elif filterp == 'last_month':
                event_df = event_df[event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(1 * 365 / 12)).strftime("%Y-%m")]
            elif filterp == 'last3_month':
                event_df = event_df[(event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(1 * 365 / 12)).strftime("%Y-%m")) | 
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(2 * 365 / 12)).strftime("%Y-%m")) |
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(3 * 365 / 12)).strftime("%Y-%m"))]
            elif filterp == 'last6_month':
                event_df = event_df[(event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(1 * 365 / 12)).strftime("%Y-%m")) | 
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(2 * 365 / 12)).strftime("%Y-%m")) |
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(3 * 365 / 12)).strftime("%Y-%m")) |
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(4 * 365 / 12)).strftime("%Y-%m")) |
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(5 * 365 / 12)).strftime("%Y-%m")) |
                                    (event_df.event_ym == (datetime.datetime.today() - datetime.timedelta(6 * 365 / 12)).strftime("%Y-%m"))]
            elif filterp == 'last_year':
                event_df = event_df[event_df.event_y == str(datetime.datetime.today().year - 1)]
            elif filterp == 'last3_year':
                event_df = event_df[(event_df.event_y == str(datetime.datetime.today().year - 1)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 2)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 3))]
            elif filterp == 'last6_year':
                event_df = event_df[(event_df.event_y == str(datetime.datetime.today().year - 1)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 2)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 3)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 4)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 5)) |
                                    (event_df.event_y == str(datetime.datetime.today().year - 6))]
            elif filterp == 'today':
                event_df = event_df[(event_df.event_ymd == datetime.datetime.today().strftime("%Y-%m-%d"))]
                    
        return event_df
    
    def refreshFull(self, filter_param='current_year'):
        # Count connected
        connected = self.filterEvent("CONNECTED", group = "ym", filterp=filter_param)

        # Count disconnected
        disconnected = self.filterEvent("DISCONNECTED", group = "ym", filterp=filter_param)

        # Count upload
        upload_count = self.filterEvent("UPLOAD", group = "ym", filterp=filter_param)

        # Count print_started
        print_started_count = self.filterEvent("PRINT_STARTED", group = "ym", filterp=filter_param)

        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "ym", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ym", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ym", filterp=filter_param)

        # Count print_paused
        print_paused_count = self.filterEvent("PRINT_PAUSED", group = "ym", filterp=filter_param)

        # Count print_resumed
        print_resumed_count = self.filterEvent("PRINT_RESUMED", group = "ym", filterp=filter_param)

        # Count error
        error_count = self.filterEvent("ERROR", group = "ym", filterp=filter_param)

        full_df = pd.concat([connected, disconnected, upload_count, print_started_count, print_done_count,
                             print_failed_count, print_cancelled_count, print_paused_count, print_resumed_count, error_count], sort=False)
    
        if full_df.empty != True:
            full_df_count = full_df.groupby("event_ym")["event_type"].value_counts().unstack().fillna(0)
                
            self.fullDataset = full_df_count.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(fullDataset=self.fullDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(fullDataset=[]))

    def refreshHour(self, filter_param='current_year'):
        # Count connected
        connected = self.filterEvent("CONNECTED", group = "h", filterp=filter_param)

        # Count disconnected
        disconnected = self.filterEvent("DISCONNECTED", group = "h", filterp=filter_param)

        # Count upload
        upload_count = self.filterEvent("UPLOAD", group = "h", filterp=filter_param)

        # Count print_started
        print_started_count = self.filterEvent("PRINT_STARTED", group = "h", filterp=filter_param)

        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "h", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "h", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "h", filterp=filter_param)

        # Count print_paused
        print_paused_count = self.filterEvent("PRINT_PAUSED", group = "h", filterp=filter_param)

        # Count print_resumed
        print_resumed_count = self.filterEvent("PRINT_RESUMED", group = "h", filterp=filter_param)

        # Count error
        error_count = self.filterEvent("ERROR", group = "h", filterp=filter_param)

        hour_df = pd.concat([connected, disconnected, upload_count, print_started_count, print_done_count,
                             print_failed_count, print_cancelled_count, print_paused_count, print_resumed_count, error_count], sort=False)

        if hour_df.empty != True:
            hour_df_count = hour_df.groupby("event_h")["event_type"].value_counts().unstack().fillna(0)

            self.hourDataset = hour_df_count.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(hourDataset=self.hourDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(hourDataset=[]))

    def refreshDay(self, filter_param='current_year'):
        # Count connected
        connected = self.filterEvent("CONNECTED", group = "d", filterp=filter_param)

        # Count disconnected
        disconnected = self.filterEvent("DISCONNECTED", group = "d", filterp=filter_param)

        # Count upload
        upload_count = self.filterEvent("UPLOAD", group = "d", filterp=filter_param)

        # Count print_started
        print_started_count = self.filterEvent("PRINT_STARTED", group = "d", filterp=filter_param)

        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "d", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "d", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "d", filterp=filter_param)

        # Count print_paused
        print_paused_count = self.filterEvent("PRINT_PAUSED", group = "d", filterp=filter_param)

        # Count print_resumed
        print_resumed_count = self.filterEvent("PRINT_RESUMED", group = "d", filterp=filter_param)

        # Count error
        error_count = self.filterEvent("ERROR", group = "d", filterp=filter_param)

        day_df = pd.concat([connected, disconnected, upload_count, print_started_count, print_done_count,
                             print_failed_count, print_cancelled_count, print_paused_count, print_resumed_count, error_count], sort=False)

        if day_df.empty != True:
            day_df_count = day_df.groupby("event_d")["event_type"].value_counts().unstack().fillna(0)

            self.dayDataset = day_df_count.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(dayDataset=self.dayDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(dayDataset=[]))

    def refreshPrint(self, filter_param='current_year'):
        # Count upload
        upload_count = self.filterEvent("UPLOAD", group = "ev", filterp=filter_param)

        # Count print_started
        print_started_count = self.filterEvent("PRINT_STARTED", group = "ev", filterp=filter_param)

        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "ev", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ev", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ev", filterp=filter_param)

        print_df = pd.concat([upload_count, print_started_count, print_done_count,
                             print_failed_count, print_cancelled_count], sort=False)

        if print_df.empty != True:
            print_df_count = print_df["event_type"].value_counts()

            self.printDataset = print_df_count.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(printDataset=self.printDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(printDataset=[]))

    def refreshTime(self, filter_param='current_year'):
        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "ev", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ev", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ev", filterp=filter_param)

        print_df = pd.concat([print_done_count,
                             print_failed_count, print_cancelled_count], sort=False)

        if print_df.empty != True:
            print_df_sum = print_df.groupby("event_type")["ptime"].sum()

            self.timeDataset = print_df_sum.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(timeDataset=self.timeDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(timeDataset=[]))

    def refreshWatts(self, filter_param='current_year'):
        pcbheatbed = float(self._settings.get(["pcbheatbed"]))
        hotend = float(self._settings.get(["hotend"]))
        steppermotors = float(self._settings.get(["steppermotors"]))
        eletronics = float(self._settings.get(["eletronics"]))

        total = pcbheatbed + hotend + steppermotors + eletronics

        # Day kWh
        
        # Count print_done 
        print_done_count = self.filterEvent("PRINT_DONE", group = "ymd", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ymd", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ymd", filterp=filter_param)

        print_df = pd.concat([print_done_count,
                             print_failed_count, print_cancelled_count], sort=False)

        if print_df.empty != True:
            print_df["kwh"] = print_df["ptime"].apply(self.calcKwh, total=total)
            print_df_sum = print_df.groupby("event_ymd")["kwh", "ptime"].sum()

            self.dkwhDataset = print_df_sum.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(dkwhDataset=self.dkwhDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(dkwhDataset=[]))

        # Month kWh
        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "ym", filterp=filter_param)

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ym", filterp=filter_param)

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ym", filterp=filter_param)

        print_df = pd.concat([print_done_count,
                             print_failed_count, print_cancelled_count], sort=False)

        if print_df.empty != True:
            print_df["kwh"] = print_df["ptime"].apply(self.calcKwh, total=total)
            print_df_sum = print_df.groupby("event_ym")["kwh", "ptime"].sum()

            self.mkwhDataset = print_df_sum.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(mkwhDataset=self.mkwhDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(mkwhDataset=[]))

    def refreshSidePrint(self):
        # Count upload
        upload_count = self.filterEvent("UPLOAD", group = "ev", filterp='today')

        # Count print_started
        print_started_count = self.filterEvent("PRINT_STARTED", group = "ev", filterp='today')

        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "ev", filterp='today')

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ev", filterp='today')

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ev", filterp='today')

        print_df = pd.concat([upload_count, print_started_count, print_done_count,
                             print_failed_count, print_cancelled_count], sort=False)

        if print_df.empty != True:
            print_df_count = print_df["event_type"].value_counts()

            self.todayPrintDataset = print_df_count.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(todayPrintDataset=self.todayPrintDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(todayPrintDataset=[]))

    def refreshSideDay(self):
        # Count connected
        connected = self.filterEvent("CONNECTED", group = "ev", filterp="today")

        # Count disconnected
        disconnected = self.filterEvent("DISCONNECTED", group = "ev", filterp="today")

        # Count upload
        upload_count = self.filterEvent("UPLOAD", group = "ev", filterp="today")

        # Count print_started
        print_started_count = self.filterEvent("PRINT_STARTED", group = "ev", filterp="today")

        # Count print_done
        print_done_count = self.filterEvent("PRINT_DONE", group = "ev", filterp="today")

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "ev", filterp="today")

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "ev", filterp="today")

        # Count print_paused
        print_paused_count = self.filterEvent("PRINT_PAUSED", group = "ev", filterp="today")

        # Count print_resumed
        print_resumed_count = self.filterEvent("PRINT_RESUMED", group = "ev", filterp="today")

        # Count error
        error_count = self.filterEvent("ERROR", group = "ev", filterp="today")

        print_df = pd.concat([connected, disconnected, upload_count, print_started_count, print_done_count,
                             print_failed_count, print_cancelled_count, print_paused_count, print_resumed_count, error_count], sort=False)

        if print_df.empty != True:
            print_df_count = print_df["event_type"].value_counts()

            self.todayStatDataset = print_df_count.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(todayStatDataset=self.todayStatDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(todayStatDataset=[]))

    def refreshSidekWh(self):
        pcbheatbed = float(self._settings.get(["pcbheatbed"]))
        hotend = float(self._settings.get(["hotend"]))
        steppermotors = float(self._settings.get(["steppermotors"]))
        eletronics = float(self._settings.get(["eletronics"]))

        total = pcbheatbed + hotend + steppermotors + eletronics

        # Day kWh
        
        # Count print_done 
        print_done_count = self.filterEvent("PRINT_DONE", group = "h", filterp='today')

        # Count print_failed
        print_failed_count = self.filterEvent("PRINT_FAILED", group = "h", filterp='today')

        # Count print_cancelled
        print_cancelled_count = self.filterEvent("PRINT_CANCELLED", group = "h", filterp='today')

        print_df = pd.concat([print_done_count,
                             print_failed_count, print_cancelled_count], sort=False)

        if print_df.empty != True:
            print_df["kwh"] = print_df["ptime"].apply(self.calcKwh, total=total)
            print_df_sum = print_df.groupby("event_h")["kwh", "ptime"].sum()

            self.todaykWhDataset = print_df_sum.to_json(orient='index')
            self._plugin_manager.send_plugin_message(self._identifier, dict(todaykWhDataset=self.todaykWhDataset))
        else:
            self._plugin_manager.send_plugin_message(self._identifier, dict(todaykWhDataset=[]))

    def on_event(self, event, payload):
        """
        Callback for general OctoPrint events.
        """
        
        eventData = None
        if event == octoprint.events.Events.CONNECTED:
            port = payload["port"]
            baudrate = payload["baudrate"]
            eventData = {'event_type': 'CONNECTED', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'port': port, 'baudrate': baudrate}}

        if event == octoprint.events.Events.DISCONNECTED:
            eventData = {'event_type': 'DISCONNECTED', 
                         'data': {'event_time': datetime.datetime.today().__str__()}}

        if event == octoprint.events.Events.UPLOAD:
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            target = payload["target"]
            name = payload["name"]
            eventData = {'event_type': 'UPLOAD', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'target': target, 'name': name}}

        if event == octoprint.events.Events.PRINT_STARTED:
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            name = payload["name"]
            origin = payload["origin"]
            size = payload["size"]
            owner = payload["owner"]
            user = payload["user"]
            bed_target = 0
            tool0_target = 0
            tool1_target = 0
            tool2_target = 0

            from octoprint.server import printer
            if printer is not None:
                temps = printer.get_current_temperatures()
                if "bed" in temps:
                    bed_target = temps["bed"]["target"]
                if "tool0" in temps:
                    tool0_target = temps["tool0"]["target"]
                if "tool1" in temps:
                    tool1_target = temps["tool1"]["target"]
                if "tool2" in temps:
                    tool2_target = temps["tool2"]["target"]

            eventData = {'event_type': 'PRINT_STARTED', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'origin': origin, 'bed_target': bed_target, 'tool0_target': tool0_target, 'tool1_target': tool1_target, 'tool2_target': tool2_target, 'size': size, 'owner': owner, 'user': user, 'name': name}}

        if event == octoprint.events.Events.PRINT_DONE:
            name = payload['name']
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            ptime = payload["time"]
            origin = payload["origin"]
            size = payload["size"]
            owner = payload["owner"]
            bed_actual = 0
            tool0_actual = 0
            tool1_actual = 0
            tool2_actual = 0
            tool0_volume = 0
            tool1_volume = 0
            tool2_volume = 0
            tool0_length = 0
            tool1_length = 0
            tool2_length = 0

            from octoprint.server import printer
            if printer is not None:
                temps = printer.get_current_temperatures()
                if "bed" in temps:
                    bed_actual = temps["bed"]["actual"]
                if "tool0" in temps:
                    tool0_actual = temps["tool0"]["actual"]
                if "tool1" in temps:
                    tool1_actual = temps["tool1"]["actual"]
                if "tool2" in temps:
                    tool2_actual = temps["tool2"]["actual"]

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
                    if "filament" in printData["analysis"] and "tool2" in printData["analysis"]["filament"]:
                        tool2_volume = printData["analysis"]["filament"]["tool2"]["volume"]
                        tool2_length = printData["analysis"]["filament"]["tool2"]['length']

            eventData = {'event_type': 'PRINT_DONE', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'ptime': ptime, 'origin': origin, 'bed_actual': bed_actual, 'tool0_actual': tool0_actual, 'tool1_actual': tool1_actual, 'tool2_actual': tool2_actual, 'tool0_volume': tool0_volume, 'tool1_volume': tool1_volume, 'tool2_volume': tool2_volume, 'tool0_length': tool0_length, 'tool1_length': tool1_length, 'tool2_length': tool2_length, 'name': name, 'size': size, 'owner': owner}}

        if event == octoprint.events.Events.PRINT_FAILED:
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            origin = payload["origin"]
            name = payload['name']
            size = payload['size']
            owner = payload['owner']
            ptime = payload['time']
            reason = payload['reason']

            eventData = {'event_type': 'PRINT_FAILED', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'origin': origin, 'name': name, 'size': size, 'owner': owner, 'ptime': ptime, 'reason': reason}}

        if event == octoprint.events.Events.PRINT_CANCELLED:
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            origin = payload["origin"]
            name = payload["name"]
            size = payload["size"]
            owner = payload["owner"]
            user = payload["user"]
            ptime = payload["time"]

            eventData = {'event_type': 'PRINT_CANCELLED', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'origin': origin, 'name': name, 'size': size, 'owner': owner, 'user': user, 'ptime': ptime}}

        if event == octoprint.events.Events.PRINT_PAUSED:
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            origin = payload["origin"]
            name = payload["name"]
            size = payload["size"]
            owner = payload["owner"]
            user = payload["user"]

            eventData = {'event_type': 'PRINT_PAUSED', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'origin': origin, 'name': name, 'size': size, 'owner': owner, 'user': user}}

        if event == octoprint.events.Events.PRINT_RESUMED:
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""
            origin = payload["origin"]
            name = payload["name"]
            size = payload["size"]
            owner = payload["owner"]
            user = payload["user"]

            eventData = {'event_type': 'PRINT_RESUMED', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'file': file, 'origin': origin, 'name': name, 'size': size, 'owner': owner, 'user': user}}

        if event == octoprint.events.Events.ERROR:
            perror = payload["error"]

            eventData = {'event_type': 'ERROR', 
                         'data': {'event_time': datetime.datetime.today().__str__(), 'error': perror}}

        if eventData != None:
            self.statDB.execute(eventData, 'events')
            
            self.refreshFull(filter_param=self.current_filter)
            self.refreshHour(filter_param=self.current_filter)
            self.refreshDay(filter_param=self.current_filter)
            self.refreshPrint(filter_param=self.current_filter)
            self.refreshTime(filter_param=self.current_filter)
            self.refreshWatts(filter_param=self.current_filter)
            
            # Side
            self.refreshSidePrint()
            self.refreshSideDay()
            self.refreshSidekWh()

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
__plugin_version__ = "2.0.0"
__plugin_description__ = "Statistics of your 3D Printer"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = StatsPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
