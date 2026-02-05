import os
import json
import time
import uuid
import requests
import pandas as pd
from collections import defaultdict
from moviepy.editor import VideoFileClip
from oss import oss_upload

***REMOVED*** 填入控制台获取的app id和access token
appid = "6824042657"
token = "nHYpO_wiMT56dvRHNlbgdC0YOrvbD7as"
submit_url = "https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/submit"
query_url = "https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/query"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)


def url2file(url, savepath=None):
    assert savepath is not None, 'The savepath should not be None'
    with open(savepath, 'wb') as f:
        f.write(requests.get(url).content)


def s2hms(x):
    m = int(x) // 60
    s = int(x) % 60
    ms = int((x - int(x)) * 1000)
    h = m // 60
    m = m % 60
    hms = f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return hms


def submit_task(audio_url):
    task_id = str(uuid.uuid4())

    headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc",
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1"
    }

    request = {
        "user": {
            "uid": "fake_uid"
        },
        "audio": {
            "url": audio_url,
            ***REMOVED*** "format": "mp3",
            ***REMOVED*** "codec": "map3",
            ***REMOVED*** "rate": 48000,
            ***REMOVED*** "bits": 16,
            ***REMOVED*** "channel": 2
        },
        "request": {
            "model_name": "bigmodel",
            "enable_channel_split": False,
            "enable_speaker_info": True,
            "enable_ddc": True,
            "enable_punc": True,
            "enable_itn": True,
            ***REMOVED*** "show_utterances": True,
            ***REMOVED*** "vad_segment": True,
            "corpus": {
                ***REMOVED*** "boosting_table_name": "test",
                "correct_table_name": "",
                "context": ""
            }
        }
    }
    print(f'Submit task id: {task_id}')
    response = requests.post(submit_url, data=json.dumps(request), headers=headers)
    if 'X-Api-Status-Code' in response.headers and response.headers["X-Api-Status-Code"] == "20000000":
        print(f'Submit task response header X-Api-Status-Code: {response.headers["X-Api-Status-Code"]}')
        print(f'Submit task response header X-Api-Message: {response.headers["X-Api-Message"]}')
        x_tt_logid = response.headers.get("X-Tt-Logid", "")
        print(f'Submit task response header X-Tt-Logid: {response.headers["X-Tt-Logid"]}\n')
        return task_id, x_tt_logid
    else:
        print(f'Submit task failed and the response headers are: {response.headers}')
        exit(1)
    return task_id


def query_task(task_id, x_tt_logid):
    headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc",
        "X-Api-Request-Id": task_id,
        "X-Tt-Logid": x_tt_logid  ***REMOVED*** 固定传递 x-tt-logid
    }

    response = requests.post(query_url, json.dumps({}), headers=headers)

    if 'X-Api-Status-Code' in response.headers:
        print(f'Query task response header X-Api-Status-Code: {response.headers["X-Api-Status-Code"]}')
        print(f'Query task response header X-Api-Message: {response.headers["X-Api-Message"]}')
        print(f'Query task response header X-Tt-Logid: {response.headers["X-Tt-Logid"]}\n')
    else:
        print(f'Query task failed and the response headers are: {response.headers}')
        exit(1)
    return response


def asr(audio_url):
    task_id, x_tt_logid = submit_task(audio_url)
    while True:
        response = query_task(task_id, x_tt_logid)
        code = response.headers.get('X-Api-Status-Code', "")
        if code == '20000000':  ***REMOVED*** task finished
            print("SUCCESS!")
            return response.json()
        elif code != '20000001' and code != '20000002':  ***REMOVED*** task failed
            print("FAILED!")
            return None
        time.sleep(1)


def asr2info(video_path, output_dir, audio_path=None, overwrite=False):
    ensure_dir(output_dir)
    if audio_path == None:
        audio_path = f'{output_dir}/task.mp3'
    asr_path = f'{output_dir}/asr.json'
    para_path = f'{output_dir}/para.csv'

    if not os.path.exists(audio_path):
        get_audio(video_path, audio_path)
    
    if overwrite:
        get_audio(video_path, audio_path)

    audio_url = oss_upload(audio_path)
    asr_data = asr(audio_url)
    if not asr_data:
        return False
    with open(asr_path, 'w', encoding='utf-8') as f:
        json.dump(asr_data, f, ensure_ascii=False, indent=4)
    sentences = asr_data['result']['utterances']

    data = []
    for i,sent in enumerate(sentences):
        data.append((i, sent['text'], [sent['start_time'] / 1000, sent['end_time'] / 1000], sent['additions']['speaker']))
    df = pd.DataFrame(data, columns=['id', 'para', 'timestamp', 'speaker'])
    df.to_csv(para_path, index=False)

    return True


if __name__ == '__main__':
    ***REMOVED*** audio_url = "https://ttc-advisory-oss.oss-cn-hangzhou.aliyuncs.com/lark_audio/int/T_APLA_1941058348698869760.mp3"
    ***REMOVED*** data = asr(audio_url)
    ***REMOVED*** with open('output/asr.json', 'w', encoding='utf-8') as f:
    ***REMOVED***     json.dump(data, f, ensure_ascii=False, indent=4)

    asr2info('../data/task.mp4', output_dir='output')
