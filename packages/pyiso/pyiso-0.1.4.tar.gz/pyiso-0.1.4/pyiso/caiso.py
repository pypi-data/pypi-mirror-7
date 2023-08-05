from datetime import datetime, timedelta, time
from pyiso.base import BaseClient
import copy
import re
from bs4 import BeautifulSoup


class CAISOClient(BaseClient):
    def __init__(self):
        self.NAME = 'CAISO'
        
        self.base_url_oasis = 'http://oasis.caiso.com/oasisapi/SingleZip'
        self.base_url_gen = 'http://content.caiso.com/green/renewrpt/'
        self.base_url_outlook = 'http://content.caiso.com/outlook/SP/'
        self.base_payload = {'version': 1}
        self.oasis_request_time_format = '%Y%m%dT%H:%M-0000'
        
        self.TZ_NAME = 'America/Los_Angeles'
        
        self.fuels = {
            'GEOTHERMAL': 'geo',
            'BIOMASS': 'biomass',
            'BIOGAS': 'biogas',
            'SMALL HYDRO': 'smhydro',
            'WIND TOTAL': 'wind',
            'SOLAR': 'solar',
            'SOLAR PV': 'solarpv',
            'SOLAR THERMAL': 'solarth',
            'NUCLEAR': 'nuclear',
            'THERMAL': 'thermal',
            'HYDRO': 'hydro',            
        }

    def get_generation(self, latest=False, yesterday=False,
                       start_at=False, end_at=False, **kwargs):
        # set args
        self.handle_options(data='gen', latest=latest, yesterday=yesterday,
                            start_at=start_at, end_at=end_at, **kwargs)

        if latest:
            return self._generation_latest()
        else:
            return self._generation_historical()

    def get_load(self, latest=False,
                       start_at=False, end_at=False, **kwargs):
        # set args
        self.handle_options(data='gen', latest=latest,
                            start_at=start_at, end_at=end_at, **kwargs)

        # get start and end times
        now = self.utcify(datetime.utcnow(), tz_name='utc')
        if self.options['latest']:
            startdatetime = now - timedelta(minutes=20)
            enddatetime = now + timedelta(minutes=20)
        else:
            startdatetime = self.options['start_at']
            enddatetime = self.options['end_at']
 
        # fetch OASIS load data
        payload = {'queryname': 'SLD_FCST',
                   'market_run_id': 'RTM',
                   'startdatetime': (startdatetime).strftime(self.oasis_request_time_format),
                   'enddatetime': (enddatetime).strftime(self.oasis_request_time_format),
                  }
        payload.update(self.base_payload)
        oasis_data = self.fetch_oasis(payload=payload)

        # parse data
        parsed_data = self.parse_oasis_demand_forecast(oasis_data)

        if self.options['latest']:
            # select latest
            latest_dp = None
            latest_ts = self.utcify('1900-01-01 12:00')
            for dp in parsed_data:
                if dp['timestamp'] < now and dp['timestamp'] > latest_ts:
                    latest_dp = dp
                    latest_ts = dp['timestamp']

            # return latest
            if latest_dp:
                return [latest_dp]
            else:
                return []
        else:
            # return all data
            return parsed_data

    def set_dt_index(self, df, date, hours, end_of_hour=True):
        if end_of_hour:
            offset = -1
        else:
            offset = 0

        # create list of combined datetimes
        dts = [datetime.combine(date, time(hour=(h+offset))) for h in hours]

        # set list as index
        df.index = dts

        # utcify
        df.index = self.utcify_index(df.index)

        # return
        return df

    def _generation_historical(self):
        # set up storage
        parsed_data = []

        # collect data
        this_date = self.options['start_at'].date()
        while this_date <= self.options['end_at'].date():
            # set up request
            url_file = this_date.strftime('%Y%m%d_DailyRenewablesWatch.txt')
            url = self.base_url_gen + url_file
            
            # carry out request
            response = self.request(url)
            if not response:
                this_date += timedelta(days=1)
                continue

            # process both halves of page
            for header in [1, 29]:
                df = self.parse_to_df(response.text,
                                    skiprows=header, nrows=24, header=header,
                                    delimiter='\t+')

                # combine date with hours to index
                indexed = self.set_dt_index(df, this_date, df['Hour'])

                # original header is fuel names
                indexed.rename(columns=self.fuels, inplace=True)

                # remove non-fuel cols
                fuel_cols = list( set(self.fuels.values()) & set(indexed.columns) )
                subsetted = indexed[fuel_cols]

                # pivot
                pivoted = self.unpivot(subsetted)
                pivoted.rename(columns={'level_1': 'fuel_name', 0: 'gen_MW'}, inplace=True)

                # store
                parsed_data += self.serialize(pivoted,
                                      header=['timestamp', 'fuel_name', 'gen_MW'],
                                      extras={'ba_name': self.NAME,
                                              'market': self.MARKET_CHOICES.hourly,
                                              'freq': self.FREQUENCY_CHOICES.hourly})

            # finish day
            this_date += timedelta(days=1)

        # return
        return parsed_data
        
    def fetch_oasis(self, payload={}):
        """Returns a list of report data elements, or an empty list if an error was encountered."""
        # set up storage
        raw_data = []
 
        # try get
        response = self.request(self.base_url_oasis, params=payload) # have request
        if not response:
            return []
            
        # read data from zip
        content = self.unzip(response.content)
        if not content:
            return []
        
        # load xml into soup
        soup = BeautifulSoup(content)
        
        # check xml content
        error = soup.find('m:error')
        if error:
            code = error.find('m:err_code')
            desc = error.find('m:err_desc')
            msg = 'XML error for CAISO OASIS with payload %s: %s %s' % (payload, code, desc)
            self.logger.error(msg)
            return []
                
        else:
            raw_data = soup.find_all('report_data')
            return raw_data
        
    def parse_oasis_renewable(self, raw_data):
        """Parse raw data output of fetch_oasis for renewables."""
        # set up storage
        preparsed_data = {}
        parsed_data = []
        
        # extract values from xml
        for raw_soup_dp in raw_data:
            # set up storage for timestamp
            ts = self.utcify(raw_soup_dp.find('interval_start_gmt').string)
            if ts not in preparsed_data:
                preparsed_data[ts] = {'wind': 0, 'solar': 0}
                
            # store generation value
            try:
                fuel_name = raw_soup_dp.find('renewable_type').string.lower()
                gen_MW = float(raw_soup_dp.find('value').string)
                preparsed_data[ts][fuel_name] += gen_MW
            except TypeError:
                self.logger.error('Error in schema for CAISO OASIS result %s' % raw_soup_dp.prettify())
                continue
            
        # collect values into dps
        for ts, preparsed_dp in preparsed_data.iteritems():
            # set up base
            base_parsed_dp = {'timestamp': ts,
                              'freq': self.FREQUENCY_CHOICES.hourly,
                              'market': self.MARKET_CHOICES.hourly,
                              'gen_MW': 0, 'ba_name': self.NAME}
                          
            # collect data
            for fuel_name in ['wind', 'solar']:
                parsed_dp = copy.deepcopy(base_parsed_dp)
                parsed_dp['fuel_name'] = fuel_name
                parsed_dp['gen_MW'] += preparsed_dp[fuel_name]
                parsed_data.append(parsed_dp)
            
        # return
        return parsed_data

    def parse_oasis_slrs(self, raw_data):
        """Parse raw data output of fetch_oasis for System Load and Resource Schedules."""
        # set up storage
        parsed_data = []
        
        # extract values from xml
        for raw_soup_dp in raw_data:
            if raw_soup_dp.find('data_item').string == 'ISO_TOT_GEN_MW':
                
                # parse timestamp
                ts = self.utcify(raw_soup_dp.find('interval_start_gmt').string)

                # set up base
                parsed_dp = {'timestamp': ts, 'fuel_name': 'other',
                              'freq': self.FREQUENCY_CHOICES.fivemin,
                              'market': self.MARKET_CHOICES.fivemin,
                              'ba_name': self.NAME}
                    
                # store generation value
                parsed_dp['gen_MW'] = float(raw_soup_dp.find('value').string)
                parsed_data.append(parsed_dp)
                
        # return
        return parsed_data

    def parse_oasis_demand_forecast(self, raw_data):
        """Parse raw data output of fetch_oasis for system-wide 5-min RTM demand forecast."""
        # set up storage
        parsed_data = []
        
        # extract values from xml
        for raw_soup_dp in raw_data:
            if raw_soup_dp.find('data_item').string == 'SYS_FCST_5MIN_MW' and \
                    raw_soup_dp.find('resource_name').string == 'CA ISO-TAC':
                
                # parse timestamp
                ts = self.utcify(raw_soup_dp.find('interval_start_gmt').string)

                # set up base
                parsed_dp = {'timestamp': ts,
                              'freq': self.FREQUENCY_CHOICES.fivemin,
                              'market': self.MARKET_CHOICES.fivemin,
                              'ba_name': self.NAME}
                    
                # store generation value
                parsed_dp['load_MW'] = float(raw_soup_dp.find('value').string)
                parsed_data.append(parsed_dp)
                
        # return
        return parsed_data
        
    def todays_outlook_time(self):
       # get timestamp
        response = self.request(self.base_url_outlook+'systemconditions.html')
        if not response:
            return None

        demand_soup = BeautifulSoup(response.content)
        for ts_soup in demand_soup.find_all(class_='docdate'):
            match = re.search('\d{1,2}-[a-zA-Z]+-\d{4} \d{1,2}:\d{2}', ts_soup.string)
            if match:
                ts_str = match.group(0)
                return self.utcify(ts_str)

    def _get_todays_outlook(self):
        # set up storage
        parsed_data = []
        
        # get timestamp from outlook page
        ts = self.todays_outlook_time()
        if not ts:
            return []

        # get renewables data
        response = self.request(self.base_url_outlook+'renewables.html')
        if not response:
            return []
        ren_soup = BeautifulSoup(response.content)
        
        # get all renewables values
        for (id_name, fuel_name) in [('totalrenewables', 'renewable'),
                                        ('currentsolar', 'solar'),
                                        ('currentwind', 'wind')]:
            resource_soup = ren_soup.find(id=id_name)
            match = re.search('(?P<val>\d+.?\d+) MW', resource_soup.string)
            if match:
                parsed_dp = {'timestamp': ts,
                              'freq': self.FREQUENCY_CHOICES.tenmin,
                              'market': self.MARKET_CHOICES.tenmin,
                              'ba_name': self.NAME}
                parsed_dp['gen_MW'] = float(match.group('val'))
                parsed_dp['fuel_name'] = fuel_name
                parsed_data.append(parsed_dp)
                
        # actual 'renewable' value should be only renewables that aren't accounted for in other categories
        accounted_for_ren = 0
        for dp in parsed_data:
            if dp['fuel_name'] != 'renewable':
                accounted_for_ren += dp['gen_MW']
        for dp in parsed_data:
            if dp['fuel_name'] == 'renewable':
                dp['gen_MW'] -= accounted_for_ren
                
        return parsed_data            
        
    def _generation_latest(self, **kwargs):
        # set up
        parsed_data = []
        
        # get and parse "Today's Outlook" data
        parsed_data += self._get_todays_outlook()
        total_ren_MW = sum([dp['gen_MW'] for dp in parsed_data])
        ts = parsed_data[0]['timestamp']
        
        # get and parse OASIS total gen data
        gen_payload = {'queryname': 'ENE_SLRS',
                   'market_run_id': 'RTM', 'schedule': 'ALL',
                   'startdatetime': (ts-timedelta(minutes=20)).strftime(self.oasis_request_time_format),
                   'enddatetime': (ts+timedelta(minutes=20)).strftime(self.oasis_request_time_format),
                  }
        gen_payload.update(self.base_payload)
        gen_oasis_data = self.fetch_oasis(payload=gen_payload)
        has_other = False
        for dp in self.parse_oasis_slrs(gen_oasis_data):
            if dp['timestamp'] == ts:
                dp['gen_MW'] -= total_ren_MW
                dp['freq'] = self.FREQUENCY_CHOICES.tenmin
                parsed_data.append(dp)
                has_other = True
                break

        # check and return
        if has_other:
            return parsed_data
        else:
            return []
