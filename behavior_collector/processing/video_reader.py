import cv2
import threading
import queue
from numpy import ndarray
from collections import deque
import time

# from dataclasses import dataclass


IMAGE_BUFFER_SIZE = 100
FORWARD_FRAME = -100
BACKWARD_FRAME = -200


def convert_frame(func):
    def wrapper(*args, **kwargs):
        frame = func(*args, **kwargs)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return wrapper


class ThreadVideoReader:
    def __init__(self, file_path):
        self.cap = cv2.VideoCapture(file_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        self.cur_frame = 0
        self.buffer = deque()
        self.buffer_range = [0, 0]  # [start_index, end_index]
        self.buffer_lock = threading.Lock()

        self.read_thread_active = True
        self.read_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.read_thread.start()
        
    def _reader_loop(self):
        while self.read_thread_active:
            with self.buffer_lock:
                if self.buffer_range[1] - self.cur_frame >= IMAGE_BUFFER_SIZE//2:
                    continue
                
                if self.buffer_range[1] < self.total_frames - 1:
                    ret, frame = self.cap.read()
                    if not ret:
                        continue
                    
                    if self.buffer_range[1] - self.buffer_range[0] >= IMAGE_BUFFER_SIZE:
                        self.buffer.append(frame)
                        self.buffer.popleft()
                        self.buffer_range = [self.buffer_range[0]+1, self.buffer_range[1]+1]
                    else:
                        self.buffer.append(frame)
                        self.buffer_range[1] += 1
                    
                    print("Cached, range: %d-%d"%(self.buffer_range[0], self.buffer_range[1]))   
                    
            time.sleep(0.01)

    def _get_frame_from_buffer(self, nframe):
        with self.buffer_lock:
            if self.buffer_range[0] <= nframe < self.buffer_range[1]:
                return self.buffer[nframe - self.buffer_range[0]]
        return None
            
    def move_next(self):
        if self.cur_frame + 1 >= self.total_frames:
            return None
        self.cur_frame += 1
        frame = self._get_frame_from_buffer(self.cur_frame)
        if frame is not None:
            return frame
        
        with self.buffer_lock:
            ret, frame = self.cap.read()
            if not ret:
                return None
            self.buffer.append(frame)
            self.buffer_range[1] = self.cur_frame
            
        return frame
        
    def move_prev(self):
        if self.cur_frame - 1 < 0:
            return None
        self.cur_frame -= 1

        # Try to get from buffer
        frame = self._get_frame_from_buffer(self.cur_frame)
        if frame is not None:
            return frame
        
        # manually read frame
        with self.buffer_lock:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame)
            ret, frame = self.cap.read()
            if not ret:
                return None
            self.buffer.appendleft(frame)
            self.buffer_range[0] = self.cur_frame
            
            if self.buffer_range[1] - self.buffer_range[0] > IMAGE_BUFFER_SIZE:
                self.buffer.pop()
                self.buffer_range[1] -= 1
                
        return frame
        
    def move_specific_frame(self, nframe):
        if not (0 <= nframe < self.total_frames):
            return None
        self.cur_frame = nframe
        
        # reset
        with self.buffer_lock:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, nframe)
            ret, frame = self.cap.read()
            if not ret:
                return None

            self.buffer.clear()
            self.buffer_range = [nframe, nframe + 1]
            self.buffer.append(frame)
            
        return frame
            
    def close(self):
        self.read_thread_active = False
        self.read_thread.join()
        self.cap.release()
        
        

class VideoReader:
    def __init__(self, file_path):
        self.cur_frame = 0
        self._init_video(file_path)
        
    def _init_video(self, file_path):
        self.file_path = file_path
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Could not open video file: {file_path}")
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self._reset_buffer()
        
    def _reset_buffer(self):
        self.frame_buffer = []
        self.num_buffer = 0
        self.buffer_range = [self.cur_frame, self.cur_frame]
        
    def _cache_buffer(self, frame):
        if self.num_buffer == IMAGE_BUFFER_SIZE:
            self._reset_buffer()
        
        self.frame_buffer.append(frame)
        self.num_buffer += 1
        self.buffer_range[1] += 1
        
    def move_next(self):
        self._validate_frame(self.cur_frame+1)
        self.cur_frame += 1
        if self.buffer_range[0] <= self.cur_frame < self.buffer_range[1]:
            frame = self._read_frame_from_buffer(self.cur_frame)
        else:
            frame = self._read_frame()
        return frame
    
    def move_prev(self):
        self._validate_frame(self.cur_frame-1)
        self.cur_frame -= 1
        if self.buffer_range[0] <= self.cur_frame < self.buffer_range[1]:
            frame = self._read_frame_from_buffer(self.cur_frame)
        else:
            frame = self.move_specific_frame(self.cur_frame)
        # self.cur_frame -= 1
        return frame
    
    def move_specific_frame(self, nframe):
        self._validate_frame(nframe)
        
        self._reset_buffer()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, nframe)
        self.cur_frame = nframe
        return self._read_frame()
    
    @convert_frame
    def _read_frame_from_buffer(self, nframe):
        frame = self.frame_buffer[nframe - self.buffer_range[0]]
        return frame
    
    @convert_frame
    def _read_frame(self):
        success, frame = self.cap.read()
        if not success:
            raise RuntimeError("Failed to read frame from video.")
        self._cache_buffer(frame)
        return frame
    
    def close(self):
        self.cap.release()
        self._reset_buffer()
    
    def _validate_frame(self, nframe):
        if nframe < 0 or nframe >= self.total_frames:
            raise ValueError(f"Frame number {nframe} is out of bounds.")
        

