import json
import re

table = [{'Columns View': 'SO Number', 'Sort By': '', 'Highlight By': 'equals=S110=rgba(172,86,86,1),equals=S111', 'Condition': 'equals=S110,equals=S111', 'Row Height': '60', 'Lines per page': '25'},
         {'Columns View': 'Client PO', 'Sort By': '', 'Highlight By': 'equals=P110,equals=P111', 'Condition': 'equals=P110', 'Row Height': '', 'Lines per page': ''},
         {'Columns View': 'Terms of Sale', 'Sort By': 'asc', 'Highlight By': 'equals=S110=rgba(172,86,86,1)', 'Condition': '', 'Row Height': '', 'Lines per page': ''}]

websocket_response = {'Client PO': {'index': 'so_list_client_po', 'filter': 'client_po'},
                      'SO Number': {'index': 'so_list_so_number', 'filter': 'so_no'},
                      'Terms of Sale': {'index': 'so_list_terms_of_sale', 'filter': 'term_sale'}}

base_ws = {'Columns View': 'columns',
           'Sort By': 'order_by',
           'Condition': 'conditions_data',
           'Lines per page': 'page_size',
           'Row Height': 'row_height',
           'Highlight By': 'color_conditions'}
           
           
           
           

result = {'columns': [{'index': 'so_list_so_number', 'sort': 0}, 
                      {'index': 'so_list_client_po', 'sort': 1}, 
                      {'index': 'so_list_terms_of_sale', 'sort': 2}], 
          'order_by': {'direction': 'asc', 'index': 'so_list_terms_of_sale'},
          'conditions_data': {'so_no': [{'type': 'equals', 'value': 'S110'}, 
                                        {'type': 'equals', 'value': 'S111'}], 
                              'client_po': [{'type': 'equals', 'value': 'P110'}]}, 
          'page_size': '25', 
          'row_height': '60',
          'color_conditions': {'so_no': [{'type': 'equals', 'value': 'S110', 'color': 'rgba(172,86,86,1)'}], 
                               'client_po': [{'type': 'equals', 'value': 'S110', 'color': ''}, {'type': 'equals', 'value': 'S111', 'color': ''}],
                               'term_sale': []}, 
          'module': 'SO'}



class TableProcessor:
    def __init__(self, table, websocket_response, base_ws):
        # Инициализация исходных данных
        self.table = table
        self.websocket_response = websocket_response
        self.base_ws = base_ws
        self.result = {
            'columns': [],
            'order_by': {},
            'conditions_data': {},
            'page_size': '',
            'row_height': '',
            'color_conditions': {}
        }

    def process(self):
        for i, row in enumerate(self.table):
            column_view = row.get('Columns View')
            ws_info = self.websocket_response.get(column_view, {})

            if ws_info:
                self.result['columns'].append({
                    'index': ws_info.get('index', ''),
                    'sort': i
                })

            sort_by = row.get('Sort By', '').lower()
            if sort_by in ['asc', 'desc']:
                self.result['order_by'] = {
                    'direction': sort_by,
                    'index': ws_info.get('index', '')
                }

            # Обработка 'Condition'
            condition = row.get('Condition', '')
            if condition:
                conditions_list = []
                conditions = condition.split(',')
                for cond in conditions:
                    cond_type, value = cond.split('=')
                    conditions_list.append({
                        'type': cond_type,
                        'value': value
                    })
                self.result['conditions_data'][ws_info.get('filter', '')] = conditions_list
            highlight_by = row.get('Highlight By', '')
            if highlight_by:
                highlights_list = []
                highlights = re.split(r',(?!(?:[^()]*\([^()]*\))?[^()]*$)', highlight_by)
                for highlight in highlights:
                    parts = highlight.split('=')
                    cond_type = parts[0] if len(parts) > 0 else ''
                    value = parts[1] if len(parts) > 1 else ''
                    color = parts[2] if len(parts) > 2 else ''
                    highlights_list.append({
                        'type': cond_type,
                        'value': value,
                        'color': color
                    })
                self.result['color_conditions'][ws_info.get('filter', '')] = highlights_list

        self.result['row_height'] = self.table[0].get('Row Height', '')
        self.result['page_size'] = self.table[0].get('Lines per page', '')

        return self.result

def process_table_to_json(table, websocket_response, base_ws):
    processor = TableProcessor(table, websocket_response, base_ws)
    return processor.process()

result_enhanced = process_table_to_json(table, websocket_response, base_ws)
print(json.dumps(result_enhanced, indent=4))
