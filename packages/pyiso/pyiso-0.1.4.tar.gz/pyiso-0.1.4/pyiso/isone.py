import copy
from datetime import timedelta
from pyiso.base import BaseClient


class ISONEClient(BaseClient):
    def __init__(self):
        self.NAME = 'ISONE'
        
        self.base_url = 'http://isoexpress.iso-ne.com/ws/wsclient'
        self.base_payload = {'_ns0_requestType':'url'}
        self.TZ_NAME = 'America/New_York'
        
        self.fuels = {
            'Coal': 'coal',
            'Hydro': 'hydro',
            'Natural Gas': 'natgas',
            'Nuclear': 'nuclear',
            'Oil': 'oil',
            'Solar': 'solar',
            'Wind': 'wind',
            'Wood': 'biomass',
            'Refuse': 'refuse',
            'Landfill Gas': 'biogas',
        }

    def get_generation(self, latest=False, start_at=False, end_at=False, **kwargs):
        # set args
        self.handle_options(data='gen', latest=latest,
                            start_at=start_at, end_at=end_at, **kwargs)

        # process args
        request_urls = []
        if latest:
            request_urls.append('current')

        elif start_at and end_at:
            this_date = start_at.date()
            while this_date <= end_at.date():
                request_urls.append(this_date.strftime('day/%Y%m%d'))
                this_date += timedelta(days=1)
        else:
            raise ValueError('Either latest must be True, or start_at and end_at must both be provided.')
            
        # set up storage
        raw_data = []
        parsed_data = []

        # collect raw data
        for request_url in request_urls:
            # set up request
            payload = copy.deepcopy(self.base_payload)
            payload.update({'_ns0_requestUrl':'/genfuelmix/%s' % request_url})
            
            # carry out request
            response = self.request(self.base_url, mode='post', data=payload)
            raw_data += response.json()[0]['data']['GenFuelMixes']['GenFuelMix']

        # parse data
        for raw_dp in raw_data:
            # set up storage
            parsed_dp = {}
            
            # add values
            parsed_dp['timestamp'] = self.utcify(raw_dp['BeginDate'])
            parsed_dp['gen_MW'] = raw_dp['GenMw']
            parsed_dp['fuel_name'] = self.fuels[raw_dp['FuelCategory']]
            parsed_dp['ba_name'] = self.NAME
            parsed_dp['market'] = self.MARKET_CHOICES.na
            parsed_dp['freq'] = self.FREQUENCY_CHOICES.na
            
            # add to full storage
            parsed_data.append(parsed_dp)
 
        return parsed_data
