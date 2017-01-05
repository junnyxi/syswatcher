#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import psutil
from settings import STORE_SQLITE
import logging
import json

from model.models import Record
from app import db

logger_main = logging.getLogger('watcher_main')
logger_cpu = logging.getLogger('watcher_cpus')


class SystemWatcher(object):
    """
    Get Linux system base information , e.g. CPU, MEM, DISK
    """
    DEFAULT_INTERVAL = 5
    CPU_USAGE_KEY = "cpu"
    MEM_USAGE_KEY = "mem"
    DISK_ALL_USAGE_KEY = "disk"
    NETWORK_INFO = 'network'
    SWAP_USAGE_KEY = 'swap'

    def __init__(self, store_type=''):
        if store_type == STORE_SQLITE:
            pass

    @staticmethod
    def save(d_type, data):
        if not isinstance(data, str):
            data = json.dumps(data)
        record = Record(data=data, type=d_type)
        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            print 'error...' + str(e)

    def get_cpu_usage(self, inter=DEFAULT_INTERVAL):
        cpu_usage = psutil.cpu_percent(interval=inter, percpu=True)
        data = cpu_usage, sum(cpu_usage)
        self.save(self.CPU_USAGE_KEY, data)
        print data

    def get_mem_usage(self, base_unit='M'):
        """
        data:
        ['available', 'used', 'cached', 'free', 'inactive', 'active', 'shared', 'total', 'buffers']
        total: 内存的总大小.
        available: 可以用来的分配的内存，不同系统计算方式不同； Linux下的计算公式:free+ buffers +　cached
        percent: 已经用掉内存的百分比 (total - available) / total 100.
        used: 已经用掉内存大小，不同系统计算方式不同
        free: 空闲未被分配的内存，Linux下不包括buffers和cached
        active: (UNIX): 最近使用内存和正在使用内存。
        inactive: (UNIX): 已经分配但是没有使用的内存
        buffers: (Linux, BSD): 缓存，linux下的Buffers
        cached:(Linux, BSD): 缓存，Linux下的cached.
        shared: (BSD): 缓存

        :param base_unit:
        :return:
        """
        _num = self.get_base_unit(base_unit)
        data = psutil.virtual_memory()
        mem_info = dict()
        for k, v in data.__dict__.items():
            if k != 'percent':
                mem_info[k] = v / _num
        print mem_info
        self.save(self.MEM_USAGE_KEY, mem_info)

    def get_swap_info(self, base_unit='M'):
        """
        单位为字节, return is Mib
        total:
        used:
        free:
        percent:
        sin:    从磁盘调入是swap的大小
        sout:   从swap调出到disk的大小

        :param base_unit:
        :return:
        """
        _num = self.get_base_unit(base_unit)
        data = psutil.swap_memory()
        mem_info = dict()
        for k, v in data.__dict__.items():
            if k != 'percent':
                mem_info[k] = v / _num
        print mem_info
        self.save(self.SWAP_USAGE_KEY, mem_info)

    def get_sys_disk_info(self,  base_unit='G'):
        _num = self.get_base_unit(base_unit)
        partition_info = psutil.disk_partitions()
        total = used = avail = 0
        for partition in partition_info:
            partition_total, partition_used, partition_avail = SystemWatcher.get_target_disk_usage(partition.mountpoint)
            total += partition_total
            used += partition_used
            avail += partition_avail
        return total / _num, used / _num, avail / _num

    @staticmethod
    def get_target_disk_usage(file_dir):
        dir_info = psutil.disk_usage(file_dir)
        return dir_info.total, dir_info.used, dir_info.free

    def get_disk_usage(self, base_unit='G'):
        database_total, database_used, database_avail = self.get_sys_disk_info(base_unit)
        all_usage = {'avail': database_avail, 'total': database_total, 'used': database_used}
        print all_usage
        self.save(self.DISK_ALL_USAGE_KEY, all_usage)

    def get_network_info(self):
        """
        ['packets_sent', 'bytes_recv', 'packets_recv', 'dropin', 'dropout', 'bytes_sent', 'errout', 'errin']
        bytes_sent: 发送的字节数
        bytes_recv: 接收的字节数
        packets_sent: 发送到数据包的个数
        packets_recv: 接受的数据包的个数
        errin:
        errout: 发送数据包错误的总数
        dropin: 接收时丢弃的数据包的总数
        dropout: 发送时丢弃的数据包的总数(OSX和BSD系统总是0)
        default 字节数
        :return:
        """
        data = psutil.net_io_counters()
        info = dict()
        for k, v in data.__dict__.items():
            info[k] = v / 1024
        print info.keys()
        print info
        self.save(self.NETWORK_INFO, info)

    @staticmethod
    def get_base_unit(name='M'):
        _num = 1024*1024
        if name == 'M':
            return _num
        elif name == 'G':
            return _num * 1024
        else:
            return _num

    def get_process(self):
        procs = None
        for x in range(2):
            time.sleep(5)
            procs = self._get_process()

        if procs:
            procs = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)
        else:
            print 'No data at all.'

        # print str(time.time()) + ' >>>'
        # for p in procs:
        #     print p
        logger_cpu.info('CPU_DATA' + str(time.time()) + '>>>')
        logger_cpu.info(procs)
        logger_main.info('='*20 + str(time.time()))

    @staticmethod
    def _get_process():
        procs = list()
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'num_threads', 'exe'])
                # pinfo = proc.as_dict('cpu_times')
            except psutil.NoSuchProcess:
                pass
            else:
                if pinfo['cpu_percent'] > 0.0:
                    procs.append(pinfo)

        return procs


def watcher_main():
    watcher = SystemWatcher()

    # watcher.get_cpu_usage()
    # watcher.get_mem_usage()
    # watcher.get_disk_usage()
    # watcher.get_network_info()
    # watcher.get_swap_info()
    watcher.get_process()

if __name__ == "__main__":
    while True:
        watcher_main()
        print '=' * 50
        time.sleep(1)
    # watcher_main()
