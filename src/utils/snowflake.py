# -*- coding:utf-8 -*-
import time
import logging

__all__ = ["generator", "generate_id"]

log = logging.getLogger(__name__)

twepoch = 1288834974657

# 64位ID的划分
worker_id_bits = 5
data_center_id_bits = 5
sequence_bits = 12

# 最大取值计算
max_worker_id = -1 ^ (-1 << worker_id_bits)
max_data_center_id = -1 ^ (-1 << data_center_id_bits)

# 位移偏移计算
worker_id_shift = sequence_bits
data_center_id_shift = sequence_bits + worker_id_bits
timestamp_left_shift = sequence_bits + worker_id_bits + data_center_id_bits

# 序号循环掩码
sequence_mask = -1 ^ (-1 << sequence_bits)


def snowflake_to_timestamp(_id):
    _id = _id >> 22  # strip the lower 22 bits
    _id += twepoch  # adjust for twitter epoch
    _id = _id / 1000  # convert from milliseconds to seconds
    return _id


def generator(worker_id, data_center_id, sleep=lambda x: time.sleep(x / 1000.0)):
    """
    :param worker_id: 机器ID
    :param data_center_id: 机器区域ID
    :param sleep: 机器区域ID
    :return:
    """
    assert 0 <= worker_id <= max_worker_id
    assert 0 <= data_center_id <= max_data_center_id

    last_timestamp = -1
    # 起始ID
    sequence = 0

    while True:
        timestamp = int(time.time() * 1000)

        # 时间回拨
        if last_timestamp > timestamp:
            log.warning(
                    "clock is moving backwards. waiting until %i" % last_timestamp)
            sleep(last_timestamp - timestamp)
            continue

        if last_timestamp == timestamp:
            sequence = (sequence + 1) & sequence_mask
            if sequence == 0:
                log.warning("sequence overrun")
                sequence = -1 & sequence_mask
                sleep(1)
                continue
        else:
            sequence = 0

        last_timestamp = timestamp
        yield (((timestamp - twepoch) << timestamp_left_shift) |
               (data_center_id << data_center_id_shift) |
               (worker_id << worker_id_shift) |
               sequence)


def generate_id():
    """
    生成雪花id
    """
    return generator(1, 1).__next__()


if __name__ == '__main__':
    print(generate_id())
