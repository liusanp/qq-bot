import yt_dlp
import os
import subprocess
import m3u8
import requests
import re
from tqdm import tqdm


def down_video(video_url, id):
    ydl_opts = {
        'cookiesfrombrowser': ('firefox', ),
        'paths': {
            'home': 'data/',
            'temp': 'temp/',
        },
        'outtmpl': f'{id}.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        vinfo = ydl.sanitize_info(info)
        # print(vinfo)
        title = vinfo['title']
        desc = vinfo['description']
        video_id = vinfo['id']
        thumbnail = vinfo['thumbnail']
        ydl.download(video_url)
        return title, desc, video_id, thumbnail
    

def down_zip_video(video_url, id):
    title, desc, _ = down_video(video_url, id)
    zip_video(f'data/{id}.mp4')
    return title, desc
    
    
def is_file_greater_than(file_path, unit=10):
    # 获取文件大小（字节）
    file_size = os.path.getsize(file_path)
    # 将10MB转换为字节
    mb_in_bytes = unit * 1024 * 1024
    # 返回判断结果
    return file_size > mb_in_bytes


def zip_video(file_path):
    if not is_file_greater_than(file_path):
        return
    temp_path = 'data/temp/zip-' + os.path.basename(file_path)
    crf = 40
    need_zip = True
    while(need_zip):
        command = [
            'ffmpeg', 
            '-y', 
            '-i', file_path, 
            '-c:v', 'hevc', 
            '-profile:v', 'main10', 
            '-c:a', 'aac', 
            '-preset', 'faster', 
            '-crf', str(crf), 
            temp_path
        ]
        subprocess.run(command)
        need_zip = is_file_greater_than(temp_path)
        crf += 5
    os.replace(temp_path, file_path)
    
    
def download_m3u8(m3u8_url, output_dir='data/segments'):
    # 创建目录以存储视频片段
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 下载并解析 M3U8 文件
    m3u8_obj = m3u8.load(m3u8_url)
    file_list_path = os.path.join(output_dir, os.path.basename(m3u8_url))
    idx = file_list_path.rindex(".")
    file_list_path = file_list_path[0:idx] + '.txt'
    # 下载每个视频片段
    with open(file_list_path, 'w') as listf:
        for segment in tqdm(m3u8_obj.segments):
            segment_url = segment.uri
            match = re.match(r'^(.+http).+', segment_url)
            if match:
                segment_url = segment_url.replace(match.group(1), 'http')
            segment_name = os.path.join(output_dir, os.path.basename(segment_url))

            if segment_url.find('http') != 0:
                continue
            # 下载片段
            with requests.get(segment_url, stream=True) as r:
                r.raise_for_status()
                with open(segment_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # print(f'Downloaded {segment_name}')
            listf.write(f"file '{os.path.basename(segment_url)}'\n")
    merge_videos(file_list_path)
            
            
def merge_videos(video_files):
    idx = video_files.rindex(".")
    output_file = video_files[0:idx] + '.mp4'
    # 调用 FFmpeg 进行合并
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', video_files,
        '-c', 'copy',
        '-crf', '28',
        output_file
    ]
    # 执行命令
    subprocess.run(cmd, check=True)
        
        
if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/BV1CT4y157Z2'
    down_video(url, 12345)
    # print(is_file_greater_than('data/1234.mp4'))
    # zip_video('data/12345.mp4')
    # download_m3u8(url)
    # down_zip_video(url, 12345)