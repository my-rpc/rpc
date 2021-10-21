import pandas as pd
import numpy as np
import os

class Attendance:

    def __init__(self, month, year, day=8.5, file_format='xlsx', path_att=''):
        self.month = str(month)
        self.year = str(year)
        self.path_att = os.path.join(f"./rpc_package" + path_att)
        self.file_format = file_format
        self.filename = '{}_{}.{}'.format(self.month, self.year, self.file_format)
        # self.path_att = 'static/files/attendance/input/att_{}'.format(self.filename)
        self.path_report = 'static/files/attendance/output/report_{}'.format(self.filename)
        self.names = []
        self.date_m = []
        self.col2_change = {"Date": 'Date M'}

    def read_excel(self):
        self.data = pd.read_excel(self.path_att, engine='xlrd')

    def get_holidays(self):
        pass

    def drop_cols(self):
        self.data.drop(columns=["AC-No.", "No.",
                                'Auto-Assign', "Timetable",
                                "Normal", "Real time",
                                "OT Time", "Must C/In",
                                "Must C/Out", "Department",
                                "Exception", "WeekEnd_OT",
                                "NDays_OT", "Holiday_OT",
                                "ATT_Time", "Holiday",
                                "WeekEnd"], inplace=True)

    def change_col_name(self):
        pass

    def get_leave_daily(self):
        pass

    def get_leave_hourly(self):
        pass

    def get_date_shamsi(self):
        self.date_m = self.data.Date.unique()


    def get_emp_id(self):
        self.names = self.data.Name.unique()


# if __name__ == '__main__':
#     att_obj = Attendance('sonbola', 1400, path_att='')
#     att_obj.read_excel()
#     att_obj.drop_cols()

#     print("end")
