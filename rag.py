import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import base64


db_config = {
    'host': 'sh-cdb-lo8m5ucm.sql.tencentcdb.com',
    'port': '59097',
    'user': 'root',
    'password': 'huayuan@2020',
    'database': 'ai_repo'
}

sql_template_cumulative_7days = """
-- 初始化运行总数变量
SET @running_total := 0;

-- 计算七天前的累计记录数
SET @initial_count = (
    SELECT COUNT(*)
    FROM #your_table# t
    WHERE t.create_time < #curr_date# - INTERVAL 7 DAY
    AND deleted = 0
    #extra_conditions#
);

-- 计算过去七天每一天的累计记录数
SELECT
    d.date,
    @running_total := IF(d.date = #curr_date# - INTERVAL 7 DAY, @initial_count, @running_total) + IFNULL(t.daily_count, 0) AS cumulative_count
FROM (
    SELECT 
        #curr_date# - INTERVAL seq DAY AS date
    FROM 
        (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7) AS seqs
) AS d
LEFT JOIN (
    SELECT
        DATE(t.create_time) AS date,
        COUNT(*) AS daily_count
    FROM
        #your_table# t
    WHERE
        t.create_time >= #curr_date# - INTERVAL 7 DAY AND t.create_time < #curr_date#
        AND t.deleted = 0
        #extra_conditions#
    GROUP BY
        DATE(t.create_time)
) AS t ON d.date = t.date
ORDER BY
    d.date;
"""

sql_template_active_user_7days = """
SELECT
    d.date,
    IFNULL(t.daily_count, 0) as daily_count
FROM (
    SELECT 
        #curr_date# - INTERVAL seq DAY AS date
    FROM 
        (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7) AS seqs
) AS d
LEFT JOIN (
    SELECT
        DATE(t.create_time) AS date,
        COUNT(DISTINCT t.user_id) AS daily_count
    FROM
        ai_llm_model_chat t
        WHERE
            t.create_time >= #curr_date# - INTERVAL 7 DAY AND t.create_time < #curr_date#
        GROUP BY
            DATE(t.create_time) 
        ORDER BY
            date
    ) AS t ON d.date = t.date
ORDER BY
    d.date; 1
"""

# 统计日期：
# 新增知识库总数：
# 用户与知识库关系：
# 新增文档总数：
# 用户与文档关系：
# 发生提问次数：
# TOP10用户
# TOP10知识库


def get_data(stat_date):
    print(f"统计日期: {stat_date}")
   
    #add one day
    next_date = stat_date + timedelta(days=1)

    # 连接到数据库
    conn = mysql.connector.connect(**db_config)

    # 创建一个游标对象
    cursor = conn.cursor()

    # 知识库总数
    total_kb = get_total_kb(cursor)
    # 新增用户知识库
    new_user_kbs = get_new_user_kbs(cursor, stat_date)
    #新增知识库
    new_kbs = get_new_kbs(cursor, stat_date)
    # 文档总数
    total_doc = get_total_doc(cursor)
    # 新增用户文档
    # new_user_docs = get_new_user_docs(cursor, stat_date)
    new_user_docs = []
    #新增文档
    new_docs = get_new_docs(cursor, stat_date)
    # 对话总数
    total_chat = get_total_chat(cursor, stat_date)
    #昨日对话用户总数
    yes_chat_user = get_chat_user(cursor, stat_date)
    # 按用户统计对话次数
    chat_users = get_chat_users(cursor, stat_date)
    # 按场景统计对话次数
    chat_scenes = get_chat_scenes(cursor, stat_date)
    #昨日活跃用户
    yesterday_user = get_yesterday_user(cursor, stat_date)
    # 知识库七日累计
    kb_7days_incr = get_kb_7days_incr(cursor, next_date)
    # 文档七日累计
    doc_7days_incr = get_doc_7days_incr(cursor, next_date)
    # 用户七日活跃度
    user_7days = get_user_7days(cursor, next_date)

    print(f"知识库总数: {total_kb}")

    for res in new_user_kbs[:10]:
        print(f"用户[{res['nickname']}]新增知识库：{res['kb_num']}")

    print(f"文档总数: {total_doc}")

    for res in new_user_docs[:10]:
        print(f"用户[{res['nickname']}]新增文档：{res['doc_num']}")

    print(f"对话总次数: {total_chat}")

    for res in chat_users[:10]:
        print(f"用户{res['nickname']}对话次数：{res['chat_num']}")

    for res in chat_scenes[:10]:
        print(f"场景[{res['scene_name']}]创建人[{res['nickname']}]对话次数：{res['chat_num']}")

    kb_dates = [result[0] for result in kb_7days_incr]
    kb_counts = [result[1] for result in kb_7days_incr]
    plot(kb_dates, kb_counts, 'kb_7days_incr.png')

    doc_dates = [result[0] for result in doc_7days_incr]
    doc_counts = [result[1] for result in doc_7days_incr]
    plot(doc_dates, doc_counts, 'doc_7days_incr.png')

    user_dates = [result[0] for result in user_7days]
    user_counts = [result[1] for result in user_7days]
    plot(user_dates, user_counts, 'user_7days.png')

    # 关闭游标和连接
    cursor.close()
    conn.close()

    return {
        "total_kb": total_kb,
        "new_user_kbs": new_user_kbs,
        "total_doc": total_doc,
        "new_user_docs": new_user_docs,
        "total_chat": total_chat,
        "chat_users": chat_users,
        "chat_scenes": chat_scenes,
        "kb_7days_incr": kb_7days_incr,
        "doc_7days_incr": doc_7days_incr,
        "user_7days": user_7days,
        "yesterday_user": yesterday_user,
        "new_docs": new_docs,
        "new_kbs": new_kbs,
        "yes_chat_user": yes_chat_user
    }

