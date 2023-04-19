import networkx as nx
import json
from scrapy import Request, Spider
from scrapy.http import Response
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class CpSearchSpider(Spider):
    name = "cp_search_spider"
    allowed_domains = ["sos.nd.gov"]

    def __init__(self, startswith='X', graph_output='graph.png', *args, **kwargs):
        super(CpSearchSpider, self).__init__(*args, **kwargs)
        self.startswith = startswith
        self.graph_output = graph_output
        self.graph_features = []
        self._graph_pos = None
        self.HEADERS = {
            'authority': 'firststop.sos.nd.gov',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'undefined',
            'content-type': 'application/json',
            'origin': 'https://firststop.sos.nd.gov',
            'referer': 'https://firststop.sos.nd.gov/search/business',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }

    def start_requests(self):
        body = {
            # apparently the startswith filter on the website doesn't filter quite good, so we can filter our items later if we require to
            'SEARCH_VALUE': self.startswith,  # FIXME: needs to be dynamic
            'STARTS_WITH_YN': 'true',  # startswith
            'ACTIVE_ONLY_YN': 'true',  # active only
        }
        r = Request(
            url='https://firststop.sos.nd.gov/api/Records/businesssearch',
            method='POST',
            headers=self.HEADERS,
            body=json.dumps(body),
            callback=self.parse_company)
        self.logger.info(
            "Calling Initial Request with params: {0}".format(body))

        return [r]

    def parse_company(self, response: Response):
        if response.status == 200:
            companies_data = json.loads(response.body)

            for key, company_row in companies_data['rows'].items():
                yield Request(
                    url='https://firststop.sos.nd.gov/api/FilingDetail/business/{0}/false'.format(
                        key),
                    method='GET',
                    headers=self.HEADERS,
                    meta={'company_row': company_row},
                    callback=self.parse_filing)

    def parse_filing(self, response: Response):
        company_details = {}

        if response.meta.get('company_row', ''):
            company_row = response.meta['company_row']
            company_details.update(company_row)

        if response.status == 200:
            filing_details = json.loads(response.body)
            filing_details = filing_details.get('DRAWER_DETAIL_LIST', {})

            if filing_details:
                for detail in filing_details:
                    company_details.update({detail['LABEL']: detail['VALUE']})
            else:
                self.logger.info(
                    "parse_filing:: failed to obtain filing_details for {0}".format(response.url))

            # Splitting title field from title and sector
            title_field = company_details['TITLE']
            company_details['TITLE'] = title_field[0] if len(
                title_field) > 1 else title_field

            # Extracting features for my graph in an array to get company network analysis and node labels
            # Best Practice is to put this in a spider pipeline
            title_feature = "COMPANY: " + company_details['TITLE']
            owner_feature = "OWNER: " + \
                company_details['Owner Name'] if company_details.get(
                    'Owner Name', None) else None
            reg_agent_feature = "REG_AGENT: " + \
                company_details['Registered Agent'] if company_details.get(
                    'Registered Agent', None) else None
            comm_agent_feature = "COMM_REG_AGENT: " + \
                company_details['Commercial Registered Agent'] if company_details.get(
                    'Commercial Registered Agent', None) else None
            self.graph_features.append(
                tuple(filter(None,
                             (title_feature,
                              owner_feature,
                              reg_agent_feature,
                              comm_agent_feature
                              ))
                      ))
        return company_details

    def closed(self, reason):
        """
        This function is usually called on spider close signal
        """
        self._generate_graph(True, self.graph_output, 1)
        self._generate_graph(False, "nolabel_"+self.graph_output, 2)

    def _generate_graph(self, with_label, fname, fig):
        plt.figure(fig, figsize=(32, 32))
        G = nx.Graph()

        for l in self.graph_features:
            if len(l) > 1:
                l = tuple(filter(None, l))
                nx.add_path(G, l)

        if self._graph_pos:
            pos = self._graph_pos
        else:
            pos = nx.spring_layout(G, scale=16, k=4/np.sqrt(G.order()))
            self._graph_pos = pos

        colors = [self._paint_node(node) for node in G.nodes]
        degrees = [G.degree[node]*1000 for node in G.nodes()]

        nx.draw(G, pos, node_color=colors, node_size=degrees,
                with_labels=with_label, font_size='12')
        plt.savefig(fname)

    def _paint_node(self, node):
        if node.startswith('COMM_REG_AGENT'):
            return '#FFBF00'  # Orange
        elif node.startswith('OWNER'):
            return '#D9F73F'  # Green
        elif node.startswith('REG_AGENT'):
            return '#EE9E9D'  # Pink
        else:
            return '#87DEE7'  # Blue

# scrapy crawl cp_search_spider -a startswith='X' -a graph_output='GRAPH.png' -O items.json
