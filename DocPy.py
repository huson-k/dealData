import pandas as pd
import os


def get_allData(JF, bOa):
    csv_file_name = r'/Users/kwok/Desktop/AI_for_env/dealData/csv/' + JF + '/' + bOa + '/'
    data = pd.DataFrame()
    data_list = os.listdir(csv_file_name)
    for i in data_list[:]:
        csv_ = pd.read_csv(csv_file_name + i)
        data = pd.concat([data, csv_], axis=0)
    return data


def get_ktpower(data):
    # 选择列名包含“空调总有功功率”字样的列并计算总和
    ac_power_columns = [col for col in data.columns if "空调总有功功率" in col]
    data['空调总有功功率总和'] = data[ac_power_columns].sum(axis=1)
    return data


def get_fwqpower(data):
    # 选择列名包含“服务器X功率”字样的列并计算总和
    server_power_columns = [col for col in data.columns if "服务器" in col and "功率" in col]
    data['服务器功率总和'] = data[server_power_columns].sum(axis=1)
    # 防止数据异常，做数据范围筛选
    data = data[data['服务器功率总和'] != 0]
    data = data[data['服务器功率总和'] > 200]
    data['pPUE'] = (data['服务器功率总和'] + data['空调总有功功率总和']) / data['服务器功率总和']
    return data


def get_ktdata(data):
    # "风机1转速", "风机2转速", "压缩机1转速", "压缩机2容量"
    selected_columns = ['sampleTime'] + ['空调总有功功率总和', '服务器功率总和', 'pPUE']
    additional_columns = ["回风温度1", "送风温度1", "风机1转速", "风机2转速", "压缩机1容量", "压缩机2容量",
                          "冷凝风机1转速"]
    selected_columns += [col for col in data.columns if any(keyword in col for keyword in additional_columns)]
    selected_columns = [element for element in selected_columns if "设定" not in element]

    # 创建包含选定列的新DataFrame
    selected_data = data[selected_columns]
    return selected_data


def get_ltdTemps(data, JF, fwq):
    # 选择其他指定列
    for fwq_i in fwq:
        if JF=='203':
            additional_columns = ["FT" + JF + '-' + fwq_i]
        if JF=='204':
            additional_columns = ["FT-" + JF + '-' + fwq_i]
        temps_columns = [col for col in data.columns if any(keyword in col for keyword in additional_columns)]
        # 计算每列的平均值

        data[fwq_i + '冷通道avg'] = data[temps_columns].mean(axis=1)

    server_tempsAVG_columns = [col for col in data.columns if "冷通道avg" in col]

    columns = server_tempsAVG_columns

    averages_data = pd.DataFrame({
        'AB冷通道avg': data[[columns[0], columns[1]]].mean(axis=1),
        'CD冷通道avg': data[[columns[2], columns[3]]].mean(axis=1),
        'EF冷通道avg': data[[columns[4], columns[5]]].mean(axis=1),
        'GH冷通道avg': data[[columns[6], columns[7]]].mean(axis=1),
        'JK冷通道avg': data[[columns[8], columns[9]]].mean(axis=1)
    })
    return averages_data


def JFdata(JF, bOa):
    if JF == '204':
        fwq = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P']
    if JF == '203':
        fwq = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K']

    data = get_allData(JF, bOa)
    data = get_ktpower(data)
    data = get_fwqpower(data)
    selected_data = get_ktdata(data)
    averages_data = get_ltdTemps(data, JF, fwq)

    all_csv = pd.concat([selected_data, averages_data], axis=1)
    # 删除指定列中包含0的行
    all_csv = all_csv[(all_csv.iloc[:, -5:] > 10).all(axis=1)]
    all_csv_avg = all_csv.iloc[:, 1:].mean(axis=0)
    average_df = pd.DataFrame(all_csv_avg)
    average_df.rename(columns={0: JF + bOa}, inplace=True)
    return average_df


JF = '204'

before = JFdata(JF, 'before')
after = JFdata(JF, 'after')

data = pd.concat([before, after], axis=1)

data['变化百分比（%）'] = ((data.iloc[:, 1] - data.iloc[:, 0]) / data.iloc[:, 0]) * 100
data.to_csv('/Users/kwok/Desktop/AI_for_env/dealData/dataCsv/finally/' + JF + '.csv')
