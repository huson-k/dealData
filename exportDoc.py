import pandas as pd
import os

JF = '204'
bOa = 'be fore'
if JF == '204':
    fwq = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P']
if JF == '203':
    fwq = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K']

csv_file_name = r'/Users/kwok/Desktop/AI_for_env/dealData/csv/' + JF + '/' + bOa + '/'
data = pd.DataFrame()
data_list = os.listdir(csv_file_name)
for i in data_list[:]:
    csv_ = pd.read_csv(csv_file_name + i)
    data = pd.concat([data, csv_], axis=0)

# 选择列名包含“空调总有功功率”字样的列并计算总和
ac_power_columns = [col for col in data.columns if "空调总有功功率" in col]
data['空调总有功功率总和'] = data[ac_power_columns].sum(axis=1)

# 选择列名包含“服务器X功率”字样的列并计算总和
server_power_columns = [col for col in data.columns if "服务器" in col and "功率" in col]
data['服务器功率总和'] = data[server_power_columns].sum(axis=1)
# 防止数据异常，做数据范围筛选
data = data[data['服务器功率总和'] != 0]
data = data[data['服务器功率总和'] > 200]

data['pPUE'] = (data['服务器功率总和'] + data['空调总有功功率总和']) / data['服务器功率总和']

# "风机1转速", "风机2转速", "压缩机1转速", "压缩机2容量"
selected_columns = ['sampleTime'] + ['空调总有功功率总和', '服务器功率总和', 'pPUE'] + ac_power_columns
additional_columns = ["回风温度1", "送风温度1", "风机1转速", "风机2转速", "压缩机1容量", "压缩机2容量", "冷凝风机1转速"]
selected_columns += [col for col in data.columns if any(keyword in col for keyword in additional_columns)]
selected_columns = [element for element in selected_columns if "设定" not in element]

# 创建包含选定列的新DataFrame
selected_data = data[selected_columns]

# 选择"冷通道温度"相关数据
for fwq_i in fwq:
    additional_columns = ["FT" + JF + '-' + fwq_i]
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

all_csv = pd.concat([selected_data, averages_data], axis=1)
# 删除指定列中包含0的行
all_csv = all_csv[(all_csv.iloc[:, -5:] > 10).all(axis=1)]
all_csv.describe()


# 保存新的DataFrame到新的CSV文件
output_path = '/Users/kwok/Desktop/AI_for_env/dealData/dataCsv/' + JF + bOa + '.csv'
all_csv.to_csv(output_path, index=False)
# 对每列求平均（除了时间）
all_csv_avg = all_csv.iloc[:, 1:].mean(axis=0)
average_df = pd.DataFrame(all_csv_avg).T
# 保存新的DataFrame到新的CSV文件
output_path2 = '/Users/kwok/Desktop/AI_for_env/dealData/dataCsv/' + JF + bOa + 'AVG.csv'
average_df.to_csv(output_path2, index=False)
average_df
