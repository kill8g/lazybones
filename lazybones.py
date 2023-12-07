import logging
import distance
import jieba
import yaml
import time
import argparse
import signal
import sys
import os
import json
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress

console = Console()
jieba.setLogLevel(logging.WARNING)

class Lazybones:
    def __init__(self, stopwords_path, cmds_path):
        self._running = False

        try:
            self.stopwords = []
            for line in open(stopwords_path, encoding = 'utf-8'):
                self.stopwords.append(line)
        except Exception as e:
            pass

        try:
            self.cmds = []
            with open('cmds.yaml', 'r', encoding = 'utf-8') as f:
                self.cmds = yaml.safe_load(f)['cmds']
        except Exception as e:
            pass

        try:
            self.cache_token = {}
            with open(".cache.json", "r") as f:
                self.cache_token = json.loads(f.read())
        except Exception as e:
            pass

    def tokenizer(self, text):
        if text in self.cache_token:
            return self.cache_token[text]

        # 使用结巴分词对字符串进行分词
        words = jieba.cut(text)
        # 过滤停用词
        filtered_words = [word for word in words if word not in self.stopwords]
        # 缓存下来, 下次使用
        self.cache_token[text] = filtered_words
        # 返回过滤后的词语列表
        return filtered_words

    def sorensen(self, prompt_token, desc_token):
        return distance.sorensen(prompt_token, desc_token)

    def similarity(self, prompt, bar = False):
        if len(prompt) == 0:
            return None
        if len(self.cmds) == 0:
            return None

        cmds = None
        minimum = 1.0
        prompt_token = self.tokenizer(prompt)
        # with Progress() as progress:
        if bar:
            progress = Progress()
            progress.start()
            task = progress.add_task("[green]Processing...", total = len(self.cmds))
        for record in self.cmds:
            if bar:
                progress.update(task, advance = 1)
            for desc in record['desc']:
                score = self.sorensen(prompt_token, self.tokenizer(desc))
                if score == 0:
                    if bar:
                        progress.update(task, advance = 100)
                        progress.stop()
                    return record['cmd'], 0
                if score < minimum:
                    minimum = score
                    cmds = record['cmd']
        if bar:
            progress.stop()
        return cmds, minimum

    def run(self):
        return self._running

    def stop(self):
        self._running = False

    def start(self):
        self._running = True

    def flush_cache(self):
        cache = {}
        with Progress() as progress:
            task = progress.add_task("[green]Processing...", total = len(self.cmds))
            for record in self.cmds:
                progress.update(task, advance = 1)
                for desc in record['desc']:
                    token = self.tokenizer(desc)
                    cache[desc] = token

        json_data = json.dumps(cache, indent = 4)
        with open(".cache.json", "w") as f:
            f.write(json_data)

    def run_shell(self, shell):
        cmd = subprocess.Popen(shell, 
            stdin = subprocess.PIPE, 
            stderr = sys.stderr, 
            close_fds = True,
            stdout = sys.stdout, 
            universal_newlines = True, 
            shell = True, 
            bufsize = 1
        )
        cmd.communicate()
        return cmd.returncode

def signal_handler(*keys):
    console.print(Markdown('*Bye.*'))
    sys.exit()

def output(cmds):
    if cmds == None:
        console.print("未找到", style = "red")
    else:
        for cmd in cmds:
            console.print(Markdown("```shell\n%s\n```" % cmd))

def interaction(lz, args):
    lz.start()
    while lz.run():
        try:
            text = input('> ')
            if len(text) > 0:
                if text == 'quit':
                    break
                if text[0] == '!':
                    lz.run_shell(text[1:])
                else:
                    cmds, score = lz.similarity(text)
                    output(cmds)
        except Exception as e:
            print(e)
            lz.stop()
    console.print(Markdown('*Bye.*'))

def single(text):
    cmds, score = lz.similarity(text)
    output(cmds)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interaction", action = "store_true", help = "交互模式")
    parser.add_argument("-f", "--flush", action = "store_true", help = "刷新cmds.yaml, 对desc进行预分词处理")
    parser.add_argument("-t", "--text", help = "查询内容, 首字符是!将会把内容当作命令执行")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    args = parse_args()
    lz = Lazybones('stopwords_cn.txt', 'cmds.yaml')
    if args.flush:
        lz.flush_cache()
    if args.text == None and not args.interaction:
        sys.exit()
    if args.interaction == True:
        interaction(lz, args)
    else:
        single(args.text)


