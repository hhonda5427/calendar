import csv
import datetime

# Read calendar.csv file and store its contents in an array
calendar_data = []
is_first_row = True
with open('syukujitsu.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if not is_first_row and row:
            calendar_data.append(row)
        is_first_row = False   

# Prompt for start_date and end_date
print()
print("*******************************************")
print("勤務表で使用する休日ファイルを作成します。")
print("カレンダーの原本は内閣府が発行する【syukujitsu.csv】です。")

print("データは1列目に日付、2列目に休日名となっています。")
print("作成されるファイル名は【tokai-calendar.csv】です。")  
print()

print("このデータは1955年の祝日から記載されているので、必要に応じてデータを削除してください")
print("祝日でも診療日となる場合は、そのデータを削除するか、あるいは接頭語に'#'を付加してください。読み飛ばしを行います。")
print()    
print("カレンダー作成の開始日(YYYY/MM/DD)と終了日(YYYY/MM/DD)を入力してください。")
print("*******************************************")
print()

start_date = input("開始日を入力 (YYYY/MM/DD): ")
end_date = input("終了日を入力 (YYYY/MM/DD): ")

# Convert input strings to date objects
try:
    start_date = datetime.datetime.strptime(start_date, "%Y/%m/%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y/%m/%d").date()

    if start_date >= end_date:
        print("エラー: 開始日よりも終了日が未来または同じ日付です。")
        exit()
except ValueError:
    print("入力された値が正しくありません。プログラムを終了します。")
    exit()

# Generate dates for Sundays, 2nd Saturdays, and 4th Saturdays between start_date and end_date
current_date = start_date
while current_date <= end_date:
    dates_to_generate = []
    if current_date.weekday() == 6:  # Sunday
        dates_to_generate.append(current_date.strftime("%Y/%m/%d"))
        dates_to_generate.append('日曜日')  # Sunday
    elif current_date.weekday() == 5:  # Saturday
        if (current_date.day // 7) == 1:  # 2nd Saturday
            dates_to_generate.append(current_date.strftime("%Y/%m/%d"))
            dates_to_generate.append('第2土曜日')
        if (current_date.day // 7) == 3:  # 4th Saturday
            dates_to_generate.append(current_date.strftime("%Y/%m/%d"))
            dates_to_generate.append('第4土曜日')
    
    if dates_to_generate:
        found = False
        # calendar_dataを検索し、同じ日付があるか調べる
        for data in calendar_data:
            if datetime.datetime.strptime(data[0], "%Y/%m/%d").date() == current_date:
                # 同じ日付があり、かつ休日名が空であれば追加
                if data[1] == '':
                    print(len(data))
                    data[1] = dates_to_generate[1]
                found = True
                break

        if not found:
            calendar_data.append(dates_to_generate)
       
    current_date += datetime.timedelta(days=1)


calendar_data.sort(key=lambda x: datetime.datetime.strptime(x[0], "%Y/%m/%d").date())

with open('tokai-calendar.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for data in calendar_data:
        writer.writerow(data)


