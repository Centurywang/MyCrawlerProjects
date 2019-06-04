from threading import Thread
import execjs
import requests
import json

def get_data(pageCount):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin' : 'https://sou.zhaopin.com',
        'Referer': 'https://sou.zhaopin.com/?p={}&jl=702&sf=0&st=0&kw=%E5%A4%A7%E6%95%B0%E6%8D%AE&kt=3'.format(pageCount),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    js = '''"f097795abafd429bb0b65846ac9944b7-" + (new Date()).valueOf() + "-" + parseInt(Math.random() * 1000000)'''
    url_id = execjs.eval(js)
    data_url = 'https://fe-api.zhaopin.com/c/i/sou?start={}&pageSize=90&cityId=702&salary=0,0&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=大数据&kt=3&=0&_v=0.14145840&x-zp-page-request-id={}'.format(pageCount*90 if pageCount>0 else 0,url_id)
    response = requests.get(data_url,headers=headers).text
    #print(response)
    data = json.loads(response)

    data = data['data']['results']
    if len(data) > 2:
        return data
    else:
        return None

def save_to_json(data,file_name):
    '''保存到json文件'''
    data = json.dumps(data)
    file_name = file_name+'.json'
    with open(file_name,'w')as f:
        f.write(data)
        print(file_name+'保存完成')

def handel_data(data):
    '''处理数据'''
    result = []
    for d in data:
        work = {}
        work['company_name'] = d['company']['name']
        work['job_name'] = d['jobName']
        work['salary'] = d['salary']
        work['work_city'] = d['city']['display']
        work['working_exp'] = d['workingExp']['name']
        work['edu_level'] = d['eduLevel']['name']
        work['welfare'] = d['jobTag']['searchTag']
        work['update_date'] = d['updateDate']
        work['skill_required'] = d['extractSkillTag']
        result.append(work)
    print(result)
    return result

def thread_crawl(start,step):
    '''多线程函数
    参数：
        start:开始页数
        step:步长
    '''
    i = start
    while True:
        data = get_data(i)
        if data == None:
            break
        i += step
        data = handel_data(data)
        result.extend(data)

if __name__ == '__main__':
    result = []

    '''
    i = 0
    while True:
        data = get_data(i)
        if data == None:
            break
        i += 1
        data = handel_data(data)
        result.extend(data)
    '''
    # 多线程
    th1 = Thread(target=thread_crawl,args=(0,3))
    th2 = Thread(target=thread_crawl,args=(1,3))
    th3 = Thread(target=thread_crawl,args=(2,3))
    th1.start()
    th2.start()
    th3.start()
    while True:
        if th1.isAlive() == False and th2.isAlive() == False and th3.isAlive() == False:
            save_to_json(data=result,file_name='大数据职位')
            break





