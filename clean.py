import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def main():
    print('正在读取数据...')
    
    data = []
    with open('dirty_data.csv', 'r', encoding='utf-8') as f:
        import csv
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    
    df = pd.DataFrame(data[1:], columns=data[0])
    print('原始数据读取完成！')
    print()

    original_df = df.copy()

    print('开始数据清洗...')
    print()

    numeric_columns = ['年龄', '收入', '购买金额']
    
    print('转换数值列...')
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    print()

    print('识别并处理异常值...')
    for col in numeric_columns:
        if col == '年龄':
            outlier_mask = (~df[col].isna()) & ((df[col] < 0) | (df[col] > 120))
        else:
            temp_data = df[col].dropna()
            Q1 = temp_data.quantile(0.25)
            Q3 = temp_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_mask = (~df[col].isna()) & ((df[col] < lower_bound) | (df[col] > upper_bound))
        
        if outlier_mask.sum() > 0:
            print(f'{col} 列发现 {outlier_mask.sum()} 个异常值')
            df.loc[outlier_mask, col] = np.nan
    print()

    print('填充缺失值...')
    for col in numeric_columns:
        mean_val = df[col].mean()
        df[col] = df[col].fillna(mean_val)
        print(f'{col} 列填充均值: {mean_val:.2f}')
    print()

    print('处理日期格式...')
    def parse_date(date_str):
        if pd.isna(date_str):
            return pd.NaT
        date_str = str(date_str).strip()
        if not date_str or date_str.lower() == 'nan':
            return pd.NaT
        
        for fmt in ['%Y-%m-%d', '%Y/%m/%d']:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        
        try:
            return pd.to_datetime(date_str)
        except:
            return pd.NaT

    df['购买日期'] = df['购买日期'].apply(parse_date)
    print(f'日期列处理完成，非空数量: {df["购买日期"].notna().sum()}')
    print()

    print('保存清洗后的数据...')
    output_df = df.copy()
    output_df['购买日期'] = output_df['购买日期'].dt.strftime('%Y-%m-%d')
    output_df.to_csv('final_data.csv', index=False, encoding='utf-8-sig')
    print('final_data.csv 保存完成！')
    print()

    print('生成对比直方图...')
    fig, axes = plt.subplots(len(numeric_columns), 2, figsize=(14, 4*len(numeric_columns)))

    for i, col in enumerate(numeric_columns):
        original_data = pd.to_numeric(original_df[col], errors='coerce').dropna()
        axes[i, 0].hist(original_data, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        axes[i, 0].set_title(f'{col} - 清洗前', fontsize=12)
        axes[i, 0].set_xlabel(col)
        axes[i, 0].set_ylabel('频数')
        axes[i, 0].grid(axis='y', alpha=0.3)
        
        axes[i, 1].hist(df[col], bins=10, alpha=0.7, color='lightgreen', edgecolor='black')
        axes[i, 1].set_title(f'{col} - 清洗后', fontsize=12)
        axes[i, 1].set_xlabel(col)
        axes[i, 1].set_ylabel('频数')
        axes[i, 1].grid(axis='y', alpha=0.3)
        
        if col == '年龄':
            axes[i, 0].set_xlim(0, 220)
            axes[i, 1].set_xlim(0, 100)
        elif col == '收入':
            min_income = min(original_data.min(), df[col].min())
            max_income = max(original_data.max(), df[col].max())
            axes[i, 0].set_xlim(min_income - 1000, max_income + 1000)
            axes[i, 1].set_xlim(min_income - 1000, max_income + 1000)
        elif col == '购买金额':
            min_amount = min(original_data.min(), df[col].min())
            max_amount = max(original_data.max(), df[col].max())
            axes[i, 0].set_xlim(max(0, min_amount - 100), max_amount + 100)
            axes[i, 1].set_xlim(max(0, min_amount - 100), max_amount + 100)

    plt.tight_layout()
    plt.savefig('comparison_histogram.png', dpi=300, bbox_inches='tight')
    print('comparison_histogram.png 保存完成！')
    print()

    print('数据清洗全部完成！')
    print('最终数据前5行:')
    print(df.head())
    return 0

if __name__ == '__main__':
    sys.exit(main())
