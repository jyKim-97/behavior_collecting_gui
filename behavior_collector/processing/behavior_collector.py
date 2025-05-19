# export with json format
import os
import json
from typing import List, Dict
from dataclasses import dataclass, asdict
from collections import OrderedDict

BEHAV_TYPE = ("State", "Event")


@dataclass
class BehavInfo:
    video_path: str
    max_frames: int
    behav_info: Dict = None
    behav_frames: Dict = None
    
    def add_behavior(self, behav_name: str,
                     behav_type: str, behav_note: str, behav_color: str):
        
        if behav_name in self.behav_info.keys():
            raise ValueError("Behavior already exists")
        
        self.behav_info[behav_name] = {
            "behavior_type": behav_type,
            "behavior_note": behav_note,
            "behavior_color": behav_color
        }
        self.behav_frames[behav_name] = []
    
    def add_frame(self, behav_name: str, start_frame: int, end_frame: int=None):
        print("Behavior added:", behav_name, start_frame, end_frame)
        self._check_behav(behav_name)
        if end_frame is None:
            frame_range = [start_frame]
        else:
            frame_range = [start_frame, end_frame]
        self.behav_frames[behav_name].append(frame_range)
    
    def remove_frame(self, behav_name: str, start_frame: int=-1, frame_id: int=-1):
        self._check_behav(behav_name)
        if start_frame == -1 and frame_id == -1:
            raise ValueError("Either start_frame or frame_id must be provided")
    
    @staticmethod
    def load(file_path: str):
        with open(file_path, "r") as fp:
            json_data = json.load(fp)
        return BehavInfo(**json_data) 
    
    def save(self, file_path: str):
        with open(file_path, "w") as fp:
            json.dump(asdict(self), fp, indent=4)
    
    def _check_behav(self, behav_name: str):
        if behav_name not in self.behav_info.keys():
            raise ValueError("Behavior does not exist")
        


# class BehaviorCollector:
#     def __init__(self, video_path, max_frames):
#         self.behav_set = BehavInfo(video_path, max_frames)
        
#     def create_behavior(self, behav_name, behav_type, behav_color, behav_note):
#         if behav_name in self.collected_behavs.keys():
#             raise ValueError("Behavior already exists")
        
#         self.behav_set.behav_info[behav_name] = {
#             "behavior_type": behav_type,
#             "behavior_note": behav_note,
#             "behavior_color": behav_color
#         }
#         self.behav_set.behav_frames[behav_name] = []
        
#     def add_behavior_frame(self, behav_name, start_frame, end_frame=None):
#         if behav_name not in self.collected_behavs.keys():
#             raise ValueError("Behavior does not exist")
        
#         if start_frame > end_frame:
#             raise ValueError("Start frame must be less than end frame")
        
#         if self.collected_behavs[behav_name]["info"]["behavior_type"] != BEHAV_TYPE[0]: # EVENT
#             if end_frame is None:
#                 raise ValueError("End frame must be provided for event type behavior")
#             self.collected_behavs[behav_name]["frames"].append((start_frame, end_frame))
#         else:
#             self.collected_behavs[behav_name]["frames"].append([start_frame])
    
#     def load_behavior(self, file_path):
#         if os.path.exists(file_path):
#             raise ValueError("File does not exist")
        
#         with open(file_path, "r") as fp:
#             json_data = json.load(fp)
#             if not isinstance(json_data, dict):
#                 raise ValueError("Invalid file format")
#             for k in json_data.keys():
#                 if "info" not in k or "frames" not in k:
#                     raise ValueError("Invalid file format")
#         self.collected_behavs = json_data            

#     def save_behavior(self, file_path):
#         with open(file_path, "w") as fp:
#             json.dump(self.collected_behavs, fp, indent=4)
            