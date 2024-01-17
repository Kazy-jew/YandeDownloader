#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date as date_, timedelta


def date_range_list(year, begin: str, end: str):
    """
    :param year:
    :param begin:
    :param end:
    :return: [month-date,..., month-date] form list, closed interval
    """
    begin_date = date_(int(f'{year}'), int(begin.split("-")[0]), int(begin.split("-")[-1]))
    end_date = date_(int(f'{year}'), int(end.split("-")[0]), int(end.split("-")[-1]))
    delta = end_date - begin_date
    date_list = []
    for i in range(delta.days + 1):
        date_list.append(str(begin_date + timedelta(days=i)))
    date_list = [_.replace(f'{year}-', '') for _ in date_list]
    return date_list


class Calendar:
    def __init__(self, year):
        """
        :param year: download year
        """
        super().__init__()
        self.form = 'date'
        self.year = year
        self.date_list = []
        self.full_date_list = []
        self.grouped_date_list = []

    def date_range(self, date_range):
        """
        :param date_range: (date(year, month1, date1), date(year, month2, date2))
        :return: [month-date,..., month-date] form list, closed interval
        """
        begin, end = date_range[0], date_range[-1]
        delta = end - begin
        full_date_list = []
        for i in range(delta.days+1):
            full_date_list.append(str(begin+timedelta(days=i)))
        date_list = [_.replace(f'{self.year}-', '') for _ in full_date_list]
        return date_list

    def date_range_between(self, begin: str, end: str):
        """
        :param begin:
        :param end:
        :return: [month-date,..., month-date] form list, closed interval
        """
        begin_date = date_(int(f'{self.year}'), int(begin.split("-")[0]), int(begin.split("-")[-1]))
        end_date = date_(int(f'{self.year}'), int(end.split("-")[0]), int(end.split("-")[-1]))
        delta = end_date - begin_date
        date_list = []
        for i in range(delta.days+1):
            date_list.append(str(begin_date+timedelta(days=i)))
        date_list = [_.replace(f'{self.year}-', '') for _ in date_list]
        return date_list

    def grouper(self, interval=1):
        """
        group generated date list by month, default interval=1, i.e, date list from 1/4 to 3/2 will be grouped
        into three sub lists [['01-01',...,'01-31'], ['02-01',...,'02-28'], ['03-01','03-02']]
        if set interval to 2, the list will be [['01-01',...,...,'02-28'], ['03-01','03-02']], etc
        """
        if not self.date_list:
            self.input_dates()
        dates = self.date_list
        month_begin = int(dates[0][:2])
        month_end = int(dates[-1][:2])
        index = 0
        for i in range(month_begin, month_end+1, interval):
            grouped_date_list = [x for x in self.date_list if i <= int(x[:2]) < i + interval]
            self.grouped_date_list.insert(index, grouped_date_list)
            index += 1
        return self.grouped_date_list

    def date_format(self, month_str1, day_str1, month_str2, day_str2):
        """
        format date to datetime type
        :param month_str1: month 1
        :param day_str1: day 1
        :param month_str2: month 2
        :param day_str2: day 2
        :return: date_range: (date(year, month1, date1), date(year, month2, date2))
        """
        date_begin = date_(int(f'{self.year}'), int(f'{month_str1:>02}'), int(f'{day_str1:>02}'))
        date_end = date_(int(f'{self.year}'), int(f'{month_str2:>02}'), int(f'{day_str2:>02}'))
        return date_begin, date_end

    def date_range_list(self, date_in):
        """
        generate dates list between range (YYYY-M1-D1, YYYY-M2-D2) and write to text.
        :param date_in:
        :return:
        """
        if len(date_in) == 1:
            date_in = date_in[0].split('-')
            if len(date_in) == 1:
                self.form = 'month'
                if int(date_in[0]) != 12:
                    date_list = self.date_range(self.date_format(date_in[0], 1, int(date_in[0])+1, 1))
                    self.date_list = date_list[:-1]
                else:
                    self.date_list = self.date_range(self.date_format(date_in[0], 1, date_in[0], 31))
            else:
                if int(date_in[1]) != 12:
                    date_list = self.date_range(self.date_format(date_in[0], 1, int(date_in[1]) + 1, 1))
                    self.date_list = date_list[:-1]
                else:
                    self.date_list = self.date_range(self.date_format(date_in[0], 1, date_in[1], 31))
        elif len(date_in) == 2:
            self.date_list = self.date_range(self.date_format(date_in[0], date_in[1], date_in[0], date_in[1]))
        elif len(date_in) == 3:
            self.date_list = self.date_range(self.date_format(date_in[0], date_in[1], date_in[0], date_in[2]))
        elif len(date_in) == 4:
            self.date_list = self.date_range(self.date_format(date_in[0], date_in[1], date_in[2], date_in[3]))
        # print(self.date_list)
        return self.date_list

    def input_dates(self):
        """
        :return: date range list
        """
        x = 1
        date_in = []
        while x:
            try:
                date_in = input('please input a date range\n'
                                '[m | m/d | m-m | m/d/d | m/d/m/d]:\n').split('/')
                if len(date_in) > 4 or len(date_in) < 1:
                    print('Invalid Form!\nERROR: format error')
                    continue
                elif len(date_in) == 4:
                    try:
                        date_(self.year, int(date_in[0]), int(date_in[1]))
                        date_(self.year, int(date_in[2]), int(date_in[3]))
                        x = 0
                    except ValueError as e:
                        print(f'Invalid Form!\nERROR: {e}')
                        continue
                elif len(date_in) == 3:
                    try:
                        date_(self.year, int(date_in[0]), int(date_in[1]))
                        date_(self.year, int(date_in[0]), int(date_in[2]))
                        x = 0
                    except ValueError as e:
                        print(f'Invalid Form!\nERROR: {e}')
                        continue
                elif len(date_in) == 2:
                    try:
                        date_(self.year, int(date_in[0]), int(date_in[-1]))
                        x = 0
                    except ValueError as e:
                        print(f'Invalid Form!\nERROR: {e}')
                        continue
                elif len(date_in) == 1:
                    _date_in = date_in[0].split('-')
                    if len(_date_in) == 1:
                        try:
                            date_(self.year, int(_date_in[0]), 1)
                            x = 0
                        except ValueError as e:
                            print(f'Invalid Form!\nERROR: {e}')
                            continue
                    elif len(_date_in) == 2:
                        try:
                            date_(self.year, int(_date_in[0]), 1)
                            date_(self.year, int(_date_in[1]), 1)
                            x = 0
                        except ValueError as e:
                            print(f'Invalid Form!\nERROR: {e}')
                            continue
                    else:
                        continue
            except KeyboardInterrupt:
                raise SystemExit(-1)
        return self.date_range_list(date_in)


if __name__ == "__main__":
    cld = Calendar(2022)
    cld.input_dates()