def plot(x, y, filename):
    # 绘制折线图
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o')
    # plt.title('Data Count from Current Date to 7 Days Ago')
    # plt.xlabel('Date')
    # plt.ylabel('Count')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 保存图表
    pic_filename = filename
    plt.savefig(pic_filename)


def get_users(cursor):
    cursor.execute(f"select id, username, nickname from system_users")

    # 获取列名
    columns = [desc[0] for desc in cursor.description]

    # 获取查询结果并转换为字典列表
    results = cursor.fetchall()

    users = {}

    for row in results:
        users[row[0]] = row[2]

    return users


def get_total_kb(cursor):
    cursor.execute("""
        select count(*) 
        from ai_rag_kb
        where deleted = 0
    """)

    result = cursor.fetchone()

    return result[0]

def get_yesterday_user(cursor,date):
    cursor.execute("""
        select count(distinct user_id)
        from ai_llm_model_chat
        where create_time like %s
    """, (f'%{date}%', ))

    result = cursor.fetchone()

    return result[0]

def get_chat_user(cursor, date):
    cursor.execute("""
    select count(user_id)
        from ai_rag_kb
        where date(create_time) = %s;
                   """, (date,))
    result = cursor.fetchone()

    return result[0]
def get_new_user_kbs(cursor, date):
    # 执行SQL查询
    cursor.execute("""
        select kb.user_id, users.nickname, count(*) as kb_num 
        from ai_rag_kb kb
        left join system_users users on kb.user_id = users.id 
        where date(kb.create_time) = %s 
        group by kb.user_id, users.nickname order by kb_num desc
    """, (date,))

    # 获取列名
    columns = [desc[0] for desc in cursor.description]

    # 获取查询结果并转换为字典列表
    results = cursor.fetchall()
    result_dicts = [dict(zip(columns, row)) for row in results]

    # result_dicts.sort(key=lambda m: m['kb_num'], reverse=True)

    # for res in result_dicts[:10]:
    #     print(f"用户[{res['nickname']}]新增知识库：{res['kb_num']}")
    return result_dicts

def get_new_kbs(cursor, date):
    cursor.execute("""
        select count(id)
        from ai_rag_kb
        where date(create_time) = %s;
            """, (date, ))
    result = cursor.fetchone()

    return result[0]

def get_total_doc(cursor):
    cursor.execute("""
        select count(*) 
        from ai_rag_kb_doc
        where deleted = 0
        """)

    result = cursor.fetchone()

    return result[0]


def get_kb_7days_incr(cursor, date_excluded):
    sql = get_cumulative_sql('ai_rag_kb', date_excluded)
    # 执行查询
    for result in cursor.execute(sql, multi=True):
        if result.with_rows:
            results = result.fetchall()
            return results

    return None


def get_doc_7days_incr(cursor, date_excluded):
    sql = get_cumulative_sql('ai_rag_kb_doc', date_excluded)
    # 执行查询
    for result in cursor.execute(sql, multi=True):
        if result.with_rows:
            results = result.fetchall()
            return results

    return None


def get_user_7days(cursor, date_excluded):
    sql = sql_template_active_user_7days.replace('#curr_date#', f"'{date_excluded}'")
    cursor.execute(sql)

    results = cursor.fetchall()

    return results


def get_cumulative_sql(table, date_excluded, extra_conditions=''):
    query = (sql_template_cumulative_7days.replace('#your_table#', table).replace('#curr_date#', f"'{date_excluded}'")
             .replace('#extra_conditions#', extra_conditions))

    return query




