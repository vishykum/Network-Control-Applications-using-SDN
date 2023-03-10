import json

from app import NetworkApp
from rule import Action, ActionType, Rule, MatchPattern
from utils_json import DefaultEncoder

def parse_action(d):
    if 'action_type' in d:
        return {
            'action_type': getattr(ActionType, d['action_type']),
            'out_port': d.get('out_port', None)
            }
    return d


class FirewallApp(NetworkApp):
    def __init__(self, json_file, of_controller=None, priority=3):
        super(FirewallApp, self).__init__(None, json_file, of_controller, priority)
        # self.rules = []
    # Translates the firewall policy file in `self.json_file` to a list of Rule objects `self.rules`
    def from_json(self):
        with open('%s'% self.json_file) as f:
            rules = json.load(f, object_hook=parse_action)
            # TODO: complete
            for rule in rules:
                switch_id = int(rule["switch_id"])
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

                action = Action(rule["action"]["action_type"], rule["action"]["out_port"])

                snd_rule = Rule(switch_id=switch_id, match_pattern=pattern, action=action)
                self.add_rule(snd_rule)
                

    # Writes the firewall policy to a JSON file
    def to_json(self, json_file):
        with open('%s'% json_file, 'w', encoding='utf-8') as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=4, cls=DefaultEncoder)

    # This function calls `send_openflow_rules` only.
    # This is because the policy is the actual OpenFlow rules to be sent.
    def calculate_firewall_rules(self):
        self.send_openflow_rules()

    # BONUS: Used to react to changes in the network (the controller notifies the App)
    def on_notified(self, **kwargs):
        pass