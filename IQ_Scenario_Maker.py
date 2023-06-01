import os
# import sys
import datetime
# import time
import logging
# import re
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
# import argparse
# import exifread
import tkinter
from tkinter import filedialog



def set_logging_level(logging_lv):
    # import datetime
    # print('[{}] Current Logging Level : ({}) {}'.format(sys._getframe().f_code.co_name, self.logging_level, _log_level_ini))
    if not os.path.exists('./_pylog'):
        os.makedirs('./_pylog')
    _now = datetime.datetime.now()
    _log_file = './_pylog/Log_PhoneControl_' + _now.strftime('%Y%m%d') + '.log'

    # 로그 생성 (console)
    logger = logging.getLogger()
    # 로그의 출력 기준 설정
    logger.setLevel(logging_lv)
    # log 출력 형식
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)-7s] [%(filename)s (%(lineno)4d)] [%(funcName)20s] %(message)s')
    # log format 설정
    # logger.handlers[0].formatter = formatter

    # log를 파일에 출력
    file_handler = logging.FileHandler(_log_file, 'a', 'utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def log_info_function():
    import inspect
    cf = inspect.currentframe()
    line_number = cf.f_back.f_lineno
    func_name = cf.f_back.f_code.co_name
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    file_name = module.__file__
    get_filename = file_name.split('/')[-1]
    return '[{}] [{} ({:>4})] [{:>30}] '.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), get_filename, line_number, func_name)


def select_file(init_dir='./', file_type=(("All files", "*.*"),)):
    '''
    .. Note:: 1개의 파일 선택
    :return: filename (str) : 선택된 Filename (경로 포함)
    '''
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    filename = os.path.abspath(filedialog.askopenfilename(parent=tk_root,
                                                          initialdir=init_dir,
                                                          title='Please select a file',
                                                          filetypes=file_type))
    # print("Selected file: {}".format(filename))
    logging.info('Selected file: {}'.format(filename))
    return filename


def select_folder_location(init_dir='./'):
    """
    .. Note:: Select folder location
    :param init_dir: Initial Directory (default = './')
    :return:
      selected_dir (str) : Selected folder location
    """
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    selected_dir = os.path.abspath(filedialog.askdirectory(parent=tk_root,
                                                           initialdir=init_dir,
                                                           title='Please select a directory'))
    # print('Selected folder: {}'.format(select_dir))
    logging.info('Selected folder: {}'.format(selected_dir))
    return selected_dir


def make_filelist(target_dir, subdir=False, list_filetype=None):
    """
    .. Note:: 선택된 폴더와 하위 폴더까지의 파일 리스트와 폴더 리스트를 Return 하는 함수
    :param target_dir: 리스트로 작성하고자 하는 root 폴더
    :param subdir: 하위 디렉토리 검색 여부 (Default : False)
    :param list_filetype: 리스트로 작성할 파일의 확장자 ex. ['.csv', '.json'] (Default : None)
    :return:
        file_list - 파일 리스트 (list) (경로명 포함)
    """
    _filelist_all = []
    file_list = []

    if subdir:
        for path, direct, files in os.walk(target_dir):
            # file_path = [os.path.join(path, file) for file in files]
            file_path = [os.path.abspath(os.path.join(path, file)) for file in files]
            # print(file_path)
            _filelist_all.extend(file_path)
    else:
        _filelist_all = [os.path.join(os.path.abspath(target_dir), file) for file in os.listdir(target_dir) if
                         os.path.isfile(os.path.join(os.path.abspath(target_dir), file))]

    for _idx_file in tqdm(_filelist_all):
        if list_filetype != None:
            if os.path.splitext(_idx_file)[1].lower() in [idx.lower() for idx in list_filetype]:
                file_list.append(_idx_file)
        else:
            file_list.append(_idx_file)
    logging.info('Total files: {}, Selected files: {}'.format(len(_filelist_all), len(file_list)))
    return file_list

