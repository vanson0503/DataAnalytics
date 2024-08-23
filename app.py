from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['STATIC_FOLDER']):
    os.makedirs(app.config['STATIC_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Đọc và tiền xử lý dữ liệu
        data = pd.read_csv(filepath)
        data_html = data.to_html(classes='table table-striped', index=False)
        data = data.replace(['-', '', ' '], pd.NA)  # Thay thế các giá trị không hợp lệ bằng NaN
        data = data.dropna(thresh=len(data.columns) * 0.5, axis=0)
        data = data.dropna(thresh=len(data) * 0.5, axis=1)
        data = data.fillna(data.mean(numeric_only=True))

        # Chuyển đổi các cột liên quan sang kiểu số, bỏ qua các giá trị NaN
        columns_to_convert = ['AQI', 'CO', 'NO2', 'O3', 'Pressure', 'PM10', 'PM2.5', 'SO2']
        for column in columns_to_convert:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors='coerce')




        # Lưu dữ liệu đã xử lý
        processed_filepath = os.path.join(app.config['STATIC_FOLDER'], 'processed_' + file.filename)
        data.to_csv(processed_filepath)

        # Xử lý cột thời gian
        if 'Data Time' in data.columns:
            data['Data Time'] = pd.to_datetime(data['Data Time'], errors='coerce')
            data = data.drop_duplicates(subset=['Data Time'])  # Loại bỏ các giá trị trùng lặp trong cột thời gian
            data.set_index('Data Time', inplace=True)
            data['Month'] = data.index.month

        # Chuyển dữ liệu thành bảng HTML


        # Vẽ các biểu đồ
        plt.figure(figsize=(10, 6))
        sns.histplot(data['AQI'].dropna(), bins=30, kde=True)
        plt.title('Biểu đồ Histogram của Chỉ số AQI')
        plt.xlabel('Chỉ số AQI')
        plt.ylabel('Tần suất')
        histogram_aqi_path = os.path.join(app.config['STATIC_FOLDER'], 'histogram_aqi.png')
        plt.savefig(histogram_aqi_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.histplot(data['CO'].dropna(), bins=30, kde=True)
        plt.title('Biểu đồ Histogram của CO')
        plt.xlabel('CO')
        plt.ylabel('Tần suất')
        histogram_co_path = os.path.join(app.config['STATIC_FOLDER'], 'histogram_co.png')
        plt.savefig(histogram_co_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.histplot(data['NO2'].dropna(), bins=30, kde=True)
        plt.title('Biểu đồ Histogram của NO2')
        plt.xlabel('NO2')
        plt.ylabel('Tần suất')
        histogram_no2_path = os.path.join(app.config['STATIC_FOLDER'], 'histogram_no2.png')
        plt.savefig(histogram_no2_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.histplot(data['PM10'].dropna(), bins=30, kde=True)
        plt.title('Biểu đồ Histogram của PM10')
        plt.xlabel('PM10')
        plt.ylabel('Tần suất')
        histogram_pm10_path = os.path.join(app.config['STATIC_FOLDER'], 'histogram_pm10.png')
        plt.savefig(histogram_pm10_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.histplot(data['PM2.5'].dropna(), bins=30, kde=True)
        plt.title('Biểu đồ Histogram của PM2.5')
        plt.xlabel('PM2.5')
        plt.ylabel('Tần suất')
        histogram_pm25_path = os.path.join(app.config['STATIC_FOLDER'], 'histogram_pm25.png')
        plt.savefig(histogram_pm25_path)
        plt.close()

        plt.figure(figsize=(12, 8))
        sns.boxplot(data=data[['CO', 'NO2', 'PM10', 'PM2.5']].dropna())
        plt.title('Biểu đồ Boxplot của các chất ô nhiễm không khí')
        plt.xlabel('Chất ô nhiễm')
        plt.ylabel('Nồng độ')
        boxplot_path = os.path.join(app.config['STATIC_FOLDER'], 'boxplot.png')
        plt.savefig(boxplot_path)
        plt.close()

        if 'PM2.5' in data.columns:
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x=data['PM2.5'], y=data['AQI'])
            plt.title('Biểu đồ Scatter Plot giữa Chỉ số AQI và PM2.5')
            plt.xlabel('PM2.5')
            plt.ylabel('Chỉ số AQI')
            scatterplot_aqi_pm25_path = os.path.join(app.config['STATIC_FOLDER'], 'scatterplot_aqi_pm25.png')
            plt.savefig(scatterplot_aqi_pm25_path)
            plt.close()

        if 'Month' in data.columns:
            plt.figure(figsize=(12, 8))
            sns.boxplot(x='Month', y='AQI', data=data)
            plt.title('Biểu đồ Boxplot của Chỉ số AQI theo tháng')
            plt.xlabel('Tháng')
            plt.ylabel('Chỉ số AQI')
            boxplot_aqi_month_path = os.path.join(app.config['STATIC_FOLDER'], 'boxplot_aqi_month.png')
            plt.savefig(boxplot_aqi_month_path)
            plt.close()

            plt.figure(figsize=(12, 8))
            sns.boxplot(x='Month', y='CO', data=data)
            plt.title('Biểu đồ Boxplot của CO theo tháng')
            plt.xlabel('Tháng')
            plt.ylabel('CO')
            boxplot_co_month_path = os.path.join(app.config['STATIC_FOLDER'], 'boxplot_co_month.png')
            plt.savefig(boxplot_co_month_path)
            plt.close()

            plt.figure(figsize=(15, 10))
            sns.lineplot(data=data['AQI'].resample('M').mean())
            plt.title('Biểu đồ đường của Chỉ số AQI theo thời gian')
            plt.xlabel('Thời gian')
            plt.ylabel('Chỉ số AQI')
            lineplot_path = os.path.join(app.config['STATIC_FOLDER'], 'lineplot.png')
            plt.savefig(lineplot_path)
            plt.close()

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=data['NO2'], y=data['CO'])
        plt.title('Biểu đồ Scatter Plot giữa NO2 và CO')
        plt.xlabel('NO2')
        plt.ylabel('CO')
        scatterplot_no2_co_path = os.path.join(app.config['STATIC_FOLDER'], 'scatterplot_no2_co.png')
        plt.savefig(scatterplot_no2_co_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=data['PM10'], y=data['CO'])
        plt.title('Biểu đồ Scatter Plot giữa PM10 và CO')
        plt.xlabel('PM10')
        plt.ylabel('CO')
        scatterplot_pm10_co_path = os.path.join(app.config['STATIC_FOLDER'], 'scatterplot_pm10_co.png')
        plt.savefig(scatterplot_pm10_co_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=data['PM2.5'], y=data['NO2'])
        plt.title('Biểu đồ Scatter Plot giữa PM2.5 và NO2')
        plt.xlabel('PM2.5')
        plt.ylabel('NO2')
        scatterplot_pm25_no2_path = os.path.join(app.config['STATIC_FOLDER'], 'scatterplot_pm25_no2.png')
        plt.savefig(scatterplot_pm25_no2_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=data['AQI'], y=data['NO2'])
        plt.title('Biểu đồ Scatter Plot giữa AQI và NO2')
        plt.xlabel('AQI')
        plt.ylabel('NO2')
        scatterplot_aqi_no2_path = os.path.join(app.config['STATIC_FOLDER'], 'scatterplot_aqi_no2.png')
        plt.savefig(scatterplot_aqi_no2_path)
        plt.close()

        plt.figure(figsize=(12, 8))
        correlation_matrix = data[['AQI', 'CO', 'NO2', 'PM10', 'PM2.5']].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Biểu đồ Heatmap của Ma trận Tương quan')
        heatmap_path = os.path.join(app.config['STATIC_FOLDER'], 'heatmap.png')
        plt.savefig(heatmap_path)
        plt.close()

        # Vẽ biểu đồ phân tán (Pairplot) của tất cả các chất ô nhiễm
        plt.figure(figsize=(15, 10))
        pairplot = sns.pairplot(data[['AQI', 'CO', 'NO2', 'PM10', 'PM2.5']].dropna())
        pairplot.fig.suptitle('Biểu đồ phân tán (Pairplot) của các chất ô nhiễm không khí', y=1.02)
        pairplot_path = os.path.join(app.config['STATIC_FOLDER'], 'pairplot.png')
        pairplot.savefig(pairplot_path)

        return render_template('index.html',
                               data_table=data_html,
                               hist_aqi_path='static/uploads/histogram_aqi.png',
                               hist_co_path='static/uploads/histogram_co.png',
                               hist_no2_path='static/uploads/histogram_no2.png',
                               hist_pm10_path='static/uploads/histogram_pm10.png',
                               hist_pm25_path='static/uploads/histogram_pm25.png',
                               box_path='static/uploads/boxplot.png',
                               scatter_aqi_pm25_path='static/uploads/scatterplot_aqi_pm25.png' if 'PM2.5' in data.columns else None,
                               box_aqi_month_path='static/uploads/boxplot_aqi_month.png' if 'Month' in data.columns else None,
                               box_co_month_path='static/uploads/boxplot_co_month.png' if 'Month' in data.columns else None,
                               line_path='static/uploads/lineplot.png' if 'Month' in data.columns else None,
                               scatter_no2_co_path='static/uploads/scatterplot_no2_co.png',
                               scatter_pm10_co_path='static/uploads/scatterplot_pm10_co.png',
                               scatter_pm25_no2_path='static/uploads/scatterplot_pm25_no2.png',
                               scatter_aqi_no2_path='static/uploads/scatterplot_aqi_no2.png',
                               heat_path='static/uploads/heatmap.png',
                               pair_path='static/uploads/pairplot.png',
                               processed_file=os.path.basename(processed_filepath))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['STATIC_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
