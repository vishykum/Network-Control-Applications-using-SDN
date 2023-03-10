from difflib import Match
import json

import networkx as nx

from app import NetworkApp
from rule import MatchPattern
from te_objs import PassByPathObjective, MinLatencyObjective, MaxBandwidthObjective
from utils_json import DefaultEncoder

class TEApp(NetworkApp):
    def __init__(self, topo_file, json_file, of_controller=None, priority=2):
        super(TEApp, self).__init__(topo_file, json_file, of_controller, priority)
        self.pass_by_paths_obj = [] # a list of PassByPathObjective objects 
        self.min_latency_obj = [] # a list of MinLatencyObjective objects
        self.max_bandwidth_obj = [] # a list of MaxBandwidthObjective objects
    
    def add_pass_by_path_obj(self, pass_by_obj):
        self.pass_by_paths_obj.append(pass_by_obj)

    def add_min_latency_obj(self, min_lat_obj):
        self.min_latency_obj.append(min_lat_obj)

    def add_max_bandwidth_obj(self, max_bw_obj):
        self.max_bandwidth_obj.append(max_bw_obj)

    # This function reads the TE objectives in the `self.json_file`
    # Then, parses the JSON objects to the three list:
    #       self.pass_by_paths_obj
    #       self.min_latency_obj
    #       self.max_bandwidth_obj
    def from_json(self):
        with open('%s'% self.json_file) as f:
            # TODO: complete
            rules = json.load(f)
            for rule in rules['pass_by_paths']:
                pattern = MatchPattern()

                #Populate Match Pattern
                if not(rule["match_pattern"]['src_ip'] == None):
                    pattern.src_ip = rule["match_pattern"]['src_ip']

                if not(rule["match_pattern"]["src_mac"] == None):
                    pattern.src_mac = rule["match_pattern"]['src_mac']
                
                if not(rule["match_pattern"]['dst_ip'] == None):
                    pattern.dst_ip = rule["match_pattern"]['dst_ip']
                
                if not(rule["match_pattern"]['dst_mac'] == None):
                    pattern.dst_mac = rule["match_pattern"]['dst_mac']

                if not(rule["match_pattern"]['mac_proto'] == None):
                    pattern.mac_proto = rule["match_pattern"]['mac_proto']

                if not(rule["match_pattern"]['ip_proto'] == None):
                    pattern.ip_proto = rule["match_pattern"]['ip_proto']
                
                if not(rule["match_pattern"]['src_port'] == None):
                    pattern.src_port = rule["match_pattern"]['src_port']

                if not(rule["match_pattern"]['dst_port'] == None):
                    pattern.dst_port = rule["match_pattern"]['dst_port']

                if not(rule["match_pattern"]['in_port'] == None):
                    pattern.in_port = rule["match_pattern"]['in_port']

                switches = []
                for switch in rule["switches"]:
                    switches.append(int(switch))

                symmetric = rule["symmetric"]
                
                obj = PassByPathObjective(pattern, switches, symmetric)
                self.add_pass_by_path_obj(obj)

            for rule in rules['min_latency']:
                pattern = MatchPattern()

                #Populate Match Pattern
                if not(rule["match_pattern"]['src_ip'] == None):
                    pattern.src_ip = rule["match_pattern"]['src_ip']

                if not(rule["match_pattern"]["src_mac"] == None):
                    pattern.src_mac = rule["match_pattern"]['src_mac']
                
                if not(rule["match_pattern"]['dst_ip'] == None):
                    pattern.dst_ip = rule["match_pattern"]['dst_ip']
                
                if not(rule["match_pattern"]['dst_mac'] == None):
                    pattern.dst_mac = rule["match_pattern"]['dst_mac']

                if not(rule["match_pattern"]['mac_proto'] == None):
                    pattern.mac_proto = rule["match_pattern"]['mac_proto']

                if not(rule["match_pattern"]['ip_proto'] == None):
                    pattern.ip_proto = rule["match_pattern"]['ip_proto']
                
                if not(rule["match_pattern"]['src_port'] == None):
                    pattern.src_port = rule["match_pattern"]['src_port']

                if not(rule["match_pattern"]['dst_port'] == None):
                    pattern.dst_port = rule["match_pattern"]['dst_port']

                if not(rule["match_pattern"]['in_port'] == None):
                    pattern.in_port = rule["match_pattern"]['in_port']

                
                src_switch = rule["src_switch"]
                dst_switch = rule["dst_switch"]

                symmetric = rule["symmetric"]

                obj = MinLatencyObjective(pattern, src_switch, dst_switch, symmetric)
                self.add_min_latency_obj(obj)

            

    
    # Translates the TE objectives to the `json_file`
    def to_json(self, json_file):
        json_dict = {
            'pass_by_paths': self.pass_by_paths_obj,
            'min_latency': self.min_latency_obj,
            'max_bandwidth': self.max_bandwidth_obj,
        }

        with open('%s'% json_file, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, ensure_ascii=False, indent=4, cls=DefaultEncoder)

    # This function translates the objectives in `self.pass_by_paths_obj` to a list of Rules in `self.rules`
    # It should: 
    #   call `self.calculate_rules_for_path` as needed
    #   handle traffic in reverse direction when `symmetric` is True 
    #   call `self.send_openflow_rules()` at the end
    def provision_pass_by_paths(self):
        self.rules = []

        for obj in self.pass_by_paths_obj:

            switches = obj.switches

            for i in range(0,len(switches)):
                switches[i] = str(switches[i])

            pattern = obj.match_pattern

            rules = self.calculate_rules_for_path(switches, pattern, include_in_port=False)
            for rule in rules:
                self.add_rule(rule)
            
            if obj.symmetric:
                switches.reverse()

                src__ip = pattern.dst_ip
                dst_ip = pattern.src_ip
                src_port = pattern.dst_port
                dst_port = pattern.src_port

                pattern.src_ip = src__ip
                pattern.dst_ip = dst_ip
                pattern.src_port = src_port
                pattern.dst_port = dst_port

                rules = self.calculate_rules_for_path(switches, pattern, include_in_port=False)

                for rule in rules:
                    self.add_rule(rule)

        self.send_openflow_rules()

    # This function translates the objectives in `self.min_latency_obj` to a list of Rules in `self.rules`
    # It should: 
    #   call `self.calculate_rules_for_path` as needed
    #   consider using the function `networkx.shortest_path` in the networkx package
    #   handle traffic in reverse direction when `symmetric` is True 
    #   call `self.send_openflow_rules()` at the end
    def provision_min_latency_paths(self):
        self.rules = []

        for obj in self.min_latency_obj:
            src_switch = str(obj.src_switch)
            dst_switch = str(obj.dst_switch)

            # switches = [src_switch, dst_switch]

            path = nx.shortest_path(self.topo, source=src_switch, target=dst_switch, weight='delay')
            
            rules = self.calculate_rules_for_path(path, obj.match_pattern)
            for rule in rules:
                self.rules.append(rule)

            if obj.symmetric:
                path = nx.shortest_path(self.topo, source=dst_switch, target=src_switch, weight='delay')
                sym_rules = self.calculate_rules_for_path(path, obj.match_pattern)

                for rule in sym_rules:
                    self.rules.append(rule)

        for rule in self.rules:
            print(rule)

        self.send_openflow_rules()

            
        


    # BONUS: 
    # This function translates the objectives in `self.max_bandwidth_obj` to a list of Rules in `self.rules`
    # It should: 
    #   call `self.calculate_rules_for_path` as needed
    #   consider what algorithms to use (from networkx) to calculate the paths
    #   handle traffic in reverse direction when `symmetric` is True 
    #   call `self.send_openflow_rules()` at the end
    def provision_max_bandwidth_paths(self):
        pass
    
    # BONUS: Used to react to changes in the network (the controller notifies the App)
    def on_notified(self, **kwargs):
        pass