def get_new_docs(cursor, date):

    cursor.execute("""
        select count(id)
        from ai_rag_kb_doc
        where create_time like %s     
                   """ , (f'%{date}%',)
        )
    result = cursor.fetchone()

    return result[0]

    # 获取列名
    columns = [desc[0] for desc in cursor.description]

    # 获取查询结果并转换为字典列表
    results = cursor.fetchall()
    result_dicts = [dict(zip(columns, row)) for row in results]

    s = '新增文档：' + str(len(results))

    # result_dicts.sort(key=lambda m: m['doc_num'], reverse=True)

    # for res in result_dicts[:10]:
    #     print(f"用户[{res['nickname']}]新增文档：{res['doc_num']}")

    return result_dicts


def get_total_chat(cursor, date):
    # 执行SQL查询
    cursor.execute("""
        select count(*) as chat_num 
        from ai_llm_model_chat 
        where platform = 'huayuan_rag' and date(create_time)=%s
    """, (date,))

    # 获取查询结果并转换为字典列表
    result = cursor.fetchone()

    # print(f"总对话次数：{result}")

    return result[0]


def get_chat_users(cursor, date):
    # 执行SQL查询
    cursor.execute("""
        select chat.user_id, users.nickname, count(*) as chat_num 
        from ai_llm_model_chat chat
        left join system_users users on chat.user_id = users.id 
        where chat.platform = 'huayuan_rag' and date(chat.create_time) = %s 
        group by chat.user_id, users.nickname order by chat_num desc 
    """, (date,))

    # 获取列名
    columns = [desc[0] for desc in cursor.description]

    # 获取查询结果并转换为字典列表
    results = cursor.fetchall()
    result_dicts = [dict(zip(columns, row)) for row in results]

    # for res in result_dicts[:10]:
    #     print(f"用户{res['nickname']}对话次数：{res['chat_num']}")

    {
        'nickname':'xiaodong',
        'chat_num':10,
        'user_id':123
    }

    return result_dicts


def get_chat_scenes(cursor, date):
    # 执行SQL查询
    cursor.execute(f"""
        select scene.name as scene_name, users.nickname, count(*) as chat_num 
        from ai_llm_model_chat chat 
        left join ai_rag_scene scene on chat.scene_id = scene.id 
        left join system_users users on chat.user_id = users.id 
        where chat.platform = 'huayuan_rag' and date(chat.create_time)='{date}'
        group by chat.scene_id, scene.name, chat.user_id, users.nickname 
        order by chat_num desc
    """)

    # 获取列名
    columns = [desc[0] for desc in cursor.description]

    # 获取查询结果并转换为字典列表
    results = cursor.fetchall()
    result_dicts = [dict(zip(columns, row)) for row in results]

    # for res in results[:10]:
    #     print(f"场景[{res[0]}]创建人[{res[1]}]对话次数：{res[2]}")

    return result_dicts


def encode_file(file_path):
    with open(file_path, 'rb') as file:
        encoded = base64.b64encode(file.read())
        return encoded.decode('utf-8')
   

image1 = encode_file('kb_7days_incr.png')
image2 = encode_file('doc_7days_incr.png')
image3 = encode_file('user_7days.png')

if __name__ == '__main__':
    today = datetime.now().date()
    yesterday = today - timedelta(days =1)
    print(f"今天: {today}")
    print('------------------------')
    data = get_data(date(yesterday.year, yesterday.month, yesterday.day))
    print("-----------------------------------")
    with open('report.html', 'r') as f:
        content = f.read()

    content = content.replace('#report_date#', str(today))
    content = content.replace('#知识库新增#', str(data['new_kbs']) )
    content = content.replace('#知识库总数#', str(data['total_kb']))
    content = content.replace('#文档新增#', str(data['new_docs']) )
    content = content.replace('#文档总数#', str(data['total_doc']) )
    content = content.replace('#昨日对话次数#', str(data['total_chat']) )
    content = content.replace('#昨日活跃用户#', str(data['yesterday_user']))
    content = content.replace('#image11#', image1)
    content = content.replace('#image22#', image2)
    content = content.replace('#image33#', image3)

    top10_chat_users = ""
    for res in data['chat_users'][:10]:
        top10_chat_users += (f"<tr><td>{res['nickname']}</td><td>{res['chat_num']}</td></tr>\n")
    content = content.replace('#TOP10用户#', top10_chat_users)

    top10_chat_kcb = ""
    for res in data['chat_scenes'][:10]:
        top10_chat_kcb += (f"<tr><td>{res['scene_name']}</td><td>{res['chat_num']}</td></tr>\n")
    content = content.replace('#TOP10场景', top10_chat_kcb)

    with open('new.html', 'w') as f:
        f.write(content)