class ImageCaptureScenarioMaker:
    def __init__(self):
        logging.warning('-=-=-=-=-=-=-=-=- Image Capture Scenario Maker v1.1 -=-=-=-=-=-=-=-=-')
        print(log_info_function() + '-=-=-=-=-=-=-=-=- Image Capture Scenario Maker v1.1 -=-=-=-=-=-=-=-=-')
        self.lightInfoLUT = {'LD100': {'ctemp': '10000', 'maxdac': '4000', 'feedback_name': 'Led', 'headangle': '168'},
                             'LD65': {'ctemp': '6500', 'maxdac': '4000', 'feedback_name': 'Led', 'headangle': '168'},
                             'LD51': {'ctemp': '5100', 'maxdac': '4000', 'feedback_name': 'Led', 'headangle': '168'},
                             'LD41': {'ctemp': '4100', 'maxdac': '4000', 'feedback_name': 'Led', 'headangle': '168'},
                             'LD32': {'ctemp': '3200', 'maxdac': '4000', 'feedback_name': 'Led', 'headangle': '168'},
                             'LD24': {'ctemp': '2400', 'maxdac': '4000', 'feedback_name': 'Led', 'headangle': '168'},
                             'HD65': {'ctemp': '6500', 'maxdac': '1300', 'feedback_name': 'Halogen', 'headangle': '0'},
                             'H3200': {'ctemp': '3200', 'maxdac': '1300', 'feedback_name': 'Halogen', 'headangle': '0'},
                             'INCA': {'ctemp': '2856', 'maxdac': '1300', 'feedback_name': 'Halogen', 'headangle': '0'},
                             'HOR': {'ctemp': '2380', 'maxdac': '700', 'feedback_name': 'Halogen', 'headangle': '0'},
                             'FD75': {'ctemp': '7500', 'maxdac': '3200', 'feedback_name': 'Fluorescent', 'headangle': '0'},
                             'FD50': {'ctemp': '5000', 'maxdac': '3200', 'feedback_name': 'Fluorescent', 'headangle': '0'},
                             'CWF': {'ctemp': '4150', 'maxdac': '3200', 'feedback_name': 'Fluorescent', 'headangle': '0'},
                             'TL84': {'ctemp': '3950', 'maxdac': '3200', 'feedback_name': 'Fluorescent', 'headangle': '0'}
                             }

    def read_setting_file(self):
        self.filename = select_file(init_dir='./', file_type=(("Excel File", "*.xlsx"), ("Excel 97-2003 File", "*.xls"), ("Excel Macro File", "*.xlsm"), ("All files", "*.*")))
        print(log_info_function() + 'Filename: {}'.format(os.path.basename(self.filename)))
        self.df_setting_chart = pd.read_excel(self.filename, sheet_name='Chart_Setting').set_index('Chart')
        self.df_setting_mirroring = pd.read_excel(self.filename, sheet_name='Mirroring_Setting').set_index('Phone')
        self.df_scenariolist = pd.read_excel(self.filename, sheet_name='Scenario')
        
        self.df_scenariolist['LightType'] = [self.lightInfoLUT[idx_light]['feedback_name'] for idx_light in self.df_scenariolist['Light']]
        return self.df_setting_chart, self.df_setting_mirroring, self.df_scenariolist

    def set_chart(self, chartName, chartHead, chartHeadNo):
        """
        .. Note:: Chart Setting

        :param chartName: [ eSFR / SFRplus / Deadleaves / etc. ]
        :param chartHead: [ LEFT / RIGHT ]
        :param chartHeadNo: [ 1 / 2 / 3 / 4 ]
        :return: (dict) scenario
        """
        print(log_info_function() + 'Set Chart >> Chart name: {}, ChartHead(L/R): {}, ChartHead No.: {}'.format(chartName, chartHead, chartHeadNo))
        dict_scenario = {'part': '-----------------------------------',
                         'value': "Chart: {} [{}, {}]".format(chartName, chartHead, chartHeadNo),
                         'action': []}
        dict_scenario['action'].append({"part": "Chart",
                                        "value": "{}:".format(chartHead),
                                        "action": []})
        if chartHead == 'LEFT':
            dict_scenario['action'].append({"part": "ChartHL",
                                            "value": "{}".format(chartHeadNo),
                                            "action": []})
        elif chartHead == 'RIGHT':
            dict_scenario['action'].append({"part": "ChartHR",
                                            "value": "{}".format(chartHeadNo),
                                            "action": []})
        else:
            print(log_info_function() + 'Chart Head is {}. Please check again !!'.format(chartHead))
            
        return dict_scenario
    
    def set_light(self, light, lux):
        '''
        .. Note:: Light Setting
        
        :param light: [LD65 / HD65 / etc.]
        :param lux: [2000 / 1000 / 100/ etc.]
        :return: (dict) scenario
        '''
        print(log_info_function() + 'Set Light >> Light: {} [{}K, {} lux]'.format(light, self.lightInfoLUT[light.upper()]['ctemp'], lux))
        dict_scenario = {'part': '-----------------------------------',
                         'value': "Light: {} [{} K, {} Lux]".format(light, self.lightInfoLUT[light.upper()]['ctemp'], lux),
                         'action': []}
        dict_scenario['action'].append({"part": "LoadLight",
                                        "value": "{}:{}:{}".format(light.upper(), self.lightInfoLUT[light.upper()]['ctemp'], lux),
                                        "action": []})
        return dict_scenario

    def mirroring(self, win_title=""):
        print(log_info_function() + 'Mirroring >> Window Title or Serial: {}'.format(win_title))
        dict_scenario = {'part': '-----------------------------------',
                         'value': "Mirroring [Window Title or Serial: {}]".format(win_title),
                         'action': []}
        dict_scenario['action'].append({"part": "Mirroring",
                                        "value": win_title,
                                        "action": []})
        return dict_scenario
    
    def move_camjig_y(self, value_Y):
        print(log_info_function() + 'Move CamJig Y Position to {}'.format(value_Y))
        dict_scenario = {'part': '-----------------------------------',
                         'value': 'Move CamJig Y Position to {}'.format(int(value_Y)),
                         'action': []}
        dict_scenario['action'].append({'part': 'CamYRun',
                                        'value': '{}'.format(int(value_Y)),
                                        'action': []})
        return dict_scenario
    
    def auto_detection_chart(self, chartName, px_LL, px_LR, px_TT, px_TB):
        print(log_info_function() + 'AutoDetection >> Chart name: {}, Crop: {}:{}:{}:{}'.format(chartName, px_LL, px_LR, px_TT, px_TB))
        dict_scenario = {'part': '-----------------------------------',
                         'value': 'AutoDetection [Chart: {}, Crop: {}:{}:{}:{}]'.format(chartName, px_LL, px_LR, px_TT, px_TB),
                         'action': []}
        dict_scenario['action'].append({'part': 'AutoDetect',
                                        'value': '{}:{}:{}:{}:{}'.format(chartName, int(px_LL), int(px_LR), int(px_TT), int(px_TB)),
                                        'action': []})
        return dict_scenario

    def phone_control(self, Phone, value_Y, f_num):
        print(log_info_function() + '>> Capture')
        dict_scenario = {'part': '-----------------------------------',
                         'value': f'capture.py" --ypos {value_Y}',
                         'action': []}
        dict_scenario['action'].append({'part': 'CmdRun',
                                        'value': f'python \"D:\\CTS_Resource\\PhoneControl\\DOF\\DOF.py\" --phone {Phone} --ypos {value_Y} --f {f_num}',
                                        'action': []})
        return dict_scenario



if __name__ == '__main__':
    idx_phone = "Xiaomi 13 Ultra"
    # idx_phone = "P60 Pro"



    IQS = ImageCaptureScenarioMaker()
    list_phone_chart = []
    _now = datetime.datetime.now()
    scenario_test = {"scen_name": "Test", "action": []}
    for i in range(10150, 9500, -10):
        scenario_test['action'].append(IQS.move_camjig_y(i))
        scenario_test['action'].append(IQS.phone_control(idx_phone, i, 1.9))
        # scenario_test['action'].append(IQS.phone_control(idx_phone, i, 2.0))
        # scenario_test['action'].append(IQS.phone_control(idx_phone, i, 2.8))
        scenario_test['action'].append(IQS.phone_control(idx_phone, i, 4.0))

    # Write Scenario to file
    result_folder = './IQ_Test_Scenario_' + _now.strftime('%Y%m%d_%H%M%S')
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    filename_scenario = os.path.join(result_folder, 'Scenario_{}.json'.format(idx_phone))
    print(log_info_function() + '$$$ Save Scenario to {}'.format(filename_scenario))
    with open(filename_scenario, 'w', encoding='UTF-8') as scenario_json:
        json.dump(scenario_test, scenario_json, indent='\t', ensure_ascii=False)